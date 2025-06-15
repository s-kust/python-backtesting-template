import sys
from typing import Callable

import pandas as pd
from dotenv import load_dotenv

from constants import LOG_FILE
from features.f_rsi import add_feature_high_rsi
from features.partition_groups.rsi_bounds import (
    get_rsi_group_label,
    group_order_rsi_bounds,
)
from utils.bootstrap import analyze_values_by_group
from utils.fwd_return_analysis import filter_df_by_date
from utils.get_df_with_fwd_ret import add_fwd_ret
from utils.local_data import TickersData

GROUP_COLUMN_NAME = "group_label"


def _get_combined_df_with_fwd_ret(
    tickers_data: TickersData, fwd_red_n_days: int, labelling_func: Callable
) -> pd.DataFrame:
    """
    Prepare a combined dataframe with a column containing the group label
    for all tickers contained in tickers_data.
    """

    # Now add forward returns column to analyze it
    # NOTE We don't need forward returns to run backtests,
    # so we add them here instead of inside the TickersData class.
    for ticker in tickers_data.tickers_data_with_features:
        tickers_data.tickers_data_with_features[ticker] = add_fwd_ret(
            ohlc_df=tickers_data.tickers_data_with_features[ticker],
            num_days=fwd_red_n_days,
        )

    # Add a column with a group label
    # and concatenate the DFs of all tickers into one large DF.
    combined_ohlc_all = pd.DataFrame()
    for ticker, ohlc_df in tickers_data.tickers_data_with_features.items():
        ohlc_df[GROUP_COLUMN_NAME] = ohlc_df.apply(labelling_func, axis=1)
        combined_ohlc_all = pd.concat([combined_ohlc_all, ohlc_df])
        del ohlc_df[GROUP_COLUMN_NAME]
        del ohlc_df[f"fwd_ret_{fwd_red_n_days}"]

    combined_ohlc_all = combined_ohlc_all.dropna()

    # just in case...
    # print(f"{combined_ohlc_all.shape=}")
    # print(f"{combined_ohlc_all.columns=}")
    print(combined_ohlc_all.tail())

    return combined_ohlc_all


if __name__ == "__main__":
    load_dotenv()

    # clear LOG_FILE every time
    open(LOG_FILE, "w", encoding="UTF-8").close()

    # The first step is to collect DataFrames with data and derived columns
    # for all the tickers we are interested in.
    # This data is stored in the TickersData class instance
    # as a dictionary whose keys are tickers and values ​are DFs.

    # For more details, see the class TickersData internals
    # and the add_features_v1_basic function.

    # TODO Get rid of adding a binary feature if we don't need it.
    # Now inside the TickersData class a binary feature will be added
    # only for adding the RSI column and then assign a group based on RSI value.
    tickers_data_instance = TickersData(
        tickers=["GLD"],
        add_feature_cols_func=add_feature_high_rsi,
    )

    for fwd_ret_days in range(13, 14):

        combined_ohlc_group_df = _get_combined_df_with_fwd_ret(
            tickers_data=tickers_data_instance,
            fwd_red_n_days=fwd_ret_days,
            labelling_func=get_rsi_group_label,
        )

        RES_FILE_NAME = f"res_GLD_by_RSI_group_{fwd_ret_days}_days.xlsx"

        # NOTE With this function, you can analyze only data for the latest periods.
        # Or, conversely, analyze older data, excluding recent periods
        # from consideration.

        # combined_ohlc_group_df = filter_df_by_date(
        #     df=combined_ohlc_group_df,
        #     date_threshold="2023-01-01",
        #     remaining_part="before",
        # )

        analyze_values_by_group(
            df=combined_ohlc_group_df,
            group_col_name=GROUP_COLUMN_NAME,
            values_col_name=f"fwd_ret_{fwd_ret_days}",
            group_order_map=group_order_rsi_bounds,
            excel_file_name=RES_FILE_NAME,
        )
        print(
            f"Complete! Please see the file {RES_FILE_NAME}",
            file=sys.stderr,
        )
