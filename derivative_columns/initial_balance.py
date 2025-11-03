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
