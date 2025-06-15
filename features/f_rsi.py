import pandas as pd

from constants import FEATURE_COL_NAME_BASIC
from derivative_columns.rsi import add_rsi_column

HIGH_RSI_THRESHOLD = 90


def _add_required_cols_for_f_high_rsi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure that every necessary column for the feature high_RSI is present in the DataFrame
    """
    if "Close" not in df.columns:
        raise ValueError("feature_high_RSI: no Close column in input DataFrame")
    if "RSI_14" not in df.columns:
        internal_df = df.copy()
        internal_df = add_rsi_column(df=internal_df, col_name="Close")
        return internal_df
    return df


def add_feature_high_rsi(df: pd.DataFrame) -> pd.DataFrame:
    """
    First make sure that all necessary derived columns are present.
    After that, add high RSI feature column.
    """
    res = df.copy()
    res = _add_required_cols_for_f_high_rsi(df=res)
    res[FEATURE_COL_NAME_BASIC] = res["RSI_14"] > HIGH_RSI_THRESHOLD
    return res
