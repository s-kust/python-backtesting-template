import pandas as pd

from constants import GROUP_LABELLING_ERROR, RSI_PERIOD


def get_rsi_group_label(row: pd.Series) -> str:
    if (row[f"RSI_{RSI_PERIOD}"] >= 0) and (row[f"RSI_{RSI_PERIOD}"] <= 5):
        return "0_5"
    if (row[f"RSI_{RSI_PERIOD}"] > 5) and (row[f"RSI_{RSI_PERIOD}"] <= 10):
        return "5_10"
    if (row[f"RSI_{RSI_PERIOD}"] > 10) and (row[f"RSI_{RSI_PERIOD}"] <= 15):
        return "10_15"
    if (row[f"RSI_{RSI_PERIOD}"] > 15) and (row[f"RSI_{RSI_PERIOD}"] <= 20):
        return "15_20"
    if (row[f"RSI_{RSI_PERIOD}"] > 20) and (row[f"RSI_{RSI_PERIOD}"] <= 25):
        return "20_25"
    if (row[f"RSI_{RSI_PERIOD}"] > 25) and (row[f"RSI_{RSI_PERIOD}"] <= 30):
        return "25_30"
    if (row[f"RSI_{RSI_PERIOD}"] > 30) and (row[f"RSI_{RSI_PERIOD}"] <= 35):
        return "30_35"
    if (row[f"RSI_{RSI_PERIOD}"] > 35) and (row[f"RSI_{RSI_PERIOD}"] <= 40):
        return "35_40"
    if (row[f"RSI_{RSI_PERIOD}"] > 40) and (row[f"RSI_{RSI_PERIOD}"] <= 45):
        return "40_45"
    if (row[f"RSI_{RSI_PERIOD}"] > 45) and (row[f"RSI_{RSI_PERIOD}"] <= 50):
        return "45_50"
    if (row[f"RSI_{RSI_PERIOD}"] > 50) and (row[f"RSI_{RSI_PERIOD}"] <= 55):
        return "50_55"
    if (row[f"RSI_{RSI_PERIOD}"] > 55) and (row[f"RSI_{RSI_PERIOD}"] <= 60):
        return "55_60"
    if (row[f"RSI_{RSI_PERIOD}"] > 60) and (row[f"RSI_{RSI_PERIOD}"] <= 65):
        return "60_65"
    if (row[f"RSI_{RSI_PERIOD}"] > 65) and (row[f"RSI_{RSI_PERIOD}"] <= 70):
        return "65_70"
    if (row[f"RSI_{RSI_PERIOD}"] > 70) and (row[f"RSI_{RSI_PERIOD}"] <= 75):
        return "70_75"
    if (row[f"RSI_{RSI_PERIOD}"] > 75) and (row[f"RSI_{RSI_PERIOD}"] <= 80):
        return "75_80"
    if (row[f"RSI_{RSI_PERIOD}"] > 80) and (row[f"RSI_{RSI_PERIOD}"] <= 85):
        return "80_85"
    if (row[f"RSI_{RSI_PERIOD}"] > 85) and (row[f"RSI_{RSI_PERIOD}"] <= 90):
        return "85_90"
    if (row[f"RSI_{RSI_PERIOD}"] > 90) and (row[f"RSI_{RSI_PERIOD}"] <= 95):
        return "90_95"
    if (row[f"RSI_{RSI_PERIOD}"] > 95) and (row[f"RSI_{RSI_PERIOD}"] <= 100):
        return "95_100"
    return GROUP_LABELLING_ERROR


group_order_rsi_bounds = {
    "0_5": 1,
    "5_10": 2,
    "10_15": 3,
    "15_20": 4,
    "20_25": 5,
    "25_30": 6,
    "30_35": 7,
    "35_40": 8,
    "40_45": 9,
    "45_50": 10,
    "50_55": 11,
    "55_60": 12,
    "60_65": 13,
    "65_70": 14,
    "70_75": 15,
    "75_80": 16,
    "80_85": 17,
    "85_90": 18,
    "90_95": 19,
    "95_100": 20,
    "all_data": 21,  # all_data row is important, don't miss it
}
