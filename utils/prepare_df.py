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


def add_features_forecasts_to_ohlc_v1(df: pd.DataFrame) -> pd.DataFrame:

    # NOTE 1. Customize this function to add forecasts and features
    # that you want. You may have

    # NOTE 2. You can have and support multiple similar functions
    # with different sets of features and forecasts.
    # The function you want to use now needs to be passed
    # as add_features_forecasts_func parameter
    # when calling the function get_stat_and_trades_for_ticker.

    res = df.copy()
    res = add_bb_forecast(df=res, col_name="Close")
    return res


def get_df_with_fwd_ret(ticker: str, num_days: int = 24) -> pd.DataFrame:
    res = import_ohlc_daily(ticker=ticker)
    res = add_features_forecasts_to_ohlc_v1(df=res)
    res[f"Close_fwd_{str(num_days)}"] = res["Close"].shift(-num_days)
    res[f"ret_{str(num_days)}"] = (
        (res[f"Close_fwd_{str(num_days)}"] - res["Close"]) / res["Close"]
    ) * 100
    res[f"ret_{str(num_days)}"] = round(res[f"ret_{str(num_days)}"], 2)
    del res[f"Close_fwd_{str(num_days)}"]
    return res


def get_forecast_bb(df: pd.DataFrame) -> pd.Series:
    return df["forecast_bb"]
