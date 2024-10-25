import logging

from dotenv import load_dotenv

from analysis.fwd_returns import (
    analyze_fwd_ret_by_bb_cooling,
    analyze_fwd_ret_by_bb_group,
)
from constants import (
    LOG_FILE,
    NUM_DAYS_FWD_RETURN,
    tickers_all,
    tickers_commodities,
    tickers_precious,
    tickers_stocks,
)
from utils.import_data import import_ohlc_daily
from utils.local_data import TickersData

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
)


if __name__ == "__main__":
    load_dotenv()

    # clear LOG_FILE every time
    open(LOG_FILE, "w").close()

    tickers_data = TickersData(tickers=tickers_all, import_ohlc_func=import_ohlc_daily)

    excel_file_name = f"fwd_ret_{NUM_DAYS_FWD_RETURN}_all_by_bb_group.xlsx"
    analyze_fwd_ret_by_bb_group(
        tickers_data=tickers_data,
        tickers=tickers_all,
        excel_file_name=excel_file_name,
    )

    excel_file_name = f"fwd_ret_{NUM_DAYS_FWD_RETURN}_all_by_bb_cooling.xlsx"
    analyze_fwd_ret_by_bb_cooling(
        tickers_data=tickers_data, tickers=tickers_all, excel_file_name=excel_file_name
    )

    excel_file_name = f"fwd_ret_{NUM_DAYS_FWD_RETURN}_precious_by_bb_cooling.xlsx"
    analyze_fwd_ret_by_bb_cooling(
        tickers_data=tickers_data,
        tickers=tickers_precious,
        excel_file_name=excel_file_name,
    )

    excel_file_name = f"fwd_ret_{NUM_DAYS_FWD_RETURN}_stocks_by_bb_cooling.xlsx"
    analyze_fwd_ret_by_bb_cooling(
        tickers_data=tickers_data,
        tickers=tickers_stocks,
        excel_file_name=excel_file_name,
    )

    excel_file_name = f"fwd_ret_{NUM_DAYS_FWD_RETURN}_cmd_by_bb_cooling.xlsx"
    analyze_fwd_ret_by_bb_cooling(
        tickers_data=tickers_data,
        tickers=tickers_commodities,
        excel_file_name=excel_file_name,
    )
