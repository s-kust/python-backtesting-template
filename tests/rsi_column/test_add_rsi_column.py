import mock
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from derivative_columns.rsi import add_rsi_column


@pytest.mark.parametrize("ma_type", ["simple", "exponential"])
@pytest.mark.unit
def test_add_rsi_column_basic_calculation_close(
    spy_df_daily: pd.DataFrame, ma_type: str
) -> None:
    """Test basic RSI calculation for the 'Close' column."""

    internal_rsi_period = 14
    # NOTE The constant RSI_PERIOD is patched where it is used,
    # and not in the constants module!
    mock.patch("derivative_columns.rsi.RSI_PERIOD", internal_rsi_period)

    df_with_rsi = add_rsi_column(spy_df_daily, col_name="Close", ma_type=ma_type)

    assert f"RSI_{internal_rsi_period}" in df_with_rsi.columns
    assert isinstance(df_with_rsi[f"RSI_{internal_rsi_period}"], pd.Series)

    rsi_column = df_with_rsi[f"RSI_{internal_rsi_period}"]

    # For simple moving average, assert that the first RSI_PERIOD - 1 values are NaN for SMA
    if ma_type == "simple":
        assert rsi_column.iloc[: internal_rsi_period - 1].isnull().all()

    # Assert all valid RSI values are between 0 and 100
    valid_rsi_values = rsi_column.dropna()
    assert (valid_rsi_values >= 0).all()
    assert (valid_rsi_values <= 100).all()


@pytest.mark.parametrize("col", ["Open", "High", "Low"])
@pytest.mark.parametrize("ma_type", ["simple", "exponential"])
@pytest.mark.unit
def test_add_rsi_column_other_columns(
    spy_df_daily: pd.DataFrame, col: str, ma_type: str
) -> None:
    """Test RSI calculation for 'Open', 'High', 'Low' columns."""

    internal_rsi_period = 14
    # NOTE The constant RSI_PERIOD is patched where it is used,
    # and not in the constants module!
    mock.patch("derivative_columns.rsi.RSI_PERIOD", internal_rsi_period)

    df_with_rsi = add_rsi_column(spy_df_daily, col_name=col, ma_type=ma_type)

    assert f"RSI_{internal_rsi_period}" in df_with_rsi.columns
    rsi_column = df_with_rsi[f"RSI_{internal_rsi_period}"]
    valid_rsi_values = rsi_column.dropna()
    assert (valid_rsi_values >= 0).all()
    assert (valid_rsi_values <= 100).all()


@pytest.mark.unit
def test_add_rsi_column_all_gains(df_all_gains: pd.DataFrame) -> None:
    """Test RSI when prices consistently increase (should be 100)."""

    internal_rsi_period = 3
    # NOTE The constant RSI_PERIOD is patched where it is used,
    # and not in the constants module!
    with mock.patch("derivative_columns.rsi.RSI_PERIOD", internal_rsi_period):
        df_with_rsi = add_rsi_column(df_all_gains, col_name="Close", ma_type="simple")
    rsi_column = df_with_rsi[f"RSI_{internal_rsi_period}"]
    # After initial NaNs, RSI should be 100
    assert (rsi_column.iloc[internal_rsi_period - 1 :].dropna() == 100).all()


@pytest.mark.unit
def test_add_rsi_column_all_losses(df_all_losses: pd.DataFrame) -> None:
    """Test RSI when prices consistently decrease (should be 0)."""

    internal_rsi_period = 3
    # NOTE The constant RSI_PERIOD is patched where it is used,
    # and not in the constants module!
    with mock.patch("derivative_columns.rsi.RSI_PERIOD", internal_rsi_period):
        df_with_rsi = add_rsi_column(df_all_losses, col_name="Close", ma_type="simple")
    rsi_column = df_with_rsi[f"RSI_{internal_rsi_period}"]
    # After initial NaNs, RSI should be 0
    assert (rsi_column.iloc[internal_rsi_period - 1 :].dropna() == 0).all()


@pytest.mark.unit
def test_add_rsi_column_fewer_rows_than_rsi_period(spy_df_daily: pd.DataFrame) -> None:
    """Test RSI calculation with a DataFrame having fewer rows than RSI_PERIOD."""
    internal_rsi_period = 14
    df_short = spy_df_daily.iloc[:5]  # A df with only 5 rows, less than 14
    with mock.patch("derivative_columns.rsi.RSI_PERIOD", internal_rsi_period):
        df_with_rsi = add_rsi_column(df_short, col_name="Close", ma_type="simple")

    assert f"RSI_{internal_rsi_period}" in df_with_rsi.columns
    rsi_column = df_with_rsi[f"RSI_{internal_rsi_period}"]
    # All values should be NaN if there's not enough data for the period.
    assert rsi_column.isnull().all()


@pytest.mark.unit
def test_add_rsi_column_original_df_not_modified(spy_df_daily: pd.DataFrame) -> None:
    """Verify that the original DataFrame is not modified by the function."""
    original_df_copy = spy_df_daily.copy()
    add_rsi_column(spy_df_daily, col_name="Close", ma_type="simple")
    assert_frame_equal(spy_df_daily, original_df_copy)  # Should be identical


@pytest.mark.unit
def test_add_rsi_column_empty_df(empty_df: pd.DataFrame) -> None:
    """Test for empty DataFrame"""
    with pytest.raises(ValueError, match="empty input DataFrame"):
        add_rsi_column(df=empty_df, col_name="Close", ma_type="simple")


@pytest.mark.unit
def test_add_rsi_column_missing_column(spy_df_daily: pd.DataFrame) -> None:
    """Test for missing column validation."""
    with pytest.raises(ValueError, match="no MissingCol column in input DataFrame"):
        add_rsi_column(df=spy_df_daily, col_name="MissingCol", ma_type="simple")


@pytest.mark.unit
def test_add_rsi_column_invalid_ma_type(spy_df_daily: pd.DataFrame) -> None:
    """Test for invalid moving average type validation."""
    with pytest.raises(
        ValueError, match="ma_type='invalid', must be simple or exponential"
    ):
        add_rsi_column(df=spy_df_daily, col_name="Close", ma_type="invalid")


@pytest.mark.unit
def test_add_rsi_column_rsi_period_less_than_2(spy_df_daily: pd.DataFrame) -> None:
    """Test for RSI_PERIOD less than 2 validation."""
    with mock.patch("derivative_columns.rsi.RSI_PERIOD", 1):
        with pytest.raises(ValueError, match="RSI_PERIOD=1, must be >= 2"):
            add_rsi_column(df=spy_df_daily, col_name="Close", ma_type="simple")
