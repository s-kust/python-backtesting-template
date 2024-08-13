from typing import Optional, Tuple

import numpy as np
import pandas as pd

from utils.import_data import import_ohlc_daily
from utils.prepare_df import get_df_with_forecasts

from .run_backtest_for_ticker import run_backtest_for_ticker


def get_stat_and_trades_for_ticker(
    ticker: str,
    max_trade_duration_long: Optional[int] = None,
    max_trade_duration_short: Optional[int] = None,
    feature_col_name: Optional[str] = None,
    strategy_params: Optional[dict] = None,
) -> Tuple[pd.Series, pd.DataFrame, dict]:
    """
    For ticker, import OHLC data and then run backtest,
    return stats, trades, and last_day_result.
    If feature_col_name is provided,
    feature value at the start date is added to every trade in trades DataFrame.
    """

    ticker_data = import_ohlc_daily(ticker=ticker)

    # NOTE customize get_df_with_forecasts function
    # to add forecasts and features that you want
    ticker_data = get_df_with_forecasts(df=ticker_data)

    stat, trades, last_day_result = run_backtest_for_ticker(
        ticker=ticker,
        data=ticker_data,
        max_trade_duration_long=max_trade_duration_long,
        max_trade_duration_short=max_trade_duration_short,
        strategy_params=strategy_params,
    )

    # NOTE If feature_col_name is None,
    # return stat and trades without added feature,
    # otherwise run add_feature_to_trades and then return
    if feature_col_name:
        return (
            stat,
            add_feature_to_trades(
                trades=trades,
                ticker_data=ticker_data,
                feature_col_name=feature_col_name,
            ),
            last_day_result,
        )

    return stat, trades, last_day_result


def add_feature_to_trades(
    trades: pd.DataFrame, ticker_data: pd.DataFrame, feature_col_name: str
) -> pd.DataFrame:
    res = trades.copy()
    res["Feature"] = np.nan
    for index, row in trades.iterrows():
        res.at[index, "Feature"] = ticker_data.iloc[row["EntryBar"]][feature_col_name]
    return res
