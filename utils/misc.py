import pandas as pd


def add_z_score_col_to_df(
    df: pd.DataFrame, col_name: str, window: int = 100
) -> pd.DataFrame:
    df_internal = df.copy(deep=True)
    col_mean = df[col_name].rolling(window=window, min_periods=window).mean()
    col_std = df[col_name].rolling(window=window, min_periods=window).std()
    df_internal[f"{col_name}_z_sc"] = (df[col_name] - col_mean) / col_std
    return df_internal
