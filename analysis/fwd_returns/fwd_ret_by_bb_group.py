import logging
import sys
from typing import Callable, List

import pandas as pd

from constants import LOG_FILE, NUM_DAYS_FWD_RETURN
from utils.bootstrap import analyze_values_by_group
from utils.get_df_with_fwd_ret import get_df_with_fwd_ret
from utils.grouping.bollinger import get_group_label_forecast_bb, group_order_bb
from utils.local_data import TickersData
from utils.misc import add_feature_group_col_to_df
from utils.prepare_df import add_features_v1_basic

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
)


def analyze_fwd_ret_by_bb_group(
    tickers_data: TickersData,
    tickers: List[str],
    excel_file_name: str,
):
    """
    Function analyzes the forward returns,
    noted as the percentage difference of todays and forward Close prices.
    Explanatory variable: distance of today's Close price to its mean value,
    expressed in the number of standard deviations.
    This distance is a continuous value. It is split into discrete groups,
    and then for each group the mean value of the forward return
    and the confidence interval are calculated.
    """
    GROUP_COL_NAME = "bb_group"
    combined_ohlc_all = pd.DataFrame()
    tickers_total_count = len(tickers)
    counter = 0
    for ticker in tickers:
        counter = counter + 1
        print(
            f"Running {ticker=}, {counter} of {tickers_total_count}...", file=sys.stderr
        )

        # add feature to ticker's daily OHLC data
        ohlc_with_forecast_bb_and_fwd_ret = get_df_with_fwd_ret(
            ohlc_df=tickers_data.get_data(ticker=ticker),
            add_features_forecasts_func=add_features_v1_basic,
            num_days=NUM_DAYS_FWD_RETURN,
        )

        # append ticker's daily OHLC data to all OHLC data
        combined_ohlc_all = pd.concat(
            [combined_ohlc_all, ohlc_with_forecast_bb_and_fwd_ret]
        )
    combined_ohlc_all = combined_ohlc_all.dropna()

    # Add a new column containing the label of the group the forecast_bb value belongs to.
    # The details of the add_feature_group_col_to_df function are probably worth your attention.
    combined_ohlc_all = add_feature_group_col_to_df(
        df=combined_ohlc_all,
        continuous_feature_col_name="forecast_bb",
        new_col_name=GROUP_COL_NAME,
        get_label_for_group=get_group_label_forecast_bb,
    )
    # combined_ohlc_all.to_excel("combined_ohlc_all.xlsx", index=False)

    # Up until this point there has been preparation,
    # and now the analysis will be carried out.
    analyze_values_by_group(
        df=combined_ohlc_all,
        group_col_name=GROUP_COL_NAME,
        values_col_name=f"ret_{NUM_DAYS_FWD_RETURN}",
        group_order_map=group_order_bb,
        excel_file_name=excel_file_name,
    )
    print(
        f"analyze_fwd_ret_by_bb_group - complete! Now you may explore the results file {excel_file_name}",
        file=sys.stderr,
    )
