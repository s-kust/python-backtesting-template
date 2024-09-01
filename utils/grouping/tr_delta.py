from typing import Optional, Union

import numpy as np
import pandas as pd

group_order_tr_delta = {
    "0_0.49": 1,
    "0.49_0.56": 2,
    "0.56_0.91": 3,
    "0.91_1.87": 4,
    "1.87_2.72": 5,
    "2.72_inf": 6,
    "all_data": 7,
}


def get_group_label_tr_delta(val: Optional[float]) -> Union[str, float]:
    """
    Get group label for continuous feature tr_delta
    """
    if val is None or pd.isna(val):
        return np.nan
    if val < 0.49:
        return "0_0.49"
    if val >= 0.49 and val < 0.56:
        return "0.49_0.56"
    if val >= 0.56 and val < 0.91:
        return "0.56_0.91"
    if val >= 0.91 and val < 1.87:
        return "0.91_1.87"
    if val >= 1.87 and val < 2.72:
        return "1.87_2.72"
    return "2.72_inf"
