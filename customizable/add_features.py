import pandas as pd

from features.ma import add_moving_average
from forecast.forecast_bb import add_bb_forecast


def add_features_v1_basic(df: pd.DataFrame) -> pd.DataFrame:

    # NOTE 1.
    # You can have multiple similar functions
    # with different sets of features and forecasts.

    # NOTE 2.
    # You already have tr (True Range) column in input DF.
    # For adding Average True Range, consider something like this:
    # res['atr_14'] = res['tr'].rolling(14).mean()

    res = df.copy()

    # NOTE better don't remove this line
    res = add_bb_forecast(df=res, col_name="Close")

    # Customize here

    MOVING_AVERAGE_N = 200

    # add ma_200 columns
    res = add_moving_average(df=res, n=MOVING_AVERAGE_N)

    res["atr_14"] = res["tr"].rolling(14).mean()
    res["feature"] = res["Close"] < res[f"ma_{MOVING_AVERAGE_N}"]

    # enlist the columns added here in required_feature_columns,
    # see run_fwd_ret_analysis_ma_200.py

    return res
