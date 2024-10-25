from typing import Callable

import pandas as pd

from customizable import add_features_v1_basic


def get_df_with_fwd_ret(
    ohlc_df: pd.DataFrame,
    num_days: int = 24,
    add_features_forecasts_func: Callable = add_features_v1_basic,
) -> pd.DataFrame:

    """
    This function is used if you want to analyze
    forward Close-Close returns rather than trades.

    1. Call add_features_forecasts_func.
    2. Add new column containing forward Close-Close return - ret_{str(num_days)}.
    """
    res = ohlc_df.copy()
    res = add_features_forecasts_func(df=res)
    res[f"Close_fwd_{str(num_days)}"] = res["Close"].shift(-num_days)
    res[f"ret_{str(num_days)}"] = (
        (res[f"Close_fwd_{str(num_days)}"] - res["Close"]) / res["Close"]
    ) * 100
    res[f"ret_{str(num_days)}"] = round(res[f"ret_{str(num_days)}"], 2)
    del res[f"Close_fwd_{str(num_days)}"]
    return res
