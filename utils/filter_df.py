from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pandas as pd


class RemainingPart(Enum):
    """
    DataFrame remaining part after filtering by date threshold
    """

    BEFORE = "before"
    AFTER = "after"


@dataclass
class FilterParams:
    """
    DataFrame filtering parameters for the function filter_df_by_date
    """

    do_filtering: bool = True
    date_threshold: Optional[str] = None
    remaining_part: RemainingPart = RemainingPart.AFTER


def filter_df_by_date(df: pd.DataFrame, filter_params: FilterParams) -> pd.DataFrame:
    """
    Filter the portion of a dataframe that is before or after a specified date_threshold.
    """
    if filter_params.do_filtering is False:
        return df
    if filter_params.date_threshold is None:
        raise ValueError(
            f"filter_df_by_date: do_filtering is {filter_params.do_filtering}, so date_threshold can't be None"
        )
    if filter_params.remaining_part.value == "after":
        return df.loc[df.index >= filter_params.date_threshold]
    return df.loc[df.index < filter_params.date_threshold]
