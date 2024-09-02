import logging
import sys

import pandas as pd
from dotenv import load_dotenv

from constants import LOG_FILE, tickers_all
from strategy.get_stat_and_trades_for_ticker import get_stat_and_trades_for_ticker
from utils.bootstrap import analyze_values_by_group
from utils.grouping.bollinger import get_group_label_forecast_bb, group_order_bb
from utils.misc import add_feature_group_col_to_df
from utils.prepare_df import add_shooting_star_to_ohlc

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
)


if __name__ == "__main__":
    load_dotenv()

    FEATURE_COLUMN_NAME = "is_shooting_star"

    # clear LOG_FILE every time
    open(LOG_FILE, "w").close()

    tickers_to_run = tickers_all

    combined_trades_all = pd.DataFrame()
    tickers_total_count = len(tickers_to_run)
    counter = 0
    for ticker in tickers_to_run:
        counter = counter + 1
        print(
            f"Running {ticker=}, {counter} of {tickers_total_count}...", file=sys.stderr
        )
        _, trades, _ = get_stat_and_trades_for_ticker(
            ticker=ticker,
            add_features_forecasts_func=add_shooting_star_to_ohlc,
            max_trade_duration_long=None,
            max_trade_duration_short=None,
            feature_col_name=FEATURE_COLUMN_NAME,
            strategy_params=None,
        )
        combined_trades_all = pd.concat([combined_trades_all, trades])
    combined_trades_all.to_excel("combined_trades.xlsx", index=False)
    long_trades = combined_trades_all[combined_trades_all["Size"] > 0]
    short_trades = combined_trades_all[combined_trades_all["Size"] < 0]
    group_order_shooting_star = {True: 0, False: 1, "all_data": 2}
    analyze_values_by_group(
        df=long_trades,
        group_col_name="Feature",
        group_order_map=group_order_shooting_star,
        excel_file_name="trades_analysis_long.xlsx",
    )
    analyze_values_by_group(
        df=short_trades,
        group_col_name="Feature",
        group_order_map=group_order_shooting_star,
        excel_file_name="trades_analysis_short.xlsx",
    )
