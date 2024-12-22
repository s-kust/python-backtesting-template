# pylint: disable=C0121
# pylint: disable=E2515
import sys
from typing import List

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from constants import (
    DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL,
    FEATURE_COL_NAME_BASIC,
    LOG_FILE,
    tickers_all,
)
from customizable.misc import get_ma_200_relation_label
from features.f_v1_basic import add_features_v1_basic
from utils.bootstrap import analyze_values_by_group, get_bootstrapped_mean_ci
from utils.get_df_with_fwd_ret import add_fwd_ret
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

    for ticker in tickers_data.tickers_data_with_features:
        if (
            f"fwd_ret_{fwd_ret_days}"
            not in tickers_data.tickers_data_with_features[ticker].columns
        ):
            tickers_data.tickers_data_with_features[ticker] = add_fwd_ret(
                ohlc_df=tickers_data.tickers_data_with_features[ticker],
                num_days=fwd_ret_days,
            )

    combined_df_all = pd.DataFrame()
    for ticker in tickers_data.tickers_data_with_features:
        combined_df_all = pd.concat(
            [combined_df_all, tickers_data.tickers_data_with_features[ticker]]
        )

    mask_feature_true = combined_df_all[feature_col_name] == True
    mask_feature_false = combined_df_all[feature_col_name] == False

    returns_f_true = (
        combined_df_all[mask_feature_true][f"fwd_ret_{fwd_ret_days}"].dropna().values
    )

    returns_f_false = (
        combined_df_all[mask_feature_false][f"fwd_ret_{fwd_ret_days}"].dropna().values
    )

    # This saves memory and speeds up the execution.
    for ticker in tickers_data.tickers_data_with_features:
        del tickers_data.tickers_data_with_features[ticker][f"fwd_ret_{fwd_ret_days}"]

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
        # create an empty row and append it to the resulting list
        # to improve the viewing experience of the resulting DataFrame
        res_f_empty = res_f_true.copy()
        res_f_empty["feature"] = np.nan
        res_f_empty[f"ci_left_{DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL}"] = np.nan
        res_f_empty[f"ci_right_{DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL}"] = np.nan
        res_f_empty["mean_val"] = np.nan
        res_f_empty["positive_pct"] = np.nan
        res_f_empty["count"] = np.nan
        res_to_return.append(res_f_empty)

    return res_to_return


def add_group_label_analyze_save(
    tickers_data: TickersData, excel_file_name: str, fwd_red_n_days: int
) -> None:
    group_col_name = "close_rel_ma_200_group"

    # Now add forward returns column to analyze it

    # NOTE We don't need forward returns to run backtests,
    # so we add them only here,
    # not inside the TickersData class or anywhere else.
    for ticker in tickers_data.tickers_data_with_features:
        tickers_data.tickers_data_with_features[ticker] = add_fwd_ret(
            ohlc_df=tickers_data.tickers_data_with_features[ticker],
            num_days=fwd_red_n_days,
        )

    # Add a column with a group label
    # and concatenate the DFs of all tickers into one large DF.
    combined_ohlc_all = pd.DataFrame()
    for ticker, ohlc_df in tickers_data.tickers_data_with_features.items():
        ohlc_df[group_col_name] = ohlc_df.apply(get_ma_200_relation_label, axis=1)
        combined_ohlc_all = pd.concat([combined_ohlc_all, ohlc_df])
        del ohlc_df[group_col_name]
        del ohlc_df[f"fwd_ret_{fwd_red_n_days}"]

    combined_ohlc_all = combined_ohlc_all.dropna()

    # just in case...
    print(f"{combined_ohlc_all.shape=}")
    print(f"{combined_ohlc_all.columns=}")
    print(combined_ohlc_all.tail())

    # Up until this point there has been preparation,
    # and now the analysis will be carried out.

    # NOTE This is for convenient sorting of rows
    # in the resulting Excel file.
    group_order_ma_200_rel = {
        "HIGHLY_ABOVE": 1,
        "MODERATELY_ABOVE": 2,
        "SLIGHTLY_ABOVE": 3,
        "SLIGHTLY_BELOW": 4,
        "MODERATELY_BELOW": 5,
        "HIGHLY_BELOW": 6,
        "all_data": 7,  # all_data row is important, don't miss it
    }

    analyze_values_by_group(
        df=combined_ohlc_all,
        group_col_name=group_col_name,
        values_col_name=f"fwd_ret_{fwd_red_n_days}",
        group_order_map=group_order_ma_200_rel,
        excel_file_name=excel_file_name,
    )


if __name__ == "__main__":
    load_dotenv()

    # clear LOG_FILE every time
    open(LOG_FILE, "w", encoding="UTF-8").close()

    EXCEL_FILE_NAME_BY_GROUP = "res_ma_200_by_group.xlsx"
    EXCEL_FILE_NAME_SIMPLE = "res_ma_200_above_below.xlsx"

    # The first step is to collect DataFrames with data and derived columns
    # for all the tickers we are interested in.
    # This data is stored in the TickersData class instance
    # as a dictionary whose keys are tickers and values ​are DFs.

    # For more details, see the class TickersData internals
    # and the add_features_v1_basic function.
    tickers_data_instance = TickersData(
        tickers=tickers_all,
        add_feature_cols_func=add_features_v1_basic,
    )

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

    # Manipulate with columns for viewing convenience
    df.insert(0, "feature", df.pop("feature"))
    df.insert(0, "fwd_ret_days", df.pop("fwd_ret_days"))
    df.sort_values(["fwd_ret_days", "feature"], ascending=[True, True])
    df.loc[df["mean_val"] != df["mean_val"], "fwd_ret_days"] = np.nan

    df.to_excel(EXCEL_FILE_NAME_SIMPLE, index=False)
    print(
        f"Analysis complete! Now you may explore the results file {EXCEL_FILE_NAME_SIMPLE}",
        file=sys.stderr,
    )
    add_group_label_analyze_save(
        tickers_data=tickers_data_instance,
        excel_file_name=EXCEL_FILE_NAME_BY_GROUP,
        fwd_red_n_days=4,
    )
    print(
        f"Complete! Please see the files {EXCEL_FILE_NAME_SIMPLE}, {EXCEL_FILE_NAME_BY_GROUP}",
        file=sys.stderr,
    )
