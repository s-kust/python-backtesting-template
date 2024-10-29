import pandas as pd

from features.ma import add_moving_average
from forecast.forecast_bb import add_bb_forecast


def add_features_v1_basic(df: pd.DataFrame) -> pd.DataFrame:

    # NOTE. You can have multiple similar functions
    # with different sets of features and forecasts.
    # Call the function you want to use
    # inside the run_all_tickers function.

    res = df.copy()

    # NOTE better don't remove this line
    res = add_bb_forecast(df=res, col_name="Close")

    # Customize here

    res = add_moving_average(df=res, n=200)

    return res
