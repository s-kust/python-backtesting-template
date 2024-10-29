import pandas as pd

from features.ma import add_moving_average
from forecast.forecast_bb import add_bb_forecast


def add_features_v1_basic(
    df: pd.DataFrame, atr_multiplier_threshold: int = 6
) -> pd.DataFrame:

    # NOTE 1.
    # You can have multiple similar functions
    # with different sets of features and forecasts.

    # NOTE 2
    # atr_multiplier_threshold is an example of a parameter
    # that you may want to optimize.
    # functools.partial is used for that.

    # NOTE 3.
    # You already have tr (True Range) column in input DF.
    # For adding Average True Range, consider something like this:
    # res['atr_14'] = res['tr'].rolling(14).mean()

    res = df.copy()

    # NOTE better don't remove this line
    res = add_bb_forecast(df=res, col_name="Close")

    # Customize below

    MOVING_AVERAGE_N = 200

    # add ma_200 columns
    res = add_moving_average(df=res, n=MOVING_AVERAGE_N)

    res["atr_14"] = res["tr"].rolling(14).mean()
    res["feature_basic"] = res["Close"] < res[f"ma_{MOVING_AVERAGE_N}"]

    # At first, a “quick and dirty” analysis of forward returns was launched.
    # See details in README.MD and in run_fwd_return_analysis.py.
    # It's a HIGHLY_BELOW group of the _get_ma_200_relation_label function.
    # It turned out that under these conditions,
    # in subsequent several days, returns are much higher than usually.
    # As an educational example, we launch backtests to check
    # whether this feature is worth using as a signal to take a long position.
    res["feature_advanced"] = (res["ma_200"] - res["Close"]) >= (
        res["atr_14"] * atr_multiplier_threshold
    )

    # enlist the columns added here in required_feature_columns,
    # see run_fwd_ret_analysis_ma_200.py

    return res
