# pylint: disable=E1136
# pylint: disable=E1137
import sys
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from constants import LOG_FILE, tickers_all
from customizable import StrategyParams
from utils.local_data import TickersData
from utils.strategy_exec import process_last_day_res

from .run_backtest_for_ticker import run_backtest_for_ticker


def _add_feature_name_to_trades(
    trades: pd.DataFrame, ticker_data: pd.DataFrame, feature_col_name: str
) -> pd.DataFrame:
    res = trades.copy()
    res["Feature"] = np.nan
    for index, row in trades.iterrows():
        res.at[index, "Feature"] = ticker_data.iloc[row["EntryBar"]][feature_col_name]
    return res


def get_stat_and_trades(
    ohlc_with_feature: pd.DataFrame,
    strategy_params: StrategyParams,
    ticker: str,
    feature_col_name: Optional[str] = None,
) -> Tuple[pd.Series, pd.DataFrame, dict]:
    """
    For ticker, run backtest,
    return stats, trades, and last_day_result.
    If feature_col_name is provided,
    feature value at the start date is added to every trade in trades DataFrame.
    """

    stat, trades, last_day_result = run_backtest_for_ticker(
        ticker=ticker,
        data=ohlc_with_feature,
        strategy_params=strategy_params,
    )

    # NOTE If feature_col_name is None,
    # return stat and trades without added feature,
    # otherwise run _add_feature_name_to_trades() and then return
    if feature_col_name:
        return (
            stat,
            _add_feature_name_to_trades(
                trades=trades,
                ticker_data=ohlc_with_feature,
                feature_col_name=feature_col_name,
            ),
            last_day_result,
        )

    return stat, trades, last_day_result


def run_all_tickers(
    tickers_data: TickersData,
    strategy_params: StrategyParams,
    tickers: List[str],
) -> float:
    """
    1. For every ticker, run get_stat_and_trades.
    2. Run process_last_day_res - send notification if trading signal.
    3. Unite all results.
    4. Save them to xlsx file.
    5. Return mean value of SQN_modified.
    """

    # clear LOG_FILE every time
    open(LOG_FILE, "w", encoding="UTF-8").close()

    performance_res = pd.DataFrame()
    if strategy_params.save_all_trades_in_xlsx:
        all_trades = pd.DataFrame()
    counter = 0
    total_len = len(tickers)
    for ticker in tickers:
        counter = counter + 1
        print("", file=sys.stderr)
        print(
            f"Running backtest for {ticker=}, {counter} of {total_len}...",
            file=sys.stderr,
        )

        ticker_data = tickers_data.get_data(ticker=ticker)

        # NOTE You can run get_stat_and_trades
        # with some feature (feature_col_name=something) or without it.
        # If feature_col_name is provided, feature value at the start date
        # is added to every trade in trades DataFrame (trades_df).

        stat, trades_df, last_day_result = get_stat_and_trades(
            ohlc_with_feature=ticker_data,
            ticker=ticker,
            feature_col_name=None,
            strategy_params=strategy_params,
        )
        process_last_day_res(last_day_res=last_day_result)
        stat = stat.drop(["_strategy", "_equity_curve", "_trades"])
        stat["Start"] = stat["Start"].date()
        stat["End"] = stat["End"].date()

        # NOTE This is to avoid a false high value of SQN
        # if the number of trades for ticker is above 100.
        # Good value for this indicator is above 0,2.
        stat["SQN_modified"] = stat["SQN"] / np.sqrt(stat["# Trades"])

        performance_res[ticker] = stat

        if strategy_params.save_all_trades_in_xlsx:
            trades_df["Ticker"] = ticker
            all_trades = pd.concat([all_trades, trades_df])

    if len(tickers) > 1:
        performance_res.to_excel("output.xlsx")
    if strategy_params.save_all_trades_in_xlsx:
        all_trades.to_excel("all_trades.xlsx", index=False)
    return performance_res.loc["SQN_modified", :].mean()
