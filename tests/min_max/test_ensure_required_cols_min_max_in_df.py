from unittest.mock import ANY, MagicMock

import pandas as pd
import pytest

from derivative_columns.min_max import _ensure_required_cols_min_max_in_df

# --- Unit Tests for _ensure_required_cols_min_max_in_df ---


@pytest.mark.unit
def test_ensure_required_cols_all_present(
    basic_ohlc_df_daily: pd.DataFrame, mock_add_atr_col_to_df: MagicMock
) -> None:
    """
    Manually add all required columns before calling _ensure_required_cols_min_max_in_df.
    Ensure no new columns are added and existing columns are not modified.
    """
    df = basic_ohlc_df_daily.copy()
    # Manually add all required columns
    df["atr_14"] = 1.0
    df["is_min"] = False
    df["is_max"] = False
    df["last_known_min_date"] = None
    df["last_known_max_date"] = None
    df["prev_known_min_date"] = None
    df["prev_known_max_date"] = None
    df["last_known_min_val"] = None
    df["last_known_max_val"] = None
    df["prev_known_min_val"] = None
    df["prev_known_max_val"] = None

    original_df_cols = df.columns.tolist()
    result_df = _ensure_required_cols_min_max_in_df(df, atr_smoothing_n=14)

    pd.testing.assert_frame_equal(result_df, df)  # Should be identical
    assert result_df.columns.tolist() == original_df_cols  # No new columns
    mock_add_atr_col_to_df.assert_not_called()  # ATR function should not be called


@pytest.mark.unit
def test_ensure_required_cols_missing_atr(
    basic_ohlc_df_daily: pd.DataFrame, mock_add_atr_col_to_df: MagicMock
) -> None:
    """Verify that add_atr_col_to_df is called and the ATR column is added."""
    mock_add_atr_col_to_df.return_value = basic_ohlc_df_daily.assign(
        atr_14=1.5
    )  # Mock its return value
    df_missing_atr = basic_ohlc_df_daily.copy()
    result_df = _ensure_required_cols_min_max_in_df(df_missing_atr, atr_smoothing_n=14)

    mock_add_atr_col_to_df.assert_called_once_with(df=ANY, n=14, exponential=False)
    assert "atr_14" in result_df.columns
    # Check that other expected columns are also added
    assert "is_min" in result_df.columns
    assert result_df["is_min"].dtype == bool  # Check dtype for bool columns
    assert result_df["is_min"].all() == False  # All should be False initially


@pytest.mark.unit
def test_ensure_required_cols_missing_some_min_max(
    basic_ohlc_df_daily: pd.DataFrame, mock_add_atr_col_to_df: MagicMock
) -> None:
    """Verify that only the missing columns are added with correct default values."""
    df_missing = basic_ohlc_df_daily.copy()
    df_missing["atr_14"] = 1.0  # Pretend ATR is already there
    # Remove some columns to test
    df_missing = df_missing.drop(
        columns=["is_min", "last_known_max_date"], errors="ignore"
    )

    result_df = _ensure_required_cols_min_max_in_df(df_missing, atr_smoothing_n=14)

    assert "is_min" in result_df.columns
    assert result_df["is_min"].dtype == bool
    assert result_df["is_min"].all() == False

    assert "last_known_max_date" in result_df.columns
    assert result_df["last_known_max_date"].isnull().all()  # All should be None/NaT

    # Ensure other existing columns are preserved
    assert "Close" in result_df.columns
    pd.testing.assert_series_equal(result_df["Close"], basic_ohlc_df_daily["Close"])
    mock_add_atr_col_to_df.assert_not_called()  # ATR was already there


@pytest.mark.unit
def test_ensure_required_cols_empty_df(
    empty_df: pd.DataFrame, mock_add_atr_col_to_df: MagicMock
) -> None:
    """Test its behavior with an empty DataFrame."""
    mock_add_atr_col_to_df.return_value = empty_df.assign(
        atr_14=pd.Series(dtype=float)
    )  # Mock its return for empty DF
    result_df = _ensure_required_cols_min_max_in_df(empty_df, atr_smoothing_n=14)

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
    mock_add_atr_col_to_df.assert_called_once()


@pytest.mark.unit
def test_ensure_required_cols_original_df_not_modified(
    basic_ohlc_df_daily: pd.DataFrame, mock_add_atr_col_to_df: MagicMock
) -> None:
    """Verify that the original DataFrame passed as input is not modified."""
    mock_add_atr_col_to_df.return_value = basic_ohlc_df_daily.assign(atr_14=1.0)
    original_df_copy = basic_ohlc_df_daily.copy()  # Make a copy to compare against
    _ensure_required_cols_min_max_in_df(basic_ohlc_df_daily, atr_smoothing_n=14)
    pd.testing.assert_frame_equal(basic_ohlc_df_daily, original_df_copy)
