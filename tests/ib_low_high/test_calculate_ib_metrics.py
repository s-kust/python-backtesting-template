import pandas as pd

from derivative_columns.initial_balance import (
    calculate_ib_breakout_and_breakdown_metrics,
)


def test_calculate_ib_breakout_and_breakdown_metrics_ok(
    df_5_min_with_ib_breakdown_breakout: pd.DataFrame,
    df_ib_high_bt_metrics_res: pd.DataFrame,
    df_ib_low_bd_metrics_res: pd.DataFrame,
) -> None:

    # NOTE The correctness of dataframes df_ib_high_bt_metrics_res
    # and df_ib_low_bd_metrics_res was checked manually.

    ib_low_bd_vals, ib_high_bt_vals = calculate_ib_breakout_and_breakdown_metrics(
        df=df_5_min_with_ib_breakdown_breakout
    )
    ib_low_bd_df = pd.DataFrame(ib_low_bd_vals)
    ib_low_bd_df["Date"] = pd.to_datetime(ib_low_bd_df["Date"])
    pd.testing.assert_frame_equal(ib_low_bd_df, df_ib_low_bd_metrics_res)

    ib_high_bt_df = pd.DataFrame(ib_high_bt_vals)
    ib_high_bt_df["Date"] = pd.to_datetime(ib_high_bt_df["Date"])
    pd.testing.assert_frame_equal(ib_high_bt_df, df_ib_high_bt_metrics_res)

    print(ib_high_bt_df["Val"].describe())
