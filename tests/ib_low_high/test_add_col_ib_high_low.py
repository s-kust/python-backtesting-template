import pandas as pd
import pytest

from derivative_columns.initial_balance import add_col_ib_high_low


def test_add_col_ib_high_low_ok(
    spy_df_5_min: pd.DataFrame, df_5_min_with_ib: pd.DataFrame
) -> None:
    """
    add_col_ib_high_low - test main OK case.
    df_5_min_with_ib - checked manually that it's OK
    """
    res = add_col_ib_high_low(df=spy_df_5_min)
    assert "ib_high" in res.columns
    assert "ib_low" in res.columns
    pd.testing.assert_frame_equal(res, df_5_min_with_ib)


def test_add_col_ib_high_low_no_datetime_index_in_df(empty_df: pd.DataFrame) -> None:
    """
    Run add_col_ib_high_low with empty DF as input.
    """
    with pytest.raises(ValueError) as exc_info:
        add_col_ib_high_low(df=empty_df)
    exc_info_value = str(exc_info.value)
    assert "input DF doesn't have DateTime index" in exc_info_value
    assert "'inferred_interval_minutes': 999" in exc_info_value


def test_add_col_ib_high_low_daily_df(spy_df_daily: pd.DataFrame) -> None:
    """
    Run add_col_ib_high_low with daily OHLC DF as input.
    It has wrong bars interval 1440 min, i.e. 24 h.
    """
    with pytest.raises(ValueError) as exc_info:
        add_col_ib_high_low(df=spy_df_daily)
    exc_info_value = str(exc_info.value)
    assert (
        "add_col_ib_high_low: input DF bars interval = 1440 min, should be 5, 15, 30, 45, 60 minutes"
        in exc_info_value
    )
