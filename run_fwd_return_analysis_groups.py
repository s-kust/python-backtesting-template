import sys

import pandas as pd
from dotenv import load_dotenv

from constants import GROUP_COLUMN_NAME, LOG_FILE
from features.f_rsi import add_feature_high_rsi
from features.partition_groups.rsi_bounds import (
    get_rsi_group_label,
    group_order_rsi_bounds,
)
from utils.bootstrap import analyze_values_by_group
from utils.filter_df import FilterParams, RemainingPart, filter_df_by_date
from utils.fwd_return_analysis import get_combined_df_with_fwd_ret_for_groups
from utils.local_data import TickersData


def analyze_data_by_group_save_res(
    combined_df: pd.DataFrame,
    fwd_ret_n_days: int,
    res_xlsx_file_name: str,
    df_filter_params: FilterParams,
) -> None:
    """
    Analyze data by group and save results in Excel file
    """

    # NOTE With this function, you can analyze only data for the latest periods.
    # Or, conversely, analyze older data, excluding recent periods
    # from consideration.

    combined_df = filter_df_by_date(df=combined_df, filter_params=df_filter_params)

    analyze_values_by_group(
        df=combined_df,
        group_col_name=GROUP_COLUMN_NAME,
        values_col_name=f"fwd_ret_{fwd_ret_n_days}",
        group_order_map=group_order_rsi_bounds,
        excel_file_name=res_xlsx_file_name,
    )
    print(
        f"Complete! Please see the file {res_xlsx_file_name}",
        file=sys.stderr,
    )


if __name__ == "__main__":

    # What you'll have to edit frequently before running this script:
    # 1. List of tickers when initializing the TickersData instance.
    # 2. Filtering parameters of the combined DataFrame df_filtering_params.
    # 3. Range of days fwd_ret_days.
    # 4. RES_FILE_NAME template.

    # If you change the feature you are testing,
    # you also need to change the following parameters:
    # 1. add_feature_cols_func
    # 2. labelling_func
    # 3. group_order_map

    # That seems to be all :)

    load_dotenv()

    # clear LOG_FILE every time
    open(LOG_FILE, "w", encoding="UTF-8").close()

    # The first step is to collect DataFrames with data and derived columns
    # for all the tickers we are interested in.
    # This data is stored in the TickersData class instance
    # as a dictionary whose keys are tickers and values ​are DFs.
    # For more details, see the class TickersData internals.

    # TODO Get rid of adding a binary feature if we don't need it.
    # Now inside the TickersData class a binary feature will be added
    # only for adding the RSI column and then assign a group based on RSI value.
    tickers_data_instance = TickersData(
        tickers=["CPER"],
        add_feature_cols_func=add_feature_high_rsi,
    )

    # NOTE if do_filtering is False, date_threshold and remaining_part don't matter
    # because there will be no DataFrame filtering
    df_filtering_params = FilterParams(
        do_filtering=True,
        date_threshold="2023-01-01",
        remaining_part=RemainingPart.AFTER,
    )

    for fwd_ret_days in range(3, 16):

        combined_ohlc_group_df = get_combined_df_with_fwd_ret_for_groups(
            tickers_data=tickers_data_instance,
            fwd_red_n_days=fwd_ret_days,
            labelling_func=get_rsi_group_label,
        )

        RES_FILE_NAME = f"res/res_CPER_by_RSI_group_{fwd_ret_days}_days_recent.xlsx"
        analyze_data_by_group_save_res(
            combined_df=combined_ohlc_group_df,
            fwd_ret_n_days=fwd_ret_days,
            res_xlsx_file_name=RES_FILE_NAME,
            df_filter_params=df_filtering_params,
        )
