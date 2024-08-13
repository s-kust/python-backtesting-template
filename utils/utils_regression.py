import statsmodels.formula.api as sm
from import_data import import_ohlc_daily
from prepare_df import get_df_with_forecasts


def run_regression_single(ticker: str, ema_fast: int, ema_slow: int):

    print(f"{ticker=}, {ema_fast=}, {ema_slow=}")
    res = import_ohlc_daily(ticker=ticker)

    # res = get_df_with_forecasts(df=res, ema_fast=16, ema_slow=64)
    # res = get_df_with_forecasts(df=res, ema_fast=32, ema_slow=128)
    res = get_df_with_forecasts(df=res, ema_fast=ema_fast, ema_slow=ema_slow)
    res["Close_fwd_24"] = res["Close"].shift(-24)
    res["ret_24"] = ((res["Close_fwd_24"] - res["Close"]) / res["Close"]) * 100
    res["ret_24"] = round(res["ret_24"], 2)
    res = res.dropna()
    # result = sm.ols(formula="ret_24 ~ forecast_rc", data=res).fit()
    result = sm.ols(formula="ret_24 ~ forecast_momentum", data=res).fit()
    print(res["momentum_10"].describe())
    print(res["forecast_momentum"].describe())
    print(result.summary())
    print(
        "===================================================================================================================="
    )
    print()
