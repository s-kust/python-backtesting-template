import pickle
from typing import Callable, Dict, List, Optional

import pandas as pd

from constants import (
    LOCAL_DAILY_OHLC_RAW_PKL,
    LOCAL_DAILY_OHLC_WITH_FEATURES_PKL,
    tickers_all,
)

from .import_data import import_alpha_vantage_daily


def prepare_raw_local_data(
    tickers: List[str], import_ohlc_func: Callable
) -> Dict[str, pd.DataFrame]:
    res: Dict[str, pd.DataFrame] = dict()
    counter = 0
    total_count = len(tickers)
    for ticker in tickers:
        counter = counter + 1
        df = import_ohlc_func(ticker=ticker)
        res[ticker] = df
        print(f"prepare_raw_local_data: {ticker=} - {counter} of {total_count} - OK")
    with open(LOCAL_DAILY_OHLC_RAW_PKL, "wb") as local_file:
        pickle.dump(res, local_file)
    print(f"prepare_raw_local_data: saving {LOCAL_DAILY_OHLC_RAW_PKL} - OK")
    return res


class TickersData:
    """
    This class stores OHLC data for tickers
    in local pickle file LOCAL_DAILY_OHLC_PKL
    and delivers it as needed,
    instead of downloading it from the Internet
    """

    def __init__(
        self,
        tickers: List[str] = tickers_all,
        import_ohlc_func: Callable = import_alpha_vantage_daily,
        add_feature_cols_func: Optional[Callable] = None,
    ):
        try:
            with open(LOCAL_DAILY_OHLC_RAW_PKL, "rb") as local_file:
                res = pickle.load(local_file)
        except OSError:  # file not found
            res = prepare_raw_local_data(
                tickers=tickers, import_ohlc_func=import_ohlc_func
            )
        self.tickers_data_raw = res
        self.import_ohlc_func = import_ohlc_func
        self.add_feature_cols_func = add_feature_cols_func
        if add_feature_cols_func:
            self.tickers_data_with_feature = dict()
            for ticker in res:
                self.tickers_data_with_feature[ticker] = add_feature_cols_func(
                    df=res[ticker]
                )

    def get_data(self, ticker: str, raw: bool = True) -> pd.DataFrame:
        if raw:
            if self.tickers_data_raw and ticker in self.tickers_data_raw:
                return self.tickers_data_raw[ticker]
            self.tickers_data_raw[ticker] = self.import_ohlc_func(ticker=ticker)
            return self.tickers_data_raw[ticker]

        if self.add_feature_cols_func is None:
            err_msg = "get_data: elf.add_feature_cols_func is None, can't return DF with feature"
            raise ValueError(err_msg)
        if self.tickers_data_with_feature and ticker in self.tickers_data_with_feature:
            return self.tickers_data_with_feature[ticker]
        self.tickers_data_raw[ticker] = self.import_ohlc_func(ticker=ticker)
        self.tickers_data_with_feature[ticker] = self.add_feature_cols_func(
            df=self.tickers_data_raw[ticker]
        )
        return self.tickers_data_with_feature[ticker]
