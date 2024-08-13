import sys

import pandas as pd

from constants import tickers_all
from forecast.forecast_bb import add_bb_forecast

from .import_data import add_atr_col_to_df, import_ohlc_daily


class TickersData:
    """
    This class is used when optimizing strategy parameters.
    Its instance stores OHLC data for tickers and delivers it as needed,
    instead of downloading it from the Internet
    or reading it from a local Excel file each time.
    """

    def __init__(self):
        self.tickers_data = dict()
        counter = 0
        total_count = len(tickers_all)
        for ticker in tickers_all:
            counter = counter + 1
            print(
                f"Loading data for {ticker=} - {counter} of {total_count}...",
                file=sys.stderr,
            )
            self.tickers_data[ticker] = import_ohlc_daily(ticker=ticker)
        print("", file=sys.stderr)

    def get_data(self, ticker: str) -> pd.DataFrame:
        if self.tickers_data and ticker in self.tickers_data:
            return self.tickers_data[ticker]
        self.tickers_data[ticker] = import_ohlc_daily(ticker=ticker)
        return self.tickers_data[ticker]


def get_df_with_forecasts(df: pd.DataFrame) -> pd.DataFrame:
    res = df.copy(deep=True)
    rolling_period_tr = 100
    internal_atr_period = 3

    res = add_bb_forecast(df=res, col_name="Close")

    res = add_atr_col_to_df(df=res, n=internal_atr_period)
    res["tr_avg"] = (
        res["tr"]
        .rolling(window=rolling_period_tr, min_periods=rolling_period_tr)
        .mean()
    )
    # NOTE tr_delta is used in update_stop_losses()
    res["tr_delta"] = res[f"atr_{internal_atr_period}"] / res["tr_avg"]
    del res["tr_avg"]

    return res


def get_df_with_fwd_ret(ticker: str, num_days: int = 24) -> pd.DataFrame:
    res = import_ohlc_daily(ticker=ticker)
    res = get_df_with_forecasts(df=res)
    res[f"Close_fwd_{str(num_days)}"] = res["Close"].shift(-num_days)
    res[f"ret_{str(num_days)}"] = (
        (res[f"Close_fwd_{str(num_days)}"] - res["Close"]) / res["Close"]
    ) * 100
    res[f"ret_{str(num_days)}"] = round(res[f"ret_{str(num_days)}"], 2)
    del res[f"Close_fwd_{str(num_days)}"]
    return res


def add_forecasts_and_fwd_ret(df: pd.DataFrame, num_days: int = 24) -> pd.DataFrame:
    """
    Add forecasts and forward returns (diff of Close values)
    """
    res = df.copy()
    res = get_df_with_forecasts(df=res)
    res[f"Close_fwd_{str(num_days)}"] = res["Close"].shift(-num_days)
    res[f"ret_{str(num_days)}"] = (
        (res[f"Close_fwd_{str(num_days)}"] - res["Close"]) / res["Close"]
    ) * 100
    res[f"ret_{str(num_days)}"] = round(res[f"ret_{str(num_days)}"], 2)
    del res[f"Close_fwd_{str(num_days)}"]
    return res


def get_forecast_rc(df: pd.DataFrame) -> pd.Series:
    return df["forecast_rc"]


def get_forecast_momentum(df: pd.DataFrame) -> pd.Series:
    return df["forecast_momentum"]


def get_forecast_bb(df: pd.DataFrame) -> pd.Series:
    return df["forecast_bb"]
