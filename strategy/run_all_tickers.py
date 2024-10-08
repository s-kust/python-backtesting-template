import sys
from typing import List, Optional

import numpy as np
import pandas as pd

from constants import tickers_all
from utils.prepare_df import add_bb_forecast_to_ohlc
from utils.strategy_exec import process_last_day_res

from .get_stat_and_trades_for_ticker import get_stat_and_trades_for_ticker


def run_all_tickers(
    tickers: List[str] = tickers_all,
    max_trade_duration_long: Optional[int] = None,
    max_trade_duration_short: Optional[int] = None,
    strategy_params: Optional[dict] = None,
    save_all_trades_in_xlsx: bool = False,
) -> float:
    """
    1. For every ticker, run get_stat_and_trades.
    2. Run process_last_day_res - send notification if trading signal.
    3. Unite all results.
    4. Save them to xlsx file.
    5. Return mean value of SQN_modified.
    """

    performance_res = pd.DataFrame()
    if save_all_trades_in_xlsx:
        all_trades = pd.DataFrame()
    counter = 0
    total_len = len(tickers)
    for ticker in tickers:
        counter = counter + 1
        print("", file=sys.stderr)
        print(f"Running {ticker=}, {counter} of {total_len}...", file=sys.stderr)

        # NOTE You can run get_stat_and_trades_for_ticker
        # with some feature (feature_col_name=something)
        # or without it

        stat, trades_df, last_day_result = get_stat_and_trades_for_ticker(
            ticker=ticker,
            add_features_forecasts_func=add_bb_forecast_to_ohlc,
            max_trade_duration_long=max_trade_duration_long,
            max_trade_duration_short=max_trade_duration_short,
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

        if save_all_trades_in_xlsx:
            trades_df["Ticker"] = ticker
            all_trades = pd.concat([all_trades, trades_df])

    if len(tickers) > 1:
        performance_res.to_excel("output.xlsx")
    if save_all_trades_in_xlsx:
        all_trades.to_excel("all_trades.xlsx", index=False)
    return performance_res.loc["SQN_modified", :].mean()
