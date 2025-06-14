from unittest import mock

import pandas as pd
import pytest

from derivative_columns.min_max import (
    _ensure_required_cols_min_max_in_df,
    _fill_is_min_max,
)

# --- Unit Tests for _fill_is_min_max ---


@pytest.mark.unit
def test_fill_is_min_max_empty_df(empty_df: pd.DataFrame) -> None:
    df = _ensure_required_cols_min_max_in_df(df=empty_df)
    result_df = _fill_is_min_max(df, col_name="Close", atr_smoothing_n=14)
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


@pytest.mark.unit
def test_fill_is_min_max_simple_uptrend(basic_ohlc_df_daily: pd.DataFrame) -> None:
    """Test with data that clearly shows a continuous uptrend."""
    df = basic_ohlc_df_daily.copy()
    # Adjust Close to be a strong uptrend
    df["Close"] = [100, 105, 110, 115, 120]
    df["atr_14"] = 1.0  # Set ATR_N to a constant small value

    # Mock constant to control ATR_MULTIPLIER for predictable behavior
    with mock.patch("derivative_columns.min_max.ATR_MULTIPLIER", 2.5):
        df = _ensure_required_cols_min_max_in_df(df=df)
        assert df["atr_14"].all() == 1.0  # just in case
        result_df = _fill_is_min_max(df, col_name="Close", atr_smoothing_n=14)

    # The search for extremes starts from the minimum. The series grows keeps growing.
    # Expected the first value to be detected as a minimum. No maximum found.
    expected_is_min = pd.Series(
        [True, False, False, False, False], index=df.index, dtype=bool
    )
    expected_is_max = pd.Series(
        [False, False, False, False, False], index=df.index, dtype=bool
    )
    # The last point might be considered a max
    # However, by logic, it waits for a drop.
    # Without a drop, the last point is just a candidate.
    pd.testing.assert_series_equal(
        result_df["is_min"], expected_is_min, check_names=False
    )
    pd.testing.assert_series_equal(
        result_df["is_max"], expected_is_max, check_names=False
    )


@pytest.mark.unit
def test_fill_is_min_max_simple_downtrend(basic_ohlc_df_daily: pd.DataFrame) -> None:
    """Test with data that clearly shows a continuous downtrend."""
    df = basic_ohlc_df_daily.copy()
    # Adjust Close to be a strong downtrend
    df["Close"] = [120, 115, 110, 105, 100]
    df["atr_14"] = 1.0  # Set ATR_N to a constant small value

    # Mock constant to control ATR_MULTIPLIER for predictable behavior
    with mock.patch("derivative_columns.min_max.ATR_MULTIPLIER", 2.5):
        df = _ensure_required_cols_min_max_in_df(df=df)
        assert df["atr_14"].all() == 1.0  # just in case
        result_df = _fill_is_min_max(df, col_name="Close", atr_smoothing_n=14)

    # The search for extremes starts from the minimum. The series keeps falling.
    # It is expected to find neither minimums nor maximums.
    expected_is_min = pd.Series(
        [False, False, False, False, False], index=df.index, dtype=bool
    )
    expected_is_max = pd.Series(
        [False, False, False, False, False], index=df.index, dtype=bool
    )

    pd.testing.assert_series_equal(
        result_df["is_min"], expected_is_min, check_names=False
    )
    pd.testing.assert_series_equal(
        result_df["is_max"], expected_is_max, check_names=False
    )


@pytest.mark.unit
def test_fill_is_min_max_alternating_min_max(basic_ohlc_df_daily: pd.DataFrame) -> None:
    """Test with data that forms a clear zig-zag pattern."""
    df = basic_ohlc_df_daily.copy()
    df["Close"] = [100, 110, 102, 112, 105]  # Max, Min, Max, Min pattern
    df["atr_14"] = 1.0  # Set ATR_N to a constant small value

    # Mock constant to control ATR_MULTIPLIER for predictable behavior
    with mock.patch("derivative_columns.min_max.ATR_MULTIPLIER", 2.5):
        df = _ensure_required_cols_min_max_in_df(df=df)
        assert df["atr_14"].all() == 1.0  # just in case
        result_df = _fill_is_min_max(df, col_name="Close", atr_smoothing_n=14)

    # The search for extremes starts from the minimum.
    expected_is_min = pd.Series(
        [True, False, True, False, False], index=df.index, dtype=bool
    )
    expected_is_max = pd.Series(
        [False, True, False, True, False], index=df.index, dtype=bool
    )

    pd.testing.assert_series_equal(
        result_df["is_min"], expected_is_min, check_names=False
    )
    pd.testing.assert_series_equal(
        result_df["is_max"], expected_is_max, check_names=False
    )


@pytest.mark.unit
def test_fill_is_min_max_flat_price(basic_ohlc_df_daily: pd.DataFrame) -> None:
    """Test how it handles periods where the price remains relatively flat."""
    df = basic_ohlc_df_daily.copy()
    df["Close"] = [100.1, 100.3, 100.15, 100.19, 100.36]
    df["atr_14"] = 1.0  # Set ATR_N to a constant small value

    # Mock constant to control ATR_MULTIPLIER for predictable behavior
    with mock.patch("derivative_columns.min_max.ATR_MULTIPLIER", 2.5):
        df = _ensure_required_cols_min_max_in_df(df=df)
        assert df["atr_14"].all() == 1.0  # just in case
        result_df = _fill_is_min_max(df, col_name="Close", atr_smoothing_n=14)

    expected_is_min = pd.Series([False] * 5, index=df.index, dtype=bool)
    expected_is_max = pd.Series([False] * 5, index=df.index, dtype=bool)

    pd.testing.assert_series_equal(
        result_df["is_min"], expected_is_min, check_names=False
    )
    pd.testing.assert_series_equal(
        result_df["is_max"], expected_is_max, check_names=False
    )


@pytest.mark.unit
def test_fill_is_min_max_different_col_name(basic_ohlc_df_daily: pd.DataFrame) -> None:
    """Test with a different column name."""
    df = basic_ohlc_df_daily.copy()
    df["CustomPrice"] = [100, 110, 102, 112, 105]  # Max, Min, Max, Min pattern
    df["atr_14"] = 1.0  # Set ATR_N to a constant small value

    # Mock constant to control ATR_MULTIPLIER for predictable behavior
    with mock.patch("derivative_columns.min_max.ATR_MULTIPLIER", 2.5):
        df = _ensure_required_cols_min_max_in_df(df=df)
        assert df["atr_14"].all() == 1.0  # just in case
        result_df = _fill_is_min_max(df, col_name="CustomPrice", atr_smoothing_n=14)

    # The search for extremes starts from the minimum.
    expected_is_min = pd.Series(
        [True, False, True, False, False], index=df.index, dtype=bool
    )
    expected_is_max = pd.Series(
        [False, True, False, True, False], index=df.index, dtype=bool
    )

    pd.testing.assert_series_equal(
        result_df["is_min"], expected_is_min, check_names=False
    )
    pd.testing.assert_series_equal(
        result_df["is_max"], expected_is_max, check_names=False
    )


@pytest.mark.unit
def test_fill_is_min_max_changed_start_date(basic_ohlc_df_daily: pd.DataFrame) -> None:
    """Verify it continues correctly if start_date is not the beginning of the DataFrame."""
    df = basic_ohlc_df_daily.copy()
    df["CustomPrice"] = [100, 110, 102, 112, 105]  # Max, Min, Max, Min pattern
    df["atr_14"] = 1.0  # Set ATR_N to a constant small value

    # Mock constant to control ATR_MULTIPLIER for predictable behavior
    with mock.patch("derivative_columns.min_max.ATR_MULTIPLIER", 2.5):
        df = _ensure_required_cols_min_max_in_df(df=df)
        assert df["atr_14"].all() == 1.0  # just in case
        # Manually set a max at the beginning
        df.loc["2023-01-01", "is_max"] = (
            True  # Pretend this was already a max, although it's wrong
        )
        result_df = _fill_is_min_max(df, col_name="CustomPrice", atr_smoothing_n=14)

    # The search for extremes starts from the minimum.
    expected_is_min = pd.Series(
        [False, False, True, False, False], index=df.index, dtype=bool
    )
    expected_is_max = pd.Series(
        [True, False, False, True, False], index=df.index, dtype=bool
    )

    pd.testing.assert_series_equal(
        result_df["is_min"], expected_is_min, check_names=False
    )
    pd.testing.assert_series_equal(
        result_df["is_max"], expected_is_max, check_names=False
    )


@pytest.mark.unit
def test_fill_is_min_max_edge_case_single_point(single_row_df: pd.DataFrame) -> None:
    """Test behavior with a single data point."""
    df = single_row_df.copy()
    df["atr_14"] = 1.0  # Set ATR_N to a constant small value

    # Mock constant to control ATR_MULTIPLIER for predictable behavior
    with mock.patch("derivative_columns.min_max.ATR_MULTIPLIER", 2.5):
        df = _ensure_required_cols_min_max_in_df(df=df)
        assert df["atr_14"].all() == 1.0  # just in case
        result_df = _fill_is_min_max(df, col_name="Close", atr_smoothing_n=14)

    # The search for extremes starts from the minimum.
    expected_is_min = pd.Series([False], index=df.index, dtype=bool)
    expected_is_max = pd.Series([False], index=df.index, dtype=bool)

    pd.testing.assert_series_equal(
        result_df["is_min"], expected_is_min, check_names=False
    )
    pd.testing.assert_series_equal(
        result_df["is_max"], expected_is_max, check_names=False
    )
