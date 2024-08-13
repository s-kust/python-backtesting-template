import pandas as pd


def add_bb_forecast(df: pd.DataFrame, col_name: str = "Close") -> pd.DataFrame:
    # bb_window = 88
    bb_window = 20
    no_of_std = 2.2
    res = df.copy(deep=True)
    res[f"mean_{bb_window}"] = res[col_name].rolling(bb_window).mean()
    res[f"std_{bb_window}"] = res[col_name].rolling(bb_window).std()
    res["BBL"] = res[f"mean_{bb_window}"] - (res[f"std_{bb_window}"] * no_of_std)
    res["BBH"] = res[f"mean_{bb_window}"] + (res[f"std_{bb_window}"] * no_of_std)
    res["forecast_bb"] = (res[col_name] - res[f"mean_{bb_window}"]) / res[
        f"std_{bb_window}"
    ]
    # print(res[f"forecast_bb"].describe())
    return res


def add_bb_forecast_typical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use typical price instead of Close price
    """
    # bb_window = 88
    bb_window = 20

    res = df.copy(deep=True)
    res["Typical"] = (res["High"] + res["Low"] + res["Close"]) / 3
    res[f"mean_{bb_window}"] = res["Typical"].rolling(bb_window).mean()
    res[f"std_{bb_window}"] = res["Typical"].rolling(bb_window).std()

    # no_of_std = 2.2
    # res["BBL"] = res[f"mean_{bb_window}"] - (res[f"std_{bb_window}"] * no_of_std)
    # res["BBH"] = res[f"mean_{bb_window}"] + (res[f"std_{bb_window}"] * no_of_std)

    res["forecast_bb"] = (res["Typical"] - res[f"mean_{bb_window}"]) / res[
        f"std_{bb_window}"
    ]
    # print(res[f"forecast_bb"].describe())
    return res
