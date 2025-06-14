from typing import Tuple

import pandas as pd

from constants import ATR_MULTIPLIER, ATR_SMOOTHING_N

from .atr import add_atr_col_to_df


def _get_fill_is_min_max_start_data(df: pd.DataFrame) -> Tuple[pd.Timestamp, str]:
    """
    For fill_is_min_max, get start date and first extremum_to_detect (min or max).
    Start date is the next day after the recently found local min or max.
    """
    all_minimums = df[df["is_min"] == True]  # pylint: disable=C0121
    all_maximums = df[df["is_max"] == True]  # pylint: disable=C0121

    latest_min_index = None
    if not all_minimums.empty:
        latest_min_index = all_minimums.index.max()
    latest_max_index = None
    if not all_maximums.empty:
        latest_max_index = all_maximums.index.max()

    if latest_min_index is None and latest_max_index is None:
        start_date = df.index.min()
        extremum_to_detect = "min"  # arbitrary choice
        return start_date, extremum_to_detect

    if latest_min_index is None:  # here latest_max_index is not None:
        extremum_to_detect = "min"
        start_date = df[df.index > latest_max_index].index.min()
        return start_date, extremum_to_detect

    if latest_max_index is None:  # here latest_min_index is not None:
        extremum_to_detect = "max"
        start_date = df[df.index > latest_min_index].index.min()
        return start_date, extremum_to_detect

    # here both latest_min_index and latest_max_index are not None:
    if latest_max_index > latest_min_index:  # type: ignore
        extremum_to_detect = "min"
        start_date = df[df.index > latest_max_index].index.min()
    else:
        extremum_to_detect = "max"
        start_date = df[df.index > latest_min_index].index.min()

    return start_date, extremum_to_detect


def _ensure_required_cols_min_max_in_df(
    df: pd.DataFrame, atr_smoothing_n: int = ATR_SMOOTHING_N
) -> pd.DataFrame:
    internal_df = df.copy()

    # Ensure ATR column exists
    if f"atr_{atr_smoothing_n}" not in internal_df.columns:
        internal_df = add_atr_col_to_df(
            df=internal_df, n=atr_smoothing_n, exponential=False
        )

    # Columns and their default values
    required_cols_defaults = {
        "is_min": False,
        "is_max": False,
        "last_known_min_date": None,
        "last_known_max_date": None,
        "prev_known_min_date": None,
        "prev_known_max_date": None,
        "last_known_min_val": None,
        "last_known_max_val": None,
        "prev_known_min_val": None,
        "prev_known_max_val": None,
    }

    # Add missing columns with their default values
    for col, default_val in required_cols_defaults.items():
        if col not in internal_df.columns:
            internal_df[col] = default_val

    return internal_df


def _fill_is_min_max(
    df: pd.DataFrame,
    col_name: str = "Close",
    atr_multiplier: float = ATR_MULTIPLIER,
    atr_smoothing_n: int = ATR_SMOOTHING_N,
) -> pd.DataFrame:
    """
    Fill the Boolean columns is_min and is_max in the DataFrame.
    They are already guaranteed to exist.

    A new maximum is considered to be found
    when the price has moved downwards from it
    by a distance of at least ATR * ATR_MULTIPLIER.

    A new minimum is considered to be found
    when the price has moved upwards from it
    by a distance of at least ATR * ATR_MULTIPLIER.
    """
    if df.empty:
        return df
    internal_df = df.copy()
    start_date, extremum_to_detect = _get_fill_is_min_max_start_data(df=internal_df)
    current_candidate = {
        "extremum_to_detect": extremum_to_detect,
        "date": start_date,
        "ts_data_val": internal_df[internal_df.index == start_date][col_name].values[0],
    }
    for i, row in (
        internal_df[internal_df.index >= current_candidate["date"]]
        .sort_index()
        .iterrows()
    ):
        if current_candidate["extremum_to_detect"] == "max":
            if row[col_name] >= current_candidate["ts_data_val"]:
                current_candidate["ts_data_val"] = row[col_name]
                current_candidate["date"] = i
            elif (current_candidate["ts_data_val"] - row[col_name]) > (
                row[f"atr_{atr_smoothing_n}"] * atr_multiplier
            ):
                internal_df.loc[
                    internal_df.index == current_candidate["date"], "is_max"
                ] = True
                current_candidate["extremum_to_detect"] = "min"
                current_candidate["date"] = i
                current_candidate["ts_data_val"] = row[col_name]

        else:  # looking for min, current_candidate['extremum_to_detect'] == 'min'
            if row[col_name] <= current_candidate["ts_data_val"]:
                current_candidate["ts_data_val"] = row[col_name]
                current_candidate["date"] = i
            elif (row[col_name] - current_candidate["ts_data_val"]) > (
                row[f"atr_{atr_smoothing_n}"] * atr_multiplier
            ):
                internal_df.loc[
                    internal_df.index == current_candidate["date"], "is_min"
                ] = True
                current_candidate["extremum_to_detect"] = "max"
                current_candidate["date"] = i
                current_candidate["ts_data_val"] = row[col_name]
    return internal_df


def _fill_min_max_date_val_columns(
    df: pd.DataFrame, col_name: str = "Close"
) -> pd.DataFrame:
    """
    In DataFrame, fill columns last_known_max_date, last_known_max_val etc.
    """
    internal_df = df.copy()
    condition_is_min = internal_df["is_min"] == True  # pylint: disable=C0121
    condition_is_max = internal_df["is_max"] == True  # pylint: disable=C0121

    for i, _ in internal_df.sort_index().iterrows():

        condition_index = internal_df.index < i
        index_mins = internal_df[condition_index & condition_is_min].index
        index_maxes = internal_df[condition_index & condition_is_max].index

        try:
            last_known_max_date = index_maxes[-1]
        except IndexError:
            last_known_max_date = None

        try:
            prev_known_max_date = index_maxes[-2]
        except IndexError:
            prev_known_max_date = None

        try:
            last_known_min_date = index_mins[-1]
        except IndexError:
            last_known_min_date = None

        try:
            prev_known_min_date = index_mins[-2]
        except IndexError:
            prev_known_min_date = None

        # fill columns
        if last_known_max_date is not None:
            internal_df.loc[internal_df.index == i, "last_known_max_date"] = (
                last_known_max_date
            )
            val = internal_df.loc[last_known_max_date, col_name]
            internal_df.loc[internal_df.index == i, "last_known_max_val"] = val

        if last_known_min_date is not None:
            internal_df.loc[internal_df.index == i, "last_known_min_date"] = (
                last_known_min_date
            )
            val = internal_df.loc[last_known_min_date, col_name]
            internal_df.loc[internal_df.index == i, "last_known_min_val"] = val

        if prev_known_max_date is not None:
            internal_df.loc[internal_df.index == i, "prev_known_max_date"] = (
                prev_known_max_date
            )
            val = internal_df.loc[prev_known_max_date, col_name]
            internal_df.loc[internal_df.index == i, "prev_known_max_val"] = val

        if prev_known_min_date is not None:
            internal_df.loc[internal_df.index == i, "prev_known_min_date"] = (
                prev_known_min_date
            )
            val = internal_df.loc[prev_known_min_date, col_name]
            internal_df.loc[internal_df.index == i, "prev_known_min_val"] = val
    return internal_df


def add_is_min_max_dates_values(
    df: pd.DataFrame,
    col_name: str = "Close",
    atr_multiplier: float = ATR_MULTIPLIER,
    atr_smoothing_n: int = ATR_SMOOTHING_N,
) -> pd.DataFrame:
    """
    Find significant minimums and maximums of the series col_name,
    put the True values in the corresponding rows of is_min and is_max columns.

    Also, fill the following columns:
    last_known_max_date, last_known_min_date,
    prev_known_max_date, prev_known_min_date,
    last_known_max_val, last_known_min_val,
    prev_known_max_val, prev_known_min_val,
    """

    # NOTE The last_known_max_date, last_known_min_date, prev_known_max_date, prev_known_min_date
    # columns are needed to avoid the look ahead bias when designing features.

    internal_df = df.copy()
    internal_df = _ensure_required_cols_min_max_in_df(
        df=internal_df, atr_smoothing_n=atr_smoothing_n
    )

    internal_df = _fill_is_min_max(
        df=internal_df,
        col_name=col_name,
        atr_multiplier=atr_multiplier,
        atr_smoothing_n=atr_smoothing_n,
    )
    internal_df = _fill_min_max_date_val_columns(df=internal_df, col_name=col_name)
    return internal_df
