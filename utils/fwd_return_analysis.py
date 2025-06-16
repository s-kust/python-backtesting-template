# pylint: disable=C0121
from typing import Callable, List

import numpy as np
import pandas as pd

from constants import (
    DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL,
    FEATURE_COL_NAME_BASIC,
    GROUP_COLUMN_NAME,
)
from utils.bootstrap import get_bootstrapped_mean_ci
from utils.get_df_with_fwd_ret import add_fwd_ret
from utils.local_data import TickersData


def res_df_final_manipulations(df: pd.DataFrame) -> pd.DataFrame:
    """
    For easier viewing of results, in the dataframe:
    1. Rearrange the columns.
    2. Delete the fwd_ret_days number from the empty rows.
    """

    # 1
    df.insert(0, "feature", df.pop("feature"))
    df.insert(0, "fwd_ret_days", df.pop("fwd_ret_days"))
    df.sort_values(["fwd_ret_days", "feature"], ascending=[True, True])

    # 2
    df.loc[df["mean_val"] != df["mean_val"], "fwd_ret_days"] = np.nan

    return df


def insert_empty_row_to_res(res: List[dict], row_template: dict) -> List[dict]:
    """
    To improve the viewing experience of the resulting DataFrame,
    make a nearly empty row out of the row_template and append it to the result.
    """
    # NOTE The function does not touch
    # the value of the fwd_ret_days key in row_template,
    # so that it can be used for sorting later.
    row_template["feature"] = np.nan
    row_template[f"ci_left_{DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL}"] = np.nan
    row_template[f"ci_right_{DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL}"] = np.nan
    row_template["mean_val"] = np.nan
    row_template["positive_pct"] = np.nan
    row_template["count"] = np.nan
    res.append(row_template)
    return res


def get_combined_df_with_fwd_ret(
    tickers_data: TickersData,
    fwd_ret_days: int,
) -> pd.DataFrame:
    """
    1. For each ticker, call add_fwd_ret function
    to add the fwd_ret_{fwd_ret_days} column to its dataframe,
    containing forward returns.

    2. Create a big merged dataframe from the dataframes for all tickers.

    3. For each ticker, remove the fwd_ret_{fwd_ret_days} column from its dataframe
    to free up memory and speed up the script.

    4. Return the big merged dataframe.
    """

    # 1
    for ticker in tickers_data.tickers_data_with_features:
        if (
            f"fwd_ret_{fwd_ret_days}"
            not in tickers_data.tickers_data_with_features[ticker].columns
        ):
            tickers_data.tickers_data_with_features[ticker] = add_fwd_ret(
                ohlc_df=tickers_data.tickers_data_with_features[ticker],
                num_days=fwd_ret_days,
            )

    # 2
    combined_df_all = pd.DataFrame()
    for ticker in tickers_data.tickers_data_with_features:
        combined_df_all = pd.concat(
            [combined_df_all, tickers_data.tickers_data_with_features[ticker]]
        )

    # 3
    for ticker in tickers_data.tickers_data_with_features:
        del tickers_data.tickers_data_with_features[ticker][f"fwd_ret_{fwd_ret_days}"]

    # 4
    return combined_df_all


def add_rows_with_feature_true_and_false_to_res(
    res_to_return: List[dict], combined_df_all: pd.DataFrame, fwd_ret_days: int
) -> List[dict]:
    """
    1. Form rows with feature True and False
    2. Add them to result
    """

    # 1

    # Filter returns on days when the feature value is True and False,
    # so that we can compare them.
    mask_feature_true = combined_df_all[FEATURE_COL_NAME_BASIC] == True
    mask_feature_false = combined_df_all[FEATURE_COL_NAME_BASIC] == False
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

    # 2

    res_to_return.append(res_f_true)
    res_to_return.append(res_f_false)

    return res_to_return


def get_combined_df_with_fwd_ret_for_groups(
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
    # print(combined_ohlc_all.tail())

    return combined_ohlc_all
