import pandas as pd
import pytest

from derivative_columns.initial_balance import check_initial_balance_breach


def test_check_initial_balance_breach_ok(
    df_5_min_with_ib: pd.DataFrame, df_5_min_with_ib_breakdown_breakout: pd.DataFrame
) -> None:
    res = check_initial_balance_breach(df=df_5_min_with_ib)
    assert "ib_high_bt" in res.columns
    assert "ib_low_bd" in res.columns
    assert "ib_high" in res.columns
    assert "ib_low" in res.columns
    pd.testing.assert_frame_equal(res, df_5_min_with_ib_breakdown_breakout)


def test_check_initial_balance_breach_no_datetime_index_in_df(
    empty_df: pd.DataFrame,
) -> None:
    """
    Run check_initial_balance_breach with empty DF as input.
    """
    with pytest.raises(ValueError) as exc_info:
        check_initial_balance_breach(df=empty_df)
    exc_info_value = str(exc_info.value)
    assert "input DF doesn't have DateTime index" in exc_info_value
    assert "'inferred_interval_minutes': 999" in exc_info_value


def test_check_initial_balance_breach_daily_df(spy_df_daily: pd.DataFrame) -> None:
    """
    Run check_initial_balance_breach with daily OHLC DF as input.
    It has wrong bars interval 1440 min, i.e. 24 h.
    """
    with pytest.raises(ValueError) as exc_info:
        check_initial_balance_breach(df=spy_df_daily)
    exc_info_value = str(exc_info.value)
    assert (
        "check_initial_balance_breach: input DF bars interval = 1440 min, should be 5, 15, 30, 45, 60 minutes"
        in exc_info_value
    )
