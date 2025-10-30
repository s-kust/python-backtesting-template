from typing import Any

import pandas as pd
import pytest

from utils.misc import check_df_format


@pytest.mark.unit
@pytest.mark.parametrize(
    "df_fixture, expected_interval_minutes",
    [
        ("spy_df_daily", 1440),
        ("spy_df_5_min", 5),
        ("spy_df_15_min", 15),
    ],
)
def test_check_df_format_ok(
    request: Any, df_fixture: str, expected_interval_minutes: int
) -> None:
    """
    Tests the check_df_format function with various valid DataFrames.
    """
    df = request.getfixturevalue(df_fixture)
    res = check_df_format(df=df)
    assert res["is_datetime_index"] is True
    assert res["inferred_interval_minutes"] == expected_interval_minutes


def test_check_df_format_empty(empty_df: pd.DataFrame) -> None:
    """
    Tests the check_df_format function with an empty DataFrame.

    This test ensures that the function handles the edge case of an empty
    DataFrame gracefully, correctly reporting that the index is not a
    DatetimeIndex and the interval is 999.
    """
    res = check_df_format(df=empty_df)
    assert res["is_datetime_index"] is False
    assert res["inferred_interval_minutes"] == 999
