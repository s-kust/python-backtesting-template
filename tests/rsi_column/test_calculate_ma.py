import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose as assert_all_close
from pandas.testing import assert_series_equal

from derivative_columns.rsi import _calculate_ma


@pytest.mark.unit
def test_calculate_ma_simple(series_for_ma_tests: pd.Series) -> None:
    """Test simple moving average calculation."""
    # Series: [10, 12, 14, 16, 18, 20]
    # Period 3 SMA: [NaN, NaN, 12, 14, 16, 18]
    expected_ma = pd.Series(
        [np.nan, np.nan, 12.0, 14.0, 16.0, 18.0], index=series_for_ma_tests.index
    )
    result = _calculate_ma(series=series_for_ma_tests, period=3, ma_type="simple")
    assert_series_equal(result, expected_ma)


@pytest.mark.unit
def test_calculate_ma_exponential(series_for_ma_tests: pd.Series) -> None:
    """Test exponential moving average calculation (adjust=False)."""
    # Series: [10, 12, 14, 16, 18, 20]
    # Period 3 EMA (alpha = 2/(3+1) = 0.5)
    # EMA_1 = 10
    # EMA_2 = 12 * 0.5 + 10 * 0.5 = 11
    # EMA_3 = 14 * 0.5 + 11 * 0.5 = 12.5
    # EMA_4 = 16 * 0.5 + 12.5 * 0.5 = 14.25
    # EMA_5 = 18 * 0.5 + 14.25 * 0.5 = 16.125
    # EMA_6 = 20 * 0.5 + 16.125 * 0.5 = 18.0625
    expected_ma = pd.Series(
        [10.0, 11.0, 12.5, 14.25, 16.125, 18.0625], index=series_for_ma_tests.index
    )
    result = _calculate_ma(series=series_for_ma_tests, period=3, ma_type="exponential")
    assert_all_close(
        result.values, expected_ma.values  # type: ignore
    )  # Using all_close for float comparisons


@pytest.mark.unit
def test_calculate_ma_invalid_ma_type(series_for_ma_tests: pd.Series) -> None:
    """Test calculate_ma with an invalid moving average type."""
    with pytest.raises(
        ValueError, match="Unsupported moving average type: ma_type='wrong'"
    ):
        _calculate_ma(series=series_for_ma_tests, period=3, ma_type="wrong")
