import pandas as pd

from forecast.forecast_bb import add_bb_forecast


def add_features_v1_basic(df: pd.DataFrame) -> pd.DataFrame:

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
