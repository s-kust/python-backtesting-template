import os

import pandas as pd
import requests

from constants import DATA_FILES_EXTENSION, LOCAL_FOLDER, TICKERS_DATA_FILENAMES_PREFIX

from .misc import ensure_df_has_all_required_columns

ALPHA_VANTAGE_API_KEY = os.environ.get("alpha_vantage_key")


def get_daily_raw_from_alpha_vantage(ticker: str) -> dict:
    # NOTE Currently, the last returned row is for yesterday
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=full"
    return requests.get(url).json()


def _rename_alpha_vantage_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(
        columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume",
        }
    )
    df["Close"] = df["Close"].astype(float)
    return df


def transform_a_v_raw_data_to_df(data: dict, key_name: str) -> pd.DataFrame:
    """
    Transform alpha vantage raw data to pd.DataFrame
    """
    if key_name not in data:
        raise ValueError(f"No column {key_name} in pd.DataFrame")
    df = pd.DataFrame.from_dict(data[key_name]).transpose()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return _rename_alpha_vantage_df_columns(df)


def _check_imported_data(df: pd.DataFrame, ticker: str, data_type: str) -> None:
    if not isinstance(df, pd.DataFrame):
        raise ValueError(
            f"In _check_imported_data ({ticker=}, {data_type=}): not instance of pd.DataFrame"
        )
    if df.empty:
        raise ValueError(
            f"In _check_imported_data ({ticker=}, {data_type=}): empty DataFrame"
        )
    if not set(df.columns.values) == {"Volume", "Close", "High", "Low", "Open"}:
        raise ValueError(
            f"In _check_imported_data ({ticker=}, {data_type=}): wrong pd.DataFrame columns: {set(df.columns.values)}"
        )
    all_columns_numeric = df.apply(
        lambda s: pd.to_numeric(s, errors="coerce").notnull().all()
    ).all()
    if not all_columns_numeric:
        raise ValueError(
            f"In _check_imported_data ({ticker=}, {data_type=}): not all pd.DataFrame columns numeric"
        )


def import_alpha_vantage_daily(ticker: str) -> pd.DataFrame:
    raw_data_daily: dict = get_daily_raw_from_alpha_vantage(ticker=ticker)
    data_daily: pd.DataFrame = transform_a_v_raw_data_to_df(
        data=raw_data_daily, key_name="Time Series (Daily)"
    )
    _check_imported_data(df=data_daily, ticker=ticker, data_type="Daily")
    return data_daily


def import_ohlc_daily(ticker: str) -> pd.DataFrame:
    """
    Check if local file with ticker data exists in /tmp/ folder.
    If yes, use it. Else, import OHLC data from AV,
    create pd.Df, save it locally and return.
    """
    internal_ticker = ticker.upper()
    local_file_path = _get_local_ticker_data_file_name(internal_ticker)
    if os.path.exists(local_file_path) and os.path.getsize(local_file_path) > 0:
        return pd.read_excel(local_file_path, index_col=0)
    res = import_alpha_vantage_daily(ticker=internal_ticker)
    res.to_excel(local_file_path)
    return pd.read_excel(local_file_path, index_col=0)


def _get_local_ticker_data_file_name(ticker: str) -> str:
    return LOCAL_FOLDER + TICKERS_DATA_FILENAMES_PREFIX + ticker + DATA_FILES_EXTENSION


def add_atr_col_to_df(
    df: pd.DataFrame, n: int = 5, exponential: bool = False
) -> pd.DataFrame:
    """
    Add ATR (Average True Range) column to DataFrame.
    Average True Range is a volatility estimate.
    n - number of periods.
    If exponential is true,
    use ewm - exponentially weighted values,
    to give more weight to the recent data point.
    Otherwise, calculate simple moving average.
    """

    ensure_df_has_all_required_columns(df=df, volume_col_required=False)
    data = df.copy(deep=True)
    high = data["High"]
    low = data["Low"]
    close = data["Close"]
    data["tr0"] = abs(high - low)
    data["tr1"] = abs(high - close.shift())
    data["tr2"] = abs(low - close.shift())
    data["tr"] = data[["tr0", "tr1", "tr2"]].max(axis=1)

    # today we know yesterday's TR only, not today's TR
    data["tr"] = data["tr"].shift()

    if exponential:
        data[f"atr_{n}"] = (
            data["tr"].ewm(alpha=2 / (n + 1), min_periods=n, adjust=False).mean()
        )
    else:
        data[f"atr_{n}"] = data["tr"].rolling(window=n, min_periods=n).mean()

    del data["tr0"]
    del data["tr1"]
    del data["tr2"]
    # del data["tr"]
    return data
