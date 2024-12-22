import os
import sys
from typing import Callable, Dict, List, Set

import pandas as pd

from derivative_columns.atr import add_tr_delta_col_to_ohlc

from .import_data import get_local_ticker_data_file_name, import_alpha_vantage_daily

MUST_HAVE_DERIVATIVE_COLUMNS: Set[str] = {"tr", "tr_delta"}

# NOTE tr - True Range
# tr_delta is a must-have column
# because it is used in update_stop_losses()


class TickersData:
    """
    This class stores OHLC data for tickers
    locally and delivers it as needed,
    instead of downloading it from the Internet.
    """

    # NOTE
    # Practice has shown that it is advisable to maintain raw OHLC data,
    # as well as data with added derivative columns and features, in separate files.
    # You'll see the code saves single_raw_XXX.xlsx and single_with_features_XXX.xlsx files.
    # You will often change derived columns and features.
    # In such cases, you only need to delete single_with_features_XXX.xlsx files
    # so that the system creates derivative columns and features again.
    # And you won't have to request the raw OHLC data from the provider again.

    def __init__(
        self,
        tickers: List[str],
        add_feature_cols_func: Callable,
        import_ohlc_func: Callable = import_alpha_vantage_daily,
        recreate_columns_every_time: bool = False,
    ):
        """
        Fill self.tickers_data_with_features
        to serve the get_data() calls.
        Also, save the inputs, because we may need them later.
        """
        self.tickers_data_with_features: Dict[str, pd.DataFrame] = dict()
        self.add_feature_cols_func = add_feature_cols_func
        self.import_ohlc_func = import_ohlc_func
        self.recreate_columns_every_time = recreate_columns_every_time
        for ticker in tickers:
            df = self.get_df_with_features(ticker=ticker)

            # All columns of MUST_HAVE_DERIVATIVE_COLUMNS
            # are essential for running backtests,
            # so ensure DataFrame has them
            for col in MUST_HAVE_DERIVATIVE_COLUMNS:
                if col not in df.columns:
                    df = add_tr_delta_col_to_ohlc(ohlc_df=df)

            self.tickers_data_with_features[ticker] = df

    def get_df_with_features(self, ticker: str) -> pd.DataFrame:
        """
        1. Try to read OHLC data with additional columns from local XLSX file.
        If OK, check data and return it.

        2. Try to read raw OHLC data from local XLSX file.
        If OK, call self.add_feature_cols_func, check data,
        save local XLSX file, and return DataFrame.

        3. If reading data from local XLSX files failed,
        call self.import_ohlc_func and then self.add_feature_cols_func.
        Check the result. Save local XLSX files with raw data
        and with added features. Return DataFrame.
        """

        # if self.recreate_columns_every_time is True -
        # don't use locally cached derived columns,
        # recreate them every time.
        # This is needed for cases when the add_feature_cols_func function
        # is called with different parameters,
        # in order to optimize these parameters.
        # See also the run_strategy_main_optimize.py file.
        if not self.recreate_columns_every_time:
            # try to read feature columns from local cache files
            #  instead of recalculating them
            filename_with_features = get_local_ticker_data_file_name(
                ticker=ticker, data_type="with_features"
            )
            if (
                os.path.exists(filename_with_features)
                and os.path.getsize(filename_with_features) > 0
            ):
                df = pd.read_excel(filename_with_features, index_col=0)
                print(f"Reading {filename_with_features} - OK")
                return df

        filename_raw = get_local_ticker_data_file_name(ticker=ticker, data_type="raw")
        if os.path.exists(filename_raw) and os.path.getsize(filename_raw) > 0:
            df = pd.read_excel(filename_raw, index_col=0)
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            df = self.add_feature_cols_func(df=df)

            # save cache files only if they will be used later
            if not self.recreate_columns_every_time:
                df.to_excel(filename_with_features)
                print(f"Saved {filename_with_features} - OK")

            print(f"Reading {filename_raw} - OK")
            return df

        print(
            f"Running {self.import_ohlc_func.__name__} for {ticker=}...",
            file=sys.stderr,
        )
        df = self.import_ohlc_func(ticker=ticker)
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            error_msg = f"get_df_with_features: failed call of {self.import_ohlc_func} for {ticker=}, returned {df=}"  # pylint: disable=C0301
            raise RuntimeError(error_msg)
        df.to_excel(filename_raw)
        print(f"Saved {filename_raw} - OK")
        df = self.add_feature_cols_func(df=df)
        if not self.recreate_columns_every_time:
            df.to_excel(filename_with_features)
            print(f"Saved {filename_with_features} - OK")
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
