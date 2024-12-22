import pandas as pd


def get_ma_200_relation_label(row: pd.Series) -> str:
    """
    Determine where the closing price is
    in relation to moving average 200 days (ma_200)
    and return label.
    """

    if (row["Close"] >= row["ma_200"]) and (
        (row["Close"] - row["ma_200"]) < (row["atr_14"] * 3)
    ):
        return "SLIGHTLY_ABOVE"

    if ((row["Close"] - row["ma_200"]) >= (row["atr_14"] * 3)) and (
        (row["Close"] - row["ma_200"]) < (row["atr_14"] * 6)
    ):
        return "MODERATELY_ABOVE"

    if (row["Close"] - row["ma_200"]) >= (row["atr_14"] * 6):
        return "HIGHLY_ABOVE"

    if (row["Close"] < row["ma_200"]) and (
        (row["ma_200"] - row["Close"]) < (row["atr_14"] * 3)
    ):
        return "SLIGHTLY_BELOW"

    if ((row["ma_200"] - row["Close"]) >= (row["atr_14"] * 3)) and (
        (row["ma_200"] - row["Close"]) < (row["atr_14"] * 6)
    ):
        return "MODERATELY_BELOW"

    if (row["ma_200"] - row["Close"]) >= (row["atr_14"] * 6):
        return "HIGHLY_BELOW"

    # just in case, should never occur
    return "N/A"
