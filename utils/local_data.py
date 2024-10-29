import os
import sys
from typing import Callable, Dict, List, Set

import pandas as pd

from constants import tickers_all
from customizable import add_features_v1_basic
from utils.atr import add_tr_delta_col_to_ohlc

from .import_data import get_local_ticker_data_file_name, import_alpha_vantage_daily

MUST_HAVE_DERIVATIVE_COLUMNS: Set[str] = {"tr", "tr_delta"}

# NOTE tr - True Range
# tr_delta is a must-have column
# because it is used in update_stop_losses()


class TickersData:
    """
    This class stores OHLC data for tickers
    locally and delivers it as needed,
    instead of downloading it from the Internet
    """

    def __init__(
        self,
        add_feature_cols_func: Callable = add_features_v1_basic,
        tickers: List[str] = tickers_all,
        import_ohlc_func: Callable = import_alpha_vantage_daily,
        required_feature_cols: Set[str] = {"forecast_bb"},
    ):
        """
        Save the inputs because we may need them later.
        Most importantly, fill self.tickers_data_with_features
        to serve the get_data() calls.
        """
        self.tickers_data_with_features: Dict[str, pd.DataFrame] = dict()
        self.add_feature_cols_func = add_feature_cols_func
        self.import_ohlc_func = import_ohlc_func
        self.required_feature_cols: Set[str] = required_feature_cols
        self.required_feature_cols.update(MUST_HAVE_DERIVATIVE_COLUMNS)
        for ticker in tickers:
            self.tickers_data_with_features[ticker] = self.get_df_with_features(
                ticker=ticker
            )

    def _check_all_required_feature_columns_in_df(self, df: pd.DataFrame):
        for col_name in self.required_feature_cols:
            if col_name in df.columns:
                continue
            error_msg = f"get_df_with_features: no column {col_name} in DF after calling {self.add_feature_cols_func.__name__}"
            raise ValueError(error_msg)

    def get_df_with_features(self, ticker: str) -> pd.DataFrame:
        """
        1. Try to read OHLC data with features from local XLSX file.
        If OK, check data and return it.

        2. Try to read raw OHLC data from local XLSX file.
        If OK, call self.add_feature_cols_func, check data,
        save local XLSX file, and return DataFrame.

        3. If reading data from local XLSX files failed,
        call self.import_ohlc_func and then self.add_feature_cols_func.
        Check the result. Save local XLSX files with raw data
        and with added features. Return DataFrame.
        """
        filename_with_features = get_local_ticker_data_file_name(
            ticker=ticker, data_type="with_features"
        )
        if (
            os.path.exists(filename_with_features)
            and os.path.getsize(filename_with_features) > 0
        ):
            df = pd.read_excel(filename_with_features, index_col=0)
            for col_name in self.required_feature_cols:
                if col_name not in df.columns:
                    df = add_tr_delta_col_to_ohlc(ohlc_df=df)
                    df = self.add_feature_cols_func(df=df)
                    df.to_excel(filename_with_features)
            self._check_all_required_feature_columns_in_df(df=df)
            print(f"Reading {filename_with_features} - OK")
            return df

        filename_raw = get_local_ticker_data_file_name(ticker=ticker, data_type="raw")
        if os.path.exists(filename_raw) and os.path.getsize(filename_raw) > 0:
            df = pd.read_excel(filename_raw, index_col=0)
            df = add_tr_delta_col_to_ohlc(ohlc_df=df)
            df = self.add_feature_cols_func(df=df)
            self._check_all_required_feature_columns_in_df(df=df)
            df.to_excel(filename_with_features)
            print(f"Reading {filename_raw} - OK")
            return df

        print(
            f"Running {self.import_ohlc_func.__name__} for {ticker=}...",
            file=sys.stderr,
        )
        df = self.import_ohlc_func(ticker=ticker)
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            error_msg = f"get_df_with_features: failed call of {self.import_ohlc_func} for {ticker=}, returned {df=}"
            raise RuntimeError(error_msg)
        df.to_excel(filename_raw)
        df = add_tr_delta_col_to_ohlc(ohlc_df=df)
        df = self.add_feature_cols_func(df=df)
        self._check_all_required_feature_columns_in_df(df=df)
        df.to_excel(filename_with_features)
        return df

    def get_data(self, ticker: str) -> pd.DataFrame:
        """
        Try to get the corresponding DataFrame
        for ticker from self.tickers_data_with_features.
        If it is not possible, fill the corresponding key-value pair
        by calling get_df_with_features(ticker=ticker).
        """
        if (
            self.tickers_data_with_features
            and ticker in self.tickers_data_with_features
        ):
            return self.tickers_data_with_features[ticker]
        self.tickers_data_with_features[ticker] = self.get_df_with_features(
            ticker=ticker
        )
        return self.tickers_data_with_features[ticker]
