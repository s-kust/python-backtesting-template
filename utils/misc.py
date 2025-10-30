import inspect
from typing import Callable

import pandas as pd


def ensure_df_has_all_required_columns(
    df: pd.DataFrame, volume_col_required: bool = False
) -> None:
    if volume_col_required:
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
    else:
        required_columns = ["Open", "High", "Low", "Close"]
    df_columns = df.columns
    for col_name in required_columns:
        if col_name not in df_columns:
            caller = inspect.stack()[1].function
            raise ValueError(
                f"OHLC DataFrame must contain columns: {required_columns}, absent column {col_name}, checked by {caller} function"
            )


def add_z_score_col_to_df(
    df: pd.DataFrame, col_name: str, window: int = 100
) -> pd.DataFrame:
    df_internal = df.copy(deep=True)
    col_mean = df[col_name].rolling(window=window, min_periods=window).mean()
    col_std = df[col_name].rolling(window=window, min_periods=window).std()
    df_internal[f"{col_name}_z_sc"] = (df[col_name] - col_mean) / col_std
    return df_internal


def add_feature_group_col_to_df(
    df: pd.DataFrame,
    continuous_feature_col_name: str,
    new_col_name: str,
    get_label_for_group: Callable,
) -> pd.DataFrame:
    """
    Break a continuous feature into discretionary groups
    in order to then conduct an analysis of these groups.
    Input: DataFrame with some feature in column continuous_feature_col_name.
    For each feature value, its label is determined
    using the group's custom function get_group_label_XXX
    and saved in a new column new_col_name.
    """

    # NOTE get_label_for_group example - see functions
    # get_group_label_forecast_bb and get_group_label_tr_delta

    res = df.copy()
    res[new_col_name] = res[continuous_feature_col_name].apply(get_label_for_group)
    return res


def get_forecast_bb(df: pd.DataFrame) -> pd.Series:
    return df["forecast_bb"]


def check_df_format(df: pd.DataFrame) -> dict:
    """
    Checks if a Pandas DataFrame has a DatetimeIndex
    and determines the bar interval in minutes.

    Args:
        df: The input Pandas DataFrame.

    Returns:
        A dictionary containing the results of the checks including the bar interval.
        The returned bar interval value 999 means the function failed to determine it
    """
    results = {}
    results["inferred_interval_minutes"] = 999

    # 1. Check if the index is a DatetimeIndex
    # is_datetime64_any_dtype checks for any datetime-like dtype
    is_dt_index = pd.api.types.is_datetime64_any_dtype(df.index)
    results["is_datetime_index"] = is_dt_index

    # 2. Check the bar interval (frequency)
    if is_dt_index and len(df) >= 2:
        # Calculate the difference between the first two timestamps
        inferred_diff_minutes = (df.index[1] - df.index[0]).total_seconds() / 60.0
        inferred_diff_minutes = int(inferred_diff_minutes)
        results["inferred_interval_minutes"] = inferred_diff_minutes

    return results
