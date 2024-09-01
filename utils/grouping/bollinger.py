from typing import Optional, Union

import numpy as np
import pandas as pd

bb_group_1 = "-inf_-2.8"
bb_group_2 = "-2.8_-2.4"
bb_group_3 = "-2.4_-2.0"
bb_group_4 = "-2.0_-1.6"
bb_group_5 = "-1.6_-1.2"
bb_group_6 = "-1.2_-0.8"
bb_group_7 = "-0.8_-0.4"
bb_group_8 = "-0.4_0.0"
bb_group_9 = "0.0_0.4"
bb_group_10 = "0.4_0.8"
bb_group_11 = "0.8_1.2"
bb_group_12 = "1.2_1.6"
bb_group_13 = "1.6_2.0"
bb_group_14 = "2.0_2.4"
bb_group_15 = "2.4_2.8"
bb_group_16 = "2.8_inf"


def get_group_label_forecast_bb(val: Optional[float]) -> Union[str, float]:
    """
    Get group label for continuous feature forecast_bb
    """
    if val is None or pd.isna(val):
        return np.nan
    if val < -2.8:
        return bb_group_1
    if -2.8 <= val < -2.4:
        return bb_group_2
    if -2.4 <= val < -2.0:
        return bb_group_3
    if -2.0 <= val < -1.6:
        return bb_group_4
    if -1.6 <= val < -1.2:
        return bb_group_5
    if -1.2 <= val < -0.8:
        return bb_group_6
    if -0.8 <= val < -0.4:
        return bb_group_7
    if -0.4 <= val < 0:
        return bb_group_8
    if 0 <= val < 0.4:
        return bb_group_9
    if 0.4 <= val < 0.8:
        return bb_group_10
    if 0.8 <= val < 1.2:
        return bb_group_11
    if 1.2 <= val < 1.6:
        return bb_group_12
    if 1.6 <= val < 2.0:
        return bb_group_13
    if 2.0 <= val < 2.4:
        return bb_group_14
    if 2.4 <= val < 2.8:
        return bb_group_15
    return bb_group_16


group_order_bb = {
    bb_group_1: 1,
    bb_group_2: 2,
    bb_group_3: 3,
    bb_group_4: 4,
    bb_group_5: 5,
    bb_group_6: 6,
    bb_group_7: 7,
    bb_group_8: 8,
    bb_group_9: 9,
    bb_group_10: 10,
    bb_group_11: 11,
    bb_group_12: 12,
    bb_group_13: 13,
    bb_group_14: 14,
    bb_group_15: 15,
    bb_group_16: 16,
    "all_data": 17,
}
