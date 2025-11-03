import pandas as pd

from utils.misc import check_df_format


def add_col_ib_high_low(
    df: pd.DataFrame, initial_balance_minutes: int = 30
) -> pd.DataFrame:
    """
    If DataFrame is OK, adds columns Initial Balance High (ib_high)
    and Initial Balance Low (ib_low) for each day,
    and returns the updated DataFrame.

    Returns:
        A pandas DataFrame with 'ib_high' and 'ib_low' columns added.
    """

    if initial_balance_minutes not in [15, 30, 45, 60]:
        raise ValueError(
            "add_col_ib_high_low: Initial balance must be 15, 30, 45, or 60 minutes."
        )

    check_df_res = check_df_format(df=df)
    if check_df_res["is_datetime_index"] is False:
        raise ValueError(
            f"add_col_ib_high_low: input DF doesn't have DateTime index, {check_df_res}"
        )
    if check_df_res["inferred_interval_minutes"] not in [5, 15, 30, 45, 60]:
        inferred_interval_min = check_df_res["inferred_interval_minutes"]
        raise ValueError(
            f"add_col_ib_high_low: input DF bars interval = {inferred_interval_min} min, should be 5, 15, 30, 45, 60 minutes"
        )

    # Calculate the number of 15-minute bars to use for the Initial Balance
    num_bars = initial_balance_minutes // check_df_res["inferred_interval_minutes"]
    if num_bars < 1:
        raise ValueError(
            f"add_col_ib_high_low: DF bars interval is {check_df_res['inferred_interval_minutes']} min, initial balance should be not less"
        )

    # 2. Create and populate "Initial balance low" (ib_low) and "Initial balance high" (ib_high)

    # Calculate the bar number within each day (0-indexed)
    bar_number_in_day = df.groupby(df.index.date).cumcount()  # type: ignore

    # Filter for the bars that belong to the Initial Balance period
    ib_bars = df[bar_number_in_day < num_bars]

    # Calculate the max High (ib_high) and min Low (ib_low) for the IB period of each day
    daily_ib = ib_bars.groupby(ib_bars.index.date)[["High", "Low"]].agg(
        ib_high=("High", "max"), ib_low=("Low", "min")
    )

    # Merge the daily IB values back into the original DataFrame,
    # mapping them to all rows of the corresponding day.
    df["Datetime"] = df.index
    df = df.reset_index(drop=True)
    # df["Date"] = df["Datetime"].dt.date
    df["Date"] = pd.to_datetime(df["Datetime"])
    df["Date"] = df["Date"].dt.date
    df = df.merge(daily_ib, left_on="Date", right_index=True, how="left")
    df = df.drop(columns=["Date"]).set_index("Datetime")

    # 3. Return the dataframe
    return df


def check_initial_balance_breach(
    df: pd.DataFrame, initial_balance_minutes: int = 30
) -> pd.DataFrame:
    """
    Checks for the first Initial Balance Low Breakdown (ib_low_bd) and High Breakout (ib_high_bt)
    after the initial balance period for each day. Uss the Close price for the breach check.

    Args:
        df: A Pandas DataFrame with 'ib_low' and 'ib_high' columns.
        initial_balance_minutes: The duration of the initial balance period
                                 in minutes (15, 30, 45, or 60).

    Returns:
        The modified DataFrame with 'ib_low_bd' and 'ib_high_bt' Boolean columns.
    """

    # 1. Check input validity
    if initial_balance_minutes not in [15, 30, 45, 60]:
        raise ValueError(
            "check_initial_balance_breach: Initial balance must be 15, 30, 45, or 60 minutes."
        )

    check_df_res = check_df_format(df=df)
    if check_df_res["is_datetime_index"] is False:
        raise ValueError(
            f"check_initial_balance_breach: input DF doesn't have DateTime index, {check_df_res}"
        )
    if check_df_res["inferred_interval_minutes"] not in [5, 15, 30, 45, 60]:
        inferred_interval_min = check_df_res["inferred_interval_minutes"]
        raise ValueError(
            f"check_initial_balance_breach: input DF bars interval = {inferred_interval_min} min, should be 5, 15, 30, 45, 60 minutes"
        )

    # 2. Create new Boolean columns
    df["ib_low_bd"] = False
    df["ib_high_bt"] = False

    # Calculate number of bars in the initial balance period
    num_bars = initial_balance_minutes // check_df_res["inferred_interval_minutes"]
    bar_number_in_day = df.groupby(df.index.date).cumcount()  # type: ignore
    post_ib_mask = bar_number_in_day >= num_bars

    # 3. Determine breakdown and breakout using 'Close' price

    breakdown_candidates = (df["Close"] < df["ib_low"]) & post_ib_mask

    first_breakdown_indices = (
        breakdown_candidates[breakdown_candidates]
        .groupby(breakdown_candidates[breakdown_candidates].index.date)
        .idxmin()
    )
    df.loc[first_breakdown_indices, "ib_low_bd"] = True

    breakout_candidates = (df["Close"] > df["ib_high"]) & post_ib_mask

    first_breakout_indices = (
        breakout_candidates[breakout_candidates]
        .groupby(breakout_candidates[breakout_candidates].index.date)
        .idxmin()
    )
    df.loc[first_breakout_indices, "ib_high_bt"] = True

    # 4. Return the modified dataframe
    return df


def calculate_ib_breakout_and_breakdown_metrics(
    df: pd.DataFrame,
) -> tuple[list[dict], list[dict]]:
    """
    Calculates metrics for Initial Balance Low Breakdown (ib_low_bd) and
    Initial Balance High Breakout (ib_high_bt) events.

    The ultimate goal is to determine whether it is worth
    taking a short trade after Initial Balance Low Breakdown has happened,
    as well as a long trade after Initial Balance High Breakout has happened.

    :param df: A Pandas DataFrame with a DatetimeIndex and columns
               'Open', 'High', 'Low', 'ib_low_bd', and 'ib_high_bt'.
    :return: A tuple containing two lists of dictionaries.
    """

    # 1. Checks that the dataframe has ib_low_bd and ib_high_bt columns.
    required_cols = ["Open", "High", "Low", "ib_low_bd", "ib_high_bt"]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(
            f"DataFrame must contain all required columns: {required_cols}"
        )

    # 2. Checks that the dataframe has a DateTime index.
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame must have a DatetimeIndex.")

    # 3. Creates empty lists (now containing dictionaries)
    ib_low_bd_vals = []
    ib_high_bt_vals = []

    # 4. Iterates the dataframe over days.
    for _, day_df in df.groupby(df.index.date):

        has_bd = day_df["ib_low_bd"].any()
        has_bt = day_df["ib_high_bt"].any()

        # Skip if no event
        if not (has_bd or has_bt):
            continue

        # --- Procedure for a day that has ib_low_bd True value ---
        if has_bd:
            breakdown_times = day_df[day_df["ib_low_bd"]].index

            for bd_time in breakdown_times:
                current_idx_loc = df.index.get_loc(bd_time)

                # 1. Find the value of the Open column in the next bar
                next_idx_loc = current_idx_loc + 1
                if next_idx_loc >= len(df):
                    continue

                next_open = df.iloc[next_idx_loc]["Open"]

                # 2. Find the minimum value of the Low column after event
                bars_after_bd = day_df.loc[day_df.index > bd_time]

                if bars_after_bd.empty:
                    continue

                lowest_low_after_breakdown = bars_after_bd["Low"].min()

                # 3. Calculate the value
                if next_open != 0:
                    bd_metric = (next_open - lowest_low_after_breakdown) / next_open

                    # 4. Append dictionary: {'Date': today's day date, 'Val': value}
                    ib_low_bd_vals.append(
                        {
                            "Date": bd_time.date(),
                            "Val": bd_metric,
                            "next_open": next_open,
                            "lowest_low_after": lowest_low_after_breakdown,
                        }
                    )

        # --- Procedure for a day that has ib_high_bt True value ---
        if has_bt:
            breakout_times = day_df[day_df["ib_high_bt"]].index

            for bt_time in breakout_times:
                current_idx_loc = df.index.get_loc(bt_time)

                # 1. Find the value of the Open column in the next bar
                next_idx_loc = current_idx_loc + 1
                if next_idx_loc >= len(df):
                    continue

                next_open = df.iloc[next_idx_loc]["Open"]

                # 2. Find the maximum value of the High column after event
                bars_after_bt = day_df.loc[day_df.index > bt_time]

                if bars_after_bt.empty:
                    continue

                highest_high_after_breakout = bars_after_bt["High"].max()

                # 3. Calculate the value
                if next_open != 0:
                    bt_metric = (highest_high_after_breakout - next_open) / next_open

                    # 4. Append dictionary: {'Date': today's day date, 'Val': value}
                    ib_high_bt_vals.append({"Date": bt_time.date(), "Val": bt_metric})

    # 5. Returns lists of dictionaries.
    return ib_low_bd_vals, ib_high_bt_vals
