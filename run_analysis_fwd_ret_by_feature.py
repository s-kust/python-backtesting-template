import logging
import sys

import pandas as pd
from dotenv import load_dotenv

from constants import LOG_FILE, tickers_all
from utils.bootstrap import analyze_values_by_group
from utils.grouping.bollinger import get_group_label_forecast_bb, group_order_bb
from utils.misc import add_feature_group_col_to_df
from utils.prepare_df import (
    TickersData,
    add_features_forecasts_to_ohlc_v1_demo,
    get_df_with_fwd_ret,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
)

if __name__ == "__main__":
    load_dotenv()

    NUM_DAYS_FWD_RETURN = 4
    GROUP_COL_NAME = "bb_group"

    # clear LOG_FILE every time
    open(LOG_FILE, "w").close()

    tickers_data = TickersData()
    combined_ohlc_all = pd.DataFrame()
    tickers_total_count = len(tickers_all)
    counter = 0
    for ticker in tickers_all:
        counter = counter + 1
        print(
            f"Running {ticker=}, {counter} of {tickers_total_count}...", file=sys.stderr
        )
        ohlc_with_forecast_bb_and_fwd_ret = get_df_with_fwd_ret(
            ohlc_df=tickers_data.get_data(ticker=ticker),
            add_features_forecasts_func=add_features_forecasts_to_ohlc_v1_demo,
            num_days=NUM_DAYS_FWD_RETURN,
        )
        combined_ohlc_all = pd.concat(
            [combined_ohlc_all, ohlc_with_forecast_bb_and_fwd_ret]
        )
    combined_ohlc_all = combined_ohlc_all.dropna()
    combined_ohlc_all = add_feature_group_col_to_df(
        df=combined_ohlc_all,
        continuous_feature_col_name="forecast_bb",
        new_col_name=GROUP_COL_NAME,
        get_label_for_group=get_group_label_forecast_bb,
    )
    combined_ohlc_all.to_excel("combined_ohlc_all.xlsx", index=False)
    analyze_values_by_group(
        df=combined_ohlc_all,
        group_col_name=GROUP_COL_NAME,
        values_col_name=f"ret_{NUM_DAYS_FWD_RETURN}",
        group_order_map=group_order_bb,
        excel_file_name=f"fwd_ret_{NUM_DAYS_FWD_RETURN}_by_{GROUP_COL_NAME}.xlsx",
    )
