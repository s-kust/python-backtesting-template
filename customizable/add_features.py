import pandas as pd

from derivative_columns.ma import add_moving_average


def add_features_v1_basic(
    df: pd.DataFrame, atr_multiplier_threshold: int = 6
) -> pd.DataFrame:

    # NOTE 1.
    # You can have multiple similar functions
    # with different sets of features and forecasts.
    # The function must be passed as a add_feature_cols_func parameter
    # when creating an instance of the TickersData class.
    # See the examples in the files run_fwd_return_analysis.py,
    # run_strategy_main_simple.py, and run_strategy_main_optimize.py.
    # The most advanced and valuable is the example
    # in the run_strategy_main_optimize.py file.

    # NOTE 2
    # atr_multiplier_threshold is an example of a parameter
    # that you may want to optimize.
    # functools.partial is used for that.
    # See the example in the run_strategy_main_optimize.py file.

    # NOTE 3.
    # You already have tr (True Range) column in input DF.
    # For adding Average True Range, consider something like this:
    # res['atr_14'] = res['tr'].rolling(14).mean()

    res = df.copy()

    # Customize below

    # NOTE
    # In the following example, the derived columns are
    # moving average (ma_200) and Average True Range (atr_14),
    # Feature_basic and feature_advanced the features created based on them.

    MOVING_AVERAGE_N = 200

    # add ma_200 column
    res = add_moving_average(df=res, n=MOVING_AVERAGE_N)

    res["atr_14"] = res["tr"].rolling(14).mean()
    res["feature_basic"] = res["Close"] < res[f"ma_{MOVING_AVERAGE_N}"]

    # NOTE
    # At first, a “quick and dirty” analysis of forward returns
    # by feature_basic True and False was launched.
    # See details in README.MD and in run_fwd_return_analysis.py.

    # feature_advanced is a HIGHLY_BELOW group of the get_ma_200_relation_label function.
    # It turned out that under these conditions,
    # in subsequent several days, returns are much higher than usually.
    # As an educational example, we launch backtests to check
    # whether this feature is worth using as a signal to take a long position.
    res["feature_advanced"] = (res["ma_200"] - res["Close"]) >= (
        res["atr_14"] * atr_multiplier_threshold
    )

    # enlist the columns created above in required_feature_columns,
    # see run_fwd_ret_analysis_ma_200.py

    return res
