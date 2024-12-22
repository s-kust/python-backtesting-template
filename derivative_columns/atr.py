import pandas as pd

from utils.misc import ensure_df_has_all_required_columns


def add_atr_col_to_df(
    df: pd.DataFrame, n: int = 5, exponential: bool = False
) -> pd.DataFrame:
    """
    Add ATR (Average True Range) column to DataFrame.
    Average True Range is a volatility estimate.
    n - number of periods.
    If exponential is true,
    use ewm - exponentially weighted values,
    to give more weight to the recent data point.
    Otherwise, calculate simple moving average.
    """

    ensure_df_has_all_required_columns(df=df, volume_col_required=False)
    data = df.copy(deep=True)
    high = data["High"]
    low = data["Low"]
    close = data["Close"]
    data["tr0"] = abs(high - low)
    data["tr1"] = abs(high - close.shift())
    data["tr2"] = abs(low - close.shift())
    data["tr"] = data[["tr0", "tr1", "tr2"]].max(axis=1)

    # today we know yesterday's TR only, not today's TR
    data["tr"] = data["tr"].shift()

    if exponential:
        data[f"atr_{n}"] = (
            data["tr"].ewm(alpha=2 / (n + 1), min_periods=n, adjust=False).mean()
        )
    else:
        data[f"atr_{n}"] = data["tr"].rolling(window=n, min_periods=n).mean()

    del data["tr0"]
    del data["tr1"]
    del data["tr2"]
    # del data["tr"]
    return data


def add_tr_delta_col_to_ohlc(ohlc_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add tr_delta column to OHLC data
    """

    # NOTE 1. This function IS MANDATORY to call,
    # because tr_delta is used in update_stop_losses()

    # NOTE 2. tr_delta is a volatility spike indicator.
    # It can be used when building features and forecasts.

    res = ohlc_df.copy()
    rolling_period_tr = 100
    small_atr_period_for_delta = 3
    res = add_atr_col_to_df(df=res, n=small_atr_period_for_delta)
    res["tr_avg"] = (
        res["tr"]
        .rolling(window=rolling_period_tr, min_periods=rolling_period_tr)
        .mean()
    )
    res["tr_delta"] = res[f"atr_{small_atr_period_for_delta}"] / res["tr_avg"]
    del res["tr_avg"]
    del res[f"atr_{small_atr_period_for_delta}"]
    return res
