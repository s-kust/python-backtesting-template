import pandas as pd


def add_moving_average(df: pd.DataFrame, n: int = 200):

    # NOTE Extend this function according to your needs:
    # exponential MA, use typical price instead of close price etc.

    df_internal = df.copy()
    df_internal[f"ma_{n}"] = df_internal["Close"].rolling(n).mean()
    return df_internal
