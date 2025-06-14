# pylint: disable=W0621
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

import pandas as pd
import pytest
import pytest_mock

from derivative_columns.min_max import _ensure_required_cols_min_max_in_df


@pytest.fixture
def spy_df_daily() -> pd.DataFrame:
    file = Path(__file__).parent / "fixtures_data/daily_SPY_for_testing.csv"
    df = pd.read_csv(file, parse_dates=[0], index_col=0)
    # Ensure columns are numeric where expected
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@pytest.fixture
def spy_df_daily_with_min_max_cols(
    spy_df_daily: pd.DataFrame,
) -> pd.DataFrame:
    return _ensure_required_cols_min_max_in_df(df=spy_df_daily)


@pytest.fixture
def spy_df_5_min() -> pd.DataFrame:
    file = Path(__file__).parent / "fixtures_data/5m_SPY_for_testing.csv"
    return pd.read_csv(file, index_col=0)


@pytest.fixture
def spy_df_15_min() -> pd.DataFrame:
    file = Path(__file__).parent / "fixtures_data/15m_SPY_for_testing.csv"
    return pd.read_csv(file, index_col=0)


@pytest.fixture
def basic_ohlc_df_daily() -> pd.DataFrame:
    """
    A simple DataFrame fixture for various unit tests.
    """
    data = {
        "Date": pd.to_datetime(
            ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
        ),
        "Open": [100, 101, 102, 103, 104],
        "High": [105, 106, 107, 108, 109],
        "Low": [99, 100, 101, 102, 103],
        "Close": [100, 103, 101, 104, 102],
    }
    df = pd.DataFrame(data).set_index("Date")
    return df


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """An empty DataFrame."""
    return pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close"]).set_index(
        "Date"
    )


@pytest.fixture
def single_row_df() -> pd.DataFrame:
    """A DataFrame with a single row."""
    data = {
        "Date": [pd.to_datetime("2023-01-01")],
        "Open": [100],
        "High": [105],
        "Low": [99],
        "Close": [102],
    }
    return pd.DataFrame(data).set_index("Date")


@pytest.fixture
def mock_add_atr_col_to_df(mocker: pytest_mock.plugin.MockerFixture) -> MagicMock:
    """
    Mock the add_atr_col_to_df function to control its behavior in tests.
    """
    # NOTE don't worry about the mocker argument, it magically works - https://stackoverflow.com/a/72943495/3139228

    # Use mocker from pytest-mock to patch the function within the min_max module
    return mocker.patch("derivative_columns.min_max.add_atr_col_to_df")
