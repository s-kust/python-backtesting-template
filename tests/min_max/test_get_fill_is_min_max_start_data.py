import pandas as pd
import pytest

from derivative_columns.min_max import _get_fill_is_min_max_start_data

# --- Unit Tests for _get_fill_is_min_max_start_data ---


@pytest.mark.unit
def test_get_fill_is_min_max_start_data_empty_df() -> None:
    empty_df = pd.DataFrame()
    with pytest.raises(KeyError):
        _get_fill_is_min_max_start_data(df=empty_df)


@pytest.mark.unit
def test_get_fill_is_min_max_start_data_not_yet_processed(
    spy_df_daily_with_min_max_cols: pd.DataFrame,
) -> None:
    """
    The first extremum to detect is the minimum (arbitrary choice)
    """
    res_date, res_extremum_type = _get_fill_is_min_max_start_data(
        df=spy_df_daily_with_min_max_cols
    )
    assert res_date == spy_df_daily_with_min_max_cols.index.min()
    assert res_extremum_type == "min"


@pytest.mark.unit
def test_get_fill_is_min_max_start_data_only_existing_mins(
    basic_ohlc_df_daily: pd.DataFrame,
) -> None:
    """
    Test the situation when the minimum has already been found.
    Make sure that now we will look for the maximum.
    """
    df = basic_ohlc_df_daily.copy()
    df["is_min"] = False
    df["is_max"] = False
    df.loc["2023-01-02", "is_min"] = True  # A minimum
    df.loc["2023-01-04", "is_min"] = True  # Latest minimum
    start_date, extremum_to_detect = _get_fill_is_min_max_start_data(df)
    assert start_date == pd.to_datetime("2023-01-05")  # Day after latest min
    assert extremum_to_detect == "max"


@pytest.mark.unit
def test_get_fill_is_min_max_start_data_only_existing_maxes(
    basic_ohlc_df_daily: pd.DataFrame,
) -> None:
    """
    Test the situation when the maximum has already been found.
    Make sure that now we will look for the minimum.
    """
    df = basic_ohlc_df_daily.copy()
    df["is_min"] = False
    df["is_max"] = False
    df.loc["2023-01-01", "is_max"] = True  # A maximum
    df.loc["2023-01-03", "is_max"] = True  # Latest maximum
    start_date, extremum_to_detect = _get_fill_is_min_max_start_data(df)
    assert start_date == pd.to_datetime("2023-01-04")  # Day after latest max
    assert extremum_to_detect == "min"


@pytest.mark.unit
def test_get_fill_is_min_max_start_data_latest_is_max(
    basic_ohlc_df_daily: pd.DataFrame,
) -> None:
    """Test when the latest extremum is a maximum."""
    df = basic_ohlc_df_daily.copy()
    df["is_min"] = False
    df["is_max"] = False
    df.loc["2023-01-02", "is_min"] = True
    df.loc["2023-01-04", "is_max"] = True  # Latest is max
    start_date, extremum_to_detect = _get_fill_is_min_max_start_data(df)
    assert start_date == pd.to_datetime("2023-01-05")
    assert extremum_to_detect == "min"


@pytest.mark.unit
def test_get_fill_is_min_max_start_data_latest_is_min(
    basic_ohlc_df_daily: pd.DataFrame,
) -> None:
    """Test when the latest extremum is a minimum."""
    df = basic_ohlc_df_daily.copy()
    df["is_min"] = False
    df["is_max"] = False
    df.loc["2023-01-01", "is_max"] = True
    df.loc["2023-01-03", "is_min"] = True  # Latest is min
    start_date, extremum_to_detect = _get_fill_is_min_max_start_data(df)
    assert start_date == pd.to_datetime("2023-01-04")
    assert extremum_to_detect == "max"


@pytest.mark.unit
def test_get_fill_is_min_max_start_data_no_data_after_latest_extremum(
    basic_ohlc_df_daily: pd.DataFrame,
) -> None:
    """Test when the latest extremum is the last row of the DataFrame."""
    df = basic_ohlc_df_daily.copy()
    df["is_min"] = False
    df["is_max"] = False
    df.loc["2023-01-05", "is_max"] = True  # Latest max at the very end
    start_date, extremum_to_detect = _get_fill_is_min_max_start_data(df)
    assert pd.isna(start_date)  # No date after the last one
    assert extremum_to_detect == "min"
