import pandas as pd

from constants import FEATURE_COL_NAME_ADVANCED, FEATURE_COL_NAME_BASIC
from derivative_columns.atr import add_atr_col_to_df
from derivative_columns.ma import add_moving_average

MOVING_AVERAGE_N = 200
REQUIRED_DERIVATIVE_COLUMNS_F_V1_BASIC = {"atr_14", f"ma_{MOVING_AVERAGE_N}"}


def add_required_cols_for_f_v1_basic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure that every column listed in REQUIRED_DERIVATIVE_COLUMNS_F_V1_BASIC is present in the DF
    """
    df_columns = df.columns
    internal_df = df.copy()
    if f"ma_{MOVING_AVERAGE_N}" not in df_columns:
        internal_df = add_moving_average(df=internal_df, n=MOVING_AVERAGE_N)
    if "atr_14" not in df_columns:
        if "tr" in df_columns:
            internal_df["atr_14"] = internal_df["tr"].rolling(14).mean()
        else:
            internal_df = add_atr_col_to_df(df=internal_df, n=14, exponential=False)
    return internal_df


def add_features_v1_basic(
    df: pd.DataFrame, atr_multiplier_threshold: int = 6
) -> pd.DataFrame:
    """
    First make sure that all necessary derived columns are present.
    After that, add features_v1_basic columns.
    """

    # NOTE 1.
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

    res = df.copy()

    for col in REQUIRED_DERIVATIVE_COLUMNS_F_V1_BASIC:
        if col not in res.columns:
            res = add_required_cols_for_f_v1_basic(df=res)

    # Customize below

    res[FEATURE_COL_NAME_BASIC] = res["Close"] < res[f"ma_{MOVING_AVERAGE_N}"]

    # NOTE 1
    # At first, a “quick and dirty” analysis of forward returns
    # by feature_basic True and False was launched.
    # See details in README.MD and in run_fwd_return_analysis.py.

    # NOTE 2
    # You may want to skip creating FEATURE_COL_NAME_ADVANCED,
    # limiting yourself to just FEATURE_COL_NAME_BASIC.
    # In this case, in the file get_position_size_main.py
    # change FEATURE_COL_NAME_ADVANCED to FEATURE_COL_NAME_BASIC.

    # FEATURE_COL_NAME_ADVANCED is a HIGHLY_BELOW group of the get_ma_200_relation_label function.
    # It turned out that under these conditions,
    # in subsequent several days, returns are much higher than usually.
    # As an educational example, we launch backtests to check
    # whether this feature is worth using as a signal to take a long position.
    res[FEATURE_COL_NAME_ADVANCED] = (res["ma_200"] - res["Close"]) >= (
        res["atr_14"] * atr_multiplier_threshold
    )

    return res
