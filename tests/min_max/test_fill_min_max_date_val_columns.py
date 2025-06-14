import pandas as pd
import pytest

from derivative_columns.min_max import (
    _ensure_required_cols_min_max_in_df,
    _fill_min_max_date_val_columns,
)


@pytest.mark.unit
def test_fill_min_max_date_val_no_is_min_max(basic_ohlc_df_daily: pd.DataFrame) -> None:
    """Ensure all last_known_*** and prev_known_*** columns remain None when no min/max."""
    df = basic_ohlc_df_daily.copy()
    df = _ensure_required_cols_min_max_in_df(
        df
    )  # Ensure all columns exist and are None/False

    result_df = _fill_min_max_date_val_columns(df, col_name="Close")

    # Check that all date/val columns are still None/NaT
    for col_suffix in ["min", "max"]:
        assert result_df[f"last_known_{col_suffix}_date"].isnull().all()
        assert result_df[f"prev_known_{col_suffix}_date"].isnull().all()
        assert result_df[f"last_known_{col_suffix}_val"].isnull().all()
        assert result_df[f"prev_known_{col_suffix}_val"].isnull().all()


@pytest.mark.unit
def test_fill_min_max_date_val_single_min(df_for_date_val_fill: pd.DataFrame) -> None:
    """Verify last_known_min_date and value are correctly filled, and prev_known_*** remain None."""
    df = df_for_date_val_fill.copy()

    # Pretend there is only one min at '2023-01-02' with value 90
    df["is_min"] = pd.Series(
        [False, True, False, False, False, False, False], index=df.index, dtype=bool
    )
    df["is_max"] = False  # No maxes

    result_df = _fill_min_max_date_val_columns(df, col_name="Close")

    # After '2023-01-02'
    assert result_df.loc["2023-01-03", "last_known_min_date"] == pd.to_datetime(
        "2023-01-02"
    )
    assert result_df.loc["2023-01-03", "last_known_min_val"] == 90
    assert pd.isna(result_df.loc["2023-01-03", "prev_known_min_date"])
    assert pd.isna(result_df.loc["2023-01-03", "prev_known_min_val"])

    # For subsequent dates, last_known_min should remain '2023-01-02'
    assert result_df.loc["2023-01-07", "last_known_min_date"] == pd.to_datetime(
        "2023-01-02"
    )
    assert result_df.loc["2023-01-07", "last_known_min_val"] == 90

    # Max columns should remain None/NaT
    assert result_df["last_known_max_date"].isnull().all()


@pytest.mark.unit
def test_fill_min_max_date_val_single_max(df_for_date_val_fill: pd.DataFrame) -> None:
    """Verify last_known_min_date and value are correctly filled, and prev_known_*** remain None."""
    df = df_for_date_val_fill.copy()

    # Pretend there is only one max at '2023-01-03' with value 110
    df["is_max"] = pd.Series(
        [False, False, True, False, False, False, False], index=df.index, dtype=bool
    )
    df["is_min"] = False  # No maxes

    result_df = _fill_min_max_date_val_columns(df, col_name="Close")

    # After '2023-01-02'
    assert result_df.loc["2023-01-04", "last_known_max_date"] == pd.to_datetime(
        "2023-01-03"
    )
    assert result_df.loc["2023-01-04", "last_known_max_val"] == 110
    assert pd.isna(result_df.loc["2023-01-04", "prev_known_max_date"])
    assert pd.isna(result_df.loc["2023-01-04", "prev_known_max_val"])

    # For subsequent dates, last_known_min should remain '2023-01-02'
    assert result_df.loc["2023-01-07", "last_known_max_date"] == pd.to_datetime(
        "2023-01-03"
    )
    assert result_df.loc["2023-01-07", "last_known_max_val"] == 110

    # Max columns should remain None/NaT
    assert result_df["last_known_min_date"].isnull().all()


@pytest.mark.unit
def test_fill_min_max_date_val_alternating_min_max(
    df_for_date_val_fill: pd.DataFrame,
) -> None:
    """Test a sequence like min, max, min, max, ensuring correct updates."""
    # df_for_date_val_fill already has alternating mins/maxes setup
    df = df_for_date_val_fill.copy()

    result_df = _fill_min_max_date_val_columns(df, col_name="Close")

    # Expected values for '2023-01-05' (after min at 01-04, max at 01-03)
    # latest_min_date: 2023-01-04 (val 85)
    # prev_min_date: 2023-01-02 (val 90)
    # latest_max_date: 2023-01-03 (val 110)
    # prev_max_date: None

    assert result_df.loc["2023-01-05", "last_known_min_date"] == pd.to_datetime(
        "2023-01-04"
    )
    assert result_df.loc["2023-01-05", "last_known_min_val"] == 85.0
    assert result_df.loc["2023-01-05", "prev_known_min_date"] == pd.to_datetime(
        "2023-01-02"
    )
    assert result_df.loc["2023-01-05", "prev_known_min_val"] == 90.0
    assert result_df.loc["2023-01-05", "last_known_max_date"] == pd.to_datetime(
        "2023-01-03"
    )
    assert result_df.loc["2023-01-05", "last_known_max_val"] == 110.0
    assert pd.isna(
        result_df.loc["2023-01-05", "prev_known_max_date"]
    )  # Only one max seen before 01-05
    assert pd.isna(result_df.loc["2023-01-05", "prev_known_max_val"])

    # Expected values for '2023-01-07' (after min at 01-06, max at 01-07)
    # latest_min_date: 2023-01-06 (val 95)
    # prev_min_date: 2023-01-04 (val 85)
    # latest_max_date: 2023-01-05 (val 120)
    # prev_max_date: 2023-01-03 (val 110)

    assert result_df.loc["2023-01-07", "last_known_min_date"] == pd.to_datetime(
        "2023-01-06"
    )
    assert result_df.loc["2023-01-07", "last_known_min_val"] == 95.0
    assert result_df.loc["2023-01-07", "prev_known_min_date"] == pd.to_datetime(
        "2023-01-04"
    )
    assert result_df.loc["2023-01-07", "prev_known_min_val"] == 85.0

    assert result_df.loc["2023-01-07", "last_known_max_date"] == pd.to_datetime(
        "2023-01-05"
    )
    assert result_df.loc["2023-01-07", "last_known_max_val"] == 120.0
    assert result_df.loc["2023-01-07", "prev_known_max_date"] == pd.to_datetime(
        "2023-01-03"
    )
    assert result_df.loc["2023-01-07", "prev_known_max_val"] == 110.0


@pytest.mark.unit
def test_fill_min_max_date_val_different_col_name(
    df_for_date_val_fill: pd.DataFrame,
) -> None:
    """Verify it uses the specified col_name to retrieve values."""
    df = df_for_date_val_fill.copy()
    df["CustomVal"] = df["Close"] * 2  # Use a different column for values
    df = df.drop(columns=["Close"])  # Remove 'Close' to ensure it's not used

    result_df = _fill_min_max_date_val_columns(df, col_name="CustomVal")

    # Check at '2023-01-05' again, but with CustomVal
    assert result_df.loc["2023-01-05", "last_known_min_date"] == pd.to_datetime(
        "2023-01-04"
    )
    assert result_df.loc["2023-01-05", "last_known_min_val"] == (
        85.0 * 2
    )  # Value should be from CustomVal
    assert result_df.loc["2023-01-05", "prev_known_min_date"] == pd.to_datetime(
        "2023-01-02"
    )
    assert result_df.loc["2023-01-05", "prev_known_min_val"] == (90.0 * 2)

    assert result_df.loc["2023-01-05", "last_known_max_date"] == pd.to_datetime(
        "2023-01-03"
    )
    assert result_df.loc["2023-01-05", "last_known_max_val"] == (110.0 * 2)
