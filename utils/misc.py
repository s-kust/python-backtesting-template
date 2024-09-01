from typing import Callable

import pandas as pd


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
    grouping_col_name: str,
    new_col_name: str,
    get_label_for_group: Callable,
) -> pd.DataFrame:
    """
    Input: DataFrame with some continuos feature in column grouping_col_name.
    For each feature value, its label is determined
    using the function get_label_for_group
    and saved in a new column new_col_name.
    """
    # NOTE get_label_for_group example - see function get_group_label_forecast_bb
    res = df.copy()
    res[new_col_name] = res[grouping_col_name].apply(get_label_for_group)
    return res
