from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def spy_df_daily() -> pd.DataFrame:
    file = Path(__file__).parent / "daily_SPY_for_testing.csv"
    return pd.read_csv(file, index_col=0)


@pytest.fixture
def spy_df_5_min() -> pd.DataFrame:
    file = Path(__file__).parent / "5m_SPY_for_testing.csv"
    return pd.read_csv(file, index_col=0)


@pytest.fixture
def spy_df_15_min() -> pd.DataFrame:
    file = Path(__file__).parent / "15m_SPY_for_testing.csv"
    return pd.read_csv(file, index_col=0)
