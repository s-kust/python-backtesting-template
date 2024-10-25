import os
import sys

import pandas as pd
import requests

from constants import DATA_FILES_EXTENSION, LOCAL_FOLDER, TICKERS_DATA_FILENAMES_PREFIX

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


def check_ohlc_df(
    df: pd.DataFrame, data_type: str, volume_required: bool = False
) -> None:
    """
    OHLC DataFrame should be non-empty,
    contain all OHLC_REQUIRED_COLUMNS,
    and all values should be numeric.
    If it contains additional columns, it is OK.
    """
    OHLC_REQUIRED_COLUMNS = ["Close", "High", "Low", "Open"]
    if not isinstance(df, pd.DataFrame):
        raise ValueError(
            f"In check_ohlc_df ({data_type=}): not instance of pd.DataFrame"
        )
    if df.empty:
        raise ValueError(f"In check_ohlc_df ({data_type=}): empty DataFrame")
    for col_name in OHLC_REQUIRED_COLUMNS:
        if col_name not in df.columns:
            raise ValueError(
                f"In check_ohlc_df ({data_type=}): column {col_name} is absent in DataFrame"
            )
    if volume_required:
        if "Volume" not in df.columns:
            raise ValueError(
                f"In check_ohlc_df ({data_type=}): Volume column is absent in DataFrame"
            )
        all_columns_numeric = (
            df[["Close", "High", "Low", "Open", "Volume"]]
            .apply(lambda s: pd.to_numeric(s, errors="coerce").notnull().all())
            .all()
        )
    else:
        all_columns_numeric = (
            df[["Close", "High", "Low", "Open"]]
            .apply(lambda s: pd.to_numeric(s, errors="coerce").notnull().all())
            .all()
        )
    if not all_columns_numeric:
        raise ValueError(
            f"In check_ohlc_df ({data_type=}): not all pd.DataFrame columns numeric"
        )


def import_alpha_vantage_daily(ticker: str) -> pd.DataFrame:
    """ """
    raw_data_daily: dict = get_daily_raw_from_alpha_vantage(ticker=ticker)
    data_daily: pd.DataFrame = transform_a_v_raw_data_to_df(
        data=raw_data_daily, key_name="Time Series (Daily)"
    )
    check_ohlc_df(df=data_daily, data_type="Daily", volume_required=True)
    return data_daily


def import_ohlc_daily(ticker: str) -> pd.DataFrame:
    """
    Check if local file with ticker data exists in /tmp/ folder.
    If yes, use it. Else, import OHLC data from AV,
    create pd.Df, save it locally and return.
    """
    internal_ticker = ticker.upper()
    local_file_path = _get_local_ticker_data_file_name(internal_ticker)
    print(
        f"Calling import_ohlc_daily with {internal_ticker=}, {local_file_path=}",
        file=sys.stderr,
    )
    if os.path.exists(local_file_path) and os.path.getsize(local_file_path) > 0:
        return pd.read_excel(local_file_path, index_col=0)
    res = import_alpha_vantage_daily(ticker=internal_ticker)
    res.to_excel(local_file_path)
    return pd.read_excel(local_file_path, index_col=0)


def _get_local_ticker_data_file_name(ticker: str) -> str:
    return LOCAL_FOLDER + TICKERS_DATA_FILENAMES_PREFIX + ticker + DATA_FILES_EXTENSION
