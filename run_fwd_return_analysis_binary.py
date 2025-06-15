# pylint: disable=C0121
# pylint: disable=E2515
import sys
from typing import List

import pandas as pd
from dotenv import load_dotenv

from constants import (
    DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL,
    FEATURE_COL_NAME_BASIC,
    LOG_FILE,
    tickers_all,
)
from features.f_rsi import add_feature_high_rsi
from features.f_v1_basic import add_features_v1_basic
from utils.bootstrap import get_bootstrapped_mean_ci
from utils.fwd_return_analysis_binary import (
    get_combined_df_with_fwd_ret,
    insert_empty_row_to_res,
    res_df_final_manipulations,
)
from utils.local_data import TickersData


def _check_feature_for_fwd_ret_days(
    tickers_data: TickersData,
    res_to_return: List[dict],
    fwd_ret_days: int,
    feature_col_name: str,
    insert_empty_row: bool = True,
) -> List[dict]:
    """
    Compare returns over fwd_ret_days subsequent days
    in situations where the feature is True and False.
    The function returns a list with dictionaries.
    Later they will become rows in the final dataframe.
    The function can also add an empty row
    to make the dataframe easier to view.
    To make this clear, see the dataframe example in the README.
    """

    combined_df_all = get_combined_df_with_fwd_ret(
        tickers_data=tickers_data, fwd_ret_days=fwd_ret_days
    )

    # Filter returns on days when the feature value is True and False,
    # so that we can compare them.
    mask_feature_true = combined_df_all[feature_col_name] == True
    mask_feature_false = combined_df_all[feature_col_name] == False
    returns_f_true = (
        combined_df_all[mask_feature_true][f"fwd_ret_{fwd_ret_days}"].dropna().values
    )
    returns_f_false = (
        combined_df_all[mask_feature_false][f"fwd_ret_{fwd_ret_days}"].dropna().values
    )

    # Finding the mean and confidence intervals for returns.
    # The get_bootstrapped_mean_ci function also returns the sample size
    # and the percentage of days where the results are positive.
    res_f_true = get_bootstrapped_mean_ci(
        data=returns_f_true, conf_level=DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL  # type: ignore
    )
    res_f_false = get_bootstrapped_mean_ci(
        data=returns_f_false, conf_level=DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL  # type: ignore
    )

    # Adding columns fwd_ret_days and feature
    # to later sort the dataframe and make it easy to view
    res_f_true["fwd_ret_days"] = res_f_false["fwd_ret_days"] = fwd_ret_days
    res_f_true["feature"] = True
    res_f_false["feature"] = False

    res_to_return.append(res_f_true)
    res_to_return.append(res_f_false)

    if insert_empty_row:
        res_to_return = insert_empty_row_to_res(
            res=res_to_return, row_template=res_f_true.copy()
        )

    return res_to_return


if __name__ == "__main__":
    load_dotenv()

    # clear LOG_FILE every time
    open(LOG_FILE, "w", encoding="UTF-8").close()

    EXCEL_FILE_NAME_SIMPLE = "res_ma_200_above_below.xlsx"

    # The first step is to collect DataFrames with data and derived columns
    # for all the tickers we are interested in.
    # This data is stored in the TickersData class instance
    # as a dictionary whose keys are tickers and values ​are DFs.

    # For more details, see the class TickersData internals
    # and the add_features_v1_basic function.
    tickers_data_instance = TickersData(
        tickers=["SLV"],
        add_feature_cols_func=add_feature_high_rsi,
    )

    # Now we run the test for each number of days in the range,
    # get the list of dictionaries
    # and make the resulting DataFrame from it.
    res: List[dict] = list()
    FWD_RETURN_DAYS_MAX = 16
    for fwd_return_days in range(2, FWD_RETURN_DAYS_MAX + 1):
        print(
            f"Now check for fwd returns {fwd_return_days} days - up to {FWD_RETURN_DAYS_MAX}"
        )
        res = _check_feature_for_fwd_ret_days(
            tickers_data=tickers_data_instance,
            res_to_return=res,
            fwd_ret_days=fwd_return_days,
            insert_empty_row=True,
            feature_col_name=FEATURE_COL_NAME_BASIC,
        )
    df = pd.DataFrame(res)
    df = res_df_final_manipulations(df=df)
    df.to_excel(EXCEL_FILE_NAME_SIMPLE, index=False)
    print(
        f"Analysis complete! Now you may explore the results file {EXCEL_FILE_NAME_SIMPLE}",
        file=sys.stderr,
    )
