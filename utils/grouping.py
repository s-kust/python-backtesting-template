from typing import Callable, Optional, Union

import numpy as np
import pandas as pd


def get_group_label_adx(val: Optional[float]) -> Union[str, float]:
    if val is None or pd.isna(val):
        return np.nan
    if val < 10:
        return "0_10"
    if val >= 10 and val < 21:
        return "10_21"
    if val >= 21 and val < 31:
        return "21_31"
    if val >= 31 and val < 41:
        return "31_41"
    return "41_100"


def get_group_label_tr_delta(val: Optional[float]) -> Union[str, float]:
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


mtum_group_1 = "abs_less_02"
mtum_group_2 = "abs_02_04"
mtum_group_3 = "abs_04_06"
mtum_group_4 = "abs_06_08"
mtum_group_5 = "abs_08_1"
mtum_group_6 = "abs_1_12"
mtum_group_7 = "abs_12_14"
mtum_group_8 = "abs_14_16"
mtum_group_9 = "abs_16_18"
mtum_group_10 = "abs_18_2"
mtum_group_11 = "abs_above_2"


def get_group_label_mtum(val: Optional[float]) -> Union[str, float]:
    if val is None or pd.isna(val):
        return np.nan
    if abs(val) < 0.2:
        return mtum_group_1
    if abs(val) >= 0.2 and abs(val) < 0.4:
        return mtum_group_2
    if abs(val) >= 0.4 and abs(val) < 0.6:
        return mtum_group_3
    if abs(val) >= 0.6 and abs(val) < 0.8:
        return mtum_group_4
    if abs(val) >= 0.8 and abs(val) < 1:
        return mtum_group_5
    if abs(val) >= 1 and abs(val) < 1.2:
        return mtum_group_6
    if abs(val) >= 1.2 and abs(val) < 1.4:
        return mtum_group_7
    if abs(val) >= 1.4 and abs(val) < 1.6:
        return mtum_group_8
    if abs(val) >= 1.6 and abs(val) < 1.8:
        return mtum_group_9
    if abs(val) >= 1.8 and abs(val) < 2:
        return mtum_group_10
    return mtum_group_11


group_order_mtum = {
    mtum_group_1: 1,
    mtum_group_2: 2,
    mtum_group_3: 3,
    mtum_group_4: 4,
    mtum_group_5: 5,
    mtum_group_6: 6,
    mtum_group_7: 7,
    mtum_group_8: 8,
    mtum_group_9: 9,
    mtum_group_10: 10,
    mtum_group_11: 11,
    "all_data": 12,
}

group_order_adx = {
    "0_10": 1,
    "10_21": 2,
    "21_31": 3,
    "31_41": 4,
    "41_100": 5,
    "all_data": 6,
}

group_order_tr_delta = {
    "0_0.49": 1,
    "0.49_0.56": 2,
    "0.56_0.91": 3,
    "0.91_1.87": 4,
    "1.87_2.72": 5,
    "2.72_inf": 6,
    "all_data": 7,
}

bb_group_1 = "-inf_-28"
bb_group_2 = "-28_-24"
bb_group_3 = "-24_-20"
bb_group_4 = "-20_-16"
bb_group_5 = "-16_-12"
bb_group_6 = "-12_-8"
bb_group_7 = "-8_-4"
bb_group_8 = "-4_0"
bb_group_9 = "0_4"
bb_group_10 = "4_8"
bb_group_11 = "8_12"
bb_group_12 = "12_16"
bb_group_13 = "16_20"
bb_group_14 = "20_24"
bb_group_15 = "24_28"
bb_group_16 = "28_inf"


def get_group_label_forecast_bb(val: Optional[float]) -> Union[str, float]:
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


def add_group_col(
    df: pd.DataFrame,
    grouping_col_name: str,
    new_col_name: str,
    get_label_for_group: Callable,
) -> pd.DataFrame:
    res = df.copy(deep=True)
    res[new_col_name] = res[grouping_col_name].apply(get_label_for_group)
    return res
