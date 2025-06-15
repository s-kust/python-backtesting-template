from typing import List

import numpy as np
import pandas as pd

from constants import DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL
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
