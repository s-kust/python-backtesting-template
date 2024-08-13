import numpy as np
import pandas as pd


def check_shooting_star_candle(
    yesterday_high: float,
    yesterday_low: float,
    yesterday_close: float,
    today_high: float,
    today_low: float,
    today_open: float,
    today_close: float,
) -> bool:
    if (
        np.isnan(yesterday_high)
        or np.isnan(yesterday_low)
        or np.isnan(yesterday_close)
        or np.isnan(today_high)
        or np.isnan(today_low)
        or np.isnan(today_open)
        or np.isnan(today_close)
    ):
        return False
    if today_close > yesterday_close:
        return False
    if today_close > today_open:
        return False
    yesterday_high_low = yesterday_high - yesterday_low
    if today_high < (yesterday_high + (yesterday_high_low * 0.07)):
        return False
    today_high_low = today_high - today_low
    if (today_high - today_open) < (today_high_low * 0.75):
        return False

    # today close near low
    if (today_close - today_low) > (today_high_low * 0.15):
        return False

    # today close not too low to have potential to go lower in subsequent days
    if (yesterday_close - today_close) > (yesterday_high_low * 0.2):
        return False

    return True


def add_feature_is_shooting_star(df: pd.DataFrame) -> pd.DataFrame:
    res = df.copy()
    res["yd_high"] = res["High"].shift(1)
    res["yd_low"] = res["Low"].shift(1)
    res["yd_close"] = res["Close"].shift(1)
    res["is_shooting_star"] = res.apply(
        lambda row: check_shooting_star_candle(
            yesterday_high=row["yd_high"],
            yesterday_low=row["yd_low"],
            yesterday_close=row["yd_close"],
            today_high=row["High"],
            today_low=row["Low"],
            today_open=row["Open"],
            today_close=row["Close"],
        ),
        axis=1,
    )
    del res["yd_high"]
    del res["yd_low"]
    del res["yd_close"]
    return res
