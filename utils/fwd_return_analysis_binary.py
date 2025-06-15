from typing import List

import numpy as np
import pandas as pd

from constants import DEFAULT_BOOTSTRAP_CONFIDENCE_LEVEL


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
