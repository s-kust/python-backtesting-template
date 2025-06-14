import mock
import pandas as pd
import pytest

from derivative_columns.rsi import _add_rsi_col_initial_validation


@pytest.mark.unit
def test_initial_validation_empty_df(empty_df: pd.DataFrame) -> None:
    """Test validation with an empty DataFrame."""
    with pytest.raises(ValueError, match="empty input DataFrame"):
        _add_rsi_col_initial_validation(df=empty_df, col_name="Close", ma_type="simple")


@pytest.mark.unit
def test_initial_validation_missing_column(spy_df_daily: pd.DataFrame) -> None:
    """Test validation when the specified column is missing."""
    with pytest.raises(ValueError, match="no MissingCol column in input DataFrame"):
        _add_rsi_col_initial_validation(
            df=spy_df_daily, col_name="MissingCol", ma_type="simple"
        )


@pytest.mark.unit
def test_initial_validation_invalid_ma_type(spy_df_daily: pd.DataFrame) -> None:
    """Test validation with an invalid moving average type."""
    with pytest.raises(
        ValueError, match="ma_type='invalid', must be simple or exponential"
    ):
        _add_rsi_col_initial_validation(
            df=spy_df_daily, col_name="Close", ma_type="invalid"
        )


@pytest.mark.unit
def test_initial_validation_rsi_period_less_than_2(
    spy_df_daily: pd.DataFrame,
) -> None:
    """Test validation when RSI_PERIOD is less than 2."""

    # NOTE The constant RSI_PERIOD is patched where it is used,
    # and not in the constants module!

    with mock.patch("derivative_columns.rsi.RSI_PERIOD", 1):
        with pytest.raises(ValueError, match="RSI_PERIOD=1, must be >= 2"):
            _add_rsi_col_initial_validation(
                df=spy_df_daily, col_name="Close", ma_type="simple"
            )

    with mock.patch("derivative_columns.rsi.RSI_PERIOD", 0):
        with pytest.raises(ValueError, match="RSI_PERIOD=0, must be >= 2"):
            _add_rsi_col_initial_validation(
                df=spy_df_daily, col_name="Close", ma_type="simple"
            )


@pytest.mark.unit
def test_initial_validation_valid_inputs(spy_df_daily: pd.DataFrame) -> None:
    """Test validation with valid inputs, should not raise an error."""
    try:
        _add_rsi_col_initial_validation(
            df=spy_df_daily, col_name="Close", ma_type="simple"
        )
        _add_rsi_col_initial_validation(
            df=spy_df_daily, col_name="Open", ma_type="exponential"
        )
    except Exception as e:  # pylint: disable=W0718
        pytest.fail(f"Valid inputs raised an unexpected exception: {e}")
