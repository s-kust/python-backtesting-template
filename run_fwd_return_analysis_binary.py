# pylint: disable=E2515
import sys
from typing import List

import pandas as pd
from dotenv import load_dotenv

from constants import LOG_FILE, tickers_all
from features.f_rsi import add_feature_rsi_within_bounds
from features.f_v1_basic import (
    add_feature_closed_lower_4_days_in_a_row,
    add_features_v2_basic,
)
from utils.filter_df import FilterParams, RemainingPart, filter_df_by_date
from utils.fwd_return_analysis import (
    add_rows_with_feature_true_and_false_to_res,
    get_combined_df_with_fwd_ret,
    insert_empty_row_to_res,
    res_df_final_manipulations,
)
from utils.local_data import TickersData

INSERT_EMPTY_ROW = True

# Below are parameters that you'll have to edit frequently before running this script:
# 1. List of tickers when initializing the TickersData instance.
# 2. Range of days FWD_RETURN_DAYS_MIN - FWD_RETURN_DAYS_MAX.
# 3. RES_FILE_NAME template.
# 4. Filtering parameters of the combined DataFrame df_filtering_params.

# If you change the feature you are testing,
# you also need to change add_feature_cols_func

# It seems to be all :)

# NOTE If you change the feature, you need to delete
# the single_with_features_***.xlsx file from the cache folder,
# otherwise the change will not work.

tickers_to_process = ["SPY"]
FWD_RETURN_DAYS_MIN = 2
FWD_RETURN_DAYS_MAX = 16
RES_FILE_NAME = "res/res_SPY_closed_lower_4x_all.xlsx"

# NOTE if do_filtering is False, date_threshold and remaining_part don't matter
# because there will be no DataFrame filtering
df_filtering_params = FilterParams(
    do_filtering=False,
    date_threshold="2023-01-01",
    remaining_part=RemainingPart.AFTER,
)

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
    tickers_data_instance = TickersData(
        tickers=tickers_to_process,
        add_feature_cols_func=add_feature_closed_lower_4_days_in_a_row,
    )

    res: List[dict] = list()

    # Now we run the test for each number of days in the range,
    # form the list of dictionaries
    # and make the resulting DataFrame from it.
    for fwd_return_days in range(FWD_RETURN_DAYS_MIN, FWD_RETURN_DAYS_MAX + 1):
        print(
            f"Now check for fwd returns {fwd_return_days} days - up to {FWD_RETURN_DAYS_MAX}"
        )
        combined_df_all = get_combined_df_with_fwd_ret(
            tickers_data=tickers_data_instance, fwd_ret_days=fwd_return_days
        )

        # NOTE With this function, you can analyze only data for the latest periods.
        # Or, conversely, analyze older data, excluding recent periods
        # from consideration.

        combined_df_all = filter_df_by_date(
            df=combined_df_all, filter_params=df_filtering_params
        )

        res = add_rows_with_feature_true_and_false_to_res(
            res_to_return=res,
            combined_df_all=combined_df_all,
            fwd_ret_days=fwd_return_days,
        )

        # NOTE INSERT_EMPTY_ROW is needed for more convenient
        # viewing of results in the Excel file.
        if INSERT_EMPTY_ROW:
            res = insert_empty_row_to_res(res=res, row_template=res[-1].copy())

    df = pd.DataFrame(res)
    df = res_df_final_manipulations(df=df)
    df.to_excel(RES_FILE_NAME, index=False)
    print(
        f"Analysis complete! Now you may explore the results file {RES_FILE_NAME}",
        file=sys.stderr,
    )
