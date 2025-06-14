import pandas as pd
import pytest


@pytest.fixture
def df_for_date_val_fill() -> pd.DataFrame:
    """DataFrame prepped with is_min/is_max for _fill_min_max_date_val_columns tests."""
    data = {
        "Date": pd.to_datetime(
            [
                "2023-01-01",
                "2023-01-02",
                "2023-01-03",
                "2023-01-04",
                "2023-01-05",
                "2023-01-06",
                "2023-01-07",
            ]
        ),
        "Close": [100, 90, 110, 85, 120, 95, 130],  # Mock prices
        "is_min": [False, True, False, True, False, True, False],
        "is_max": [False, False, True, False, True, False, False],
    }
    df = pd.DataFrame(data).set_index("Date")
    # Initialize all relevant columns to None/False as _ensure_required_cols would
    df["last_known_min_date"] = None
    df["last_known_max_date"] = None
    df["prev_known_min_date"] = None
    df["prev_known_max_date"] = None
    df["last_known_min_val"] = None
    df["last_known_max_val"] = None
    df["prev_known_min_val"] = None
    df["prev_known_max_val"] = None
    return df
