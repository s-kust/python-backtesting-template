import sys
from typing import Optional

import numpy as np
import pandas as pd

from constants import tickers_all
from utils.prepare_df import add_bb_forecast_to_ohlc
from utils.strategy_exec import process_last_day_res

from .get_stat_and_trades_for_ticker import get_stat_and_trades_for_ticker


def run_all_tickers(
    max_trade_duration_long: Optional[int] = None,
    max_trade_duration_short: Optional[int] = None,
    strategy_params: Optional[dict] = None,
) -> float:
    """
    1. For every ticker, run get_stat_and_trades.
    2. Run process_last_day_res - send notification if trading signal.
    3. Unite all results.
    4. Save them to xlsx file.
    5. Return mean value of SQN_modified.
    """
    tickers = tickers_all
    # tickers = ["SOYB"]
    # tickers = ["QQQ", "XME"]
    # tickers = ["QQQ"]

    res = pd.DataFrame()
    counter = 0
    total_len = len(tickers)
    for ticker in tickers:
        counter = counter + 1
        print("", file=sys.stderr)
        print(f"Running {ticker=}, {counter} of {total_len}...", file=sys.stderr)
        print("", file=sys.stderr)

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

        res[ticker] = stat
    if len(tickers) > 1:
        res.to_excel("output.xlsx")
    return res.loc["SQN_modified", :].mean()
