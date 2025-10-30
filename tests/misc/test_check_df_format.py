from typing import Any

import pandas as pd
import pytest

from utils.misc import check_df_format


@pytest.mark.unit
@pytest.mark.parametrize(
    "df_fixture, expected_interval",
    [
        ("spy_df_daily", "1 days"),
        ("spy_df_5_min", "5 min"),
        ("spy_df_15_min", "15 min"),
    ],
)
def test_check_df_format_ok(
    request: Any, df_fixture: str, expected_interval: str
) -> None:
    """
    Tests the check_df_format function with various valid DataFrames.
    """
    df = request.getfixturevalue(df_fixture)
    res = check_df_format(df=df, expected_interval=expected_interval)
    assert res["is_datetime_index"] is True
    assert res["is_correct_interval"] is True
    assert res["inferred_interval"] == pd.Timedelta(expected_interval)
    print(res)


def test_check_df_format_empty(empty_df: pd.DataFrame) -> None:
    """
    Tests the check_df_format function with an empty DataFrame.

    This test ensures that the function handles the edge case of an empty
    DataFrame gracefully, correctly reporting that the index is not a
    DatetimeIndex and the interval cannot be checked.
    """
    res = check_df_format(df=empty_df, expected_interval="some wrong")
    assert res["is_datetime_index"] is False
    assert res["is_correct_interval"] is False
    assert res["inferred_interval"] == "N/A (DF too small or Index not Datetime)"
