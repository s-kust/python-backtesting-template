import pandas as pd

from features.shooting_star import check_shooting_star_candle
from forecast.forecast_bb import add_bb_forecast


def add_bb_forecast_to_ohlc(df: pd.DataFrame) -> pd.DataFrame:

    # NOTE. You can have multiple similar functions
    # with different sets of features and forecasts.
    # Call the function you want to use
    # inside the run_all_tickers function.

    res = df.copy()

    # NOTE better don't remove this line
    res = add_bb_forecast(df=res, col_name="Close")

    # res["feature_ys_negative_advanced"] = (
    #     (res["Close"] < res["avwap_min_min"])
    #     # & (res["Close"] < res["Close"].shift(1))
    #     & (res["Close"].shift(1) < res["avwap_min_min"].shift(1))
    #     & (res["Close"].shift(2) < res["avwap_min_min"].shift(2))
    #     & (abs(res["avwap_min_min"] - res["Close"]) < (res[f"atr_14"] * 0.8))
    #     & (res["fwd_ret_3"].shift(4) > 0)
    #     & (res["prev_close_trend_7"].shift(4) > 0)
    # )

    return res


def add_shooting_star_to_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add discrete feature is_shooting_star
    """
    res = df.copy()

    # NOTE Currently this is mandatory to run backtests, don't remove
    res = add_bb_forecast(df=res, col_name="Close")

    res["Close_yesterday"] = res["Close"].shift(1)
    res["Low_yesterday"] = res["Low"].shift(1)
    res["High_yesterday"] = res["High"].shift(1)
    res["is_shooting_star"] = res.apply(
        lambda row: check_shooting_star_candle(
            yesterday_close=row["Close_yesterday"],
            yesterday_high=row["High_yesterday"],
            yesterday_low=row["Low_yesterday"],
            today_close=row["Close"],
            today_high=row["High"],
            today_low=row["Low"],
            today_open=row["Open"],
        ),
        axis=1,
    )
    del res["Close_yesterday"]
    del res["Low_yesterday"]
    del res["High_yesterday"]
    return res


def _get_bb_cooling_label(row) -> str:

    # check if oversold conditions start improving
    if (row["forecast_bb_yesterday"]) < -2.4 and (
        row["forecast_bb_yesterday"] < row["forecast_bb"]
    ):
        return "LOW_TO_HIGHER"

    # check if overbought conditions start improving
    if (row["forecast_bb_yesterday"]) > 2.4 and (
        row["forecast_bb_yesterday"] > row["forecast_bb"]
    ):
        return "HIGH_TO_LOWER"

    # base case
    return "NOTHING_SPECIAL"


def add_bb_cooling_to_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add discrete feature bb_cooling,
    i. e. overbought or oversold conditions start improving.
    """
    res = df.copy()

    # We need forecast_bb for this feature
    res = add_bb_forecast(df=res, col_name="Close")
    res["forecast_bb_yesterday"] = res["forecast_bb"].shift(1)
    res["bb_cooling"] = res.apply(_get_bb_cooling_label, axis=1)
    del res["forecast_bb_yesterday"]
    return res


def get_forecast_bb(df: pd.DataFrame) -> pd.Series:
    return df["forecast_bb"]
