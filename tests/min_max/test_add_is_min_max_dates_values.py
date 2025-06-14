import pandas as pd
import pytest

from derivative_columns.min_max import ATR_SMOOTHING_N, add_is_min_max_dates_values


@pytest.mark.e2e
def test_add_is_min_max_dates_values_end_to_end_spy_df(
    spy_df_daily: pd.DataFrame,
) -> None:
    """
    End-to-end test using the real SPY daily data.
    This test primarily checks that the function runs without errors and
    produces a DataFrame with the expected columns and types.
    """
    # Ensure ATR_SMOOTHING_N is within reasonable bounds for the SPY df
    if len(spy_df_daily) < ATR_SMOOTHING_N:
        pytest.skip(
            "SPY DataFrame too short for ATR calculation with default ATR_SMOOTHING_N"
        )

    result_df = add_is_min_max_dates_values(spy_df_daily, col_name="Close")

    # Assertions for expected columns
    expected_cols = [
        "atr_14",
        "is_min",
        "is_max",
        "last_known_min_date",
        "last_known_max_date",
        "prev_known_min_date",
        "prev_known_max_date",
        "last_known_min_val",
        "last_known_max_val",
        "prev_known_min_val",
        "prev_known_max_val",
    ]
    for col in expected_cols:
        assert col in result_df.columns

    # Assert types
    assert result_df["is_min"].dtype == bool
    assert result_df["is_max"].dtype == bool

    # Basic sanity checks (e.g., no NaNs in is_min/is_max after processing)
    assert not result_df["is_min"].isnull().any()
    assert not result_df["is_max"].isnull().any()

    # Check that at least some mins/maxes are identified
    assert result_df["is_min"].any()
    assert result_df["is_max"].any()


@pytest.mark.unit
def test_add_is_min_max_dates_values_empty_df(empty_df: pd.DataFrame) -> None:
    """Test the full function with an empty DataFrame."""
    result_df = add_is_min_max_dates_values(empty_df, col_name="Close")
    # Check if all columns are added and empty with correct dtypes
    expected_cols = [
        "atr_14",
        "is_min",
        "is_max",
        "last_known_min_date",
        "last_known_max_date",
        "prev_known_min_date",
        "prev_known_max_date",
        "last_known_min_val",
        "last_known_max_val",
        "prev_known_min_val",
        "prev_known_max_val",
    ]
    assert all(col in result_df.columns for col in expected_cols)
    assert result_df.empty
    assert result_df["is_min"].dtype == bool
