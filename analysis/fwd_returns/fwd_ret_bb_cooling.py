import logging
import sys
from typing import List

import pandas as pd

from constants import LOG_FILE, NUM_DAYS_FWD_RETURN
from forecast.forecast_bb import add_bb_forecast
from utils.bootstrap import analyze_values_by_group
from utils.get_df_with_fwd_ret import get_df_with_fwd_ret
from utils.local_data import TickersData

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
)


def _get_bb_cooling_label(row) -> str:

    # check if oversold conditions start improving
    if (row["forecast_bb_yesterday"]) < -2.4 and (
        row["forecast_bb_yesterday"] < row["forecast_bb"]
    ):
        return "LOW_TO_HIGHER"

    # check if overbought conditions start improving
    if (row["forecast_bb_yesterday"]) > 2.4 and (
        row["forecast_bb_yesterday"] > row["forecast_bb"]
    ):
        return "HIGH_TO_LOWER"

    # base case
    return "NOTHING_SPECIAL"


def add_bb_cooling_to_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add discrete feature bb_cooling,
    i. e. overbought or oversold conditions start improving.
    """
    res = df.copy()

    # We need forecast_bb for this feature
    res = add_bb_forecast(df=res, col_name="Close")
    res["forecast_bb_yesterday"] = res["forecast_bb"].shift(1)
    res["bb_cooling"] = res.apply(_get_bb_cooling_label, axis=1)
    del res["forecast_bb_yesterday"]
    return res


def analyze_fwd_ret_by_bb_cooling(
    tickers_data: TickersData,
    tickers: List[str],
    excel_file_name: str,
):
    """
    Function analyzes the forward returns,
    noted as the percentage difference of todays and forward Close prices.
    Explanatory variable: bb_cooling feature. It indicates
    whether oversold or overbought conditions started to cool off.
    See and customize its details in the code of add_features_forecasts_to_ohlc_v3 function.
    """
    GROUP_COL_NAME = "bb_cooling"
    combined_ohlc_all = pd.DataFrame()
    tickers_total_count = len(tickers)
    counter = 0
    for ticker in tickers:
        counter = counter + 1
        print(
            f"Running {ticker=}, {counter} of {tickers_total_count}...", file=sys.stderr
        )

        # add feature to ticker's daily OHLC data
        ohlc_with_forecast_bb_and_fwd_ret = get_df_with_fwd_ret(
            ohlc_df=tickers_data.get_data(ticker=ticker),
            add_features_forecasts_func=add_bb_cooling_to_ohlc,
            num_days=NUM_DAYS_FWD_RETURN,
        )

        # append ticker's daily OHLC data to all OHLC data
        combined_ohlc_all = pd.concat(
            [combined_ohlc_all, ohlc_with_forecast_bb_and_fwd_ret]
        )
    combined_ohlc_all = combined_ohlc_all.dropna()
    # combined_ohlc_all.to_excel("combined_ohlc_all.xlsx", index=False)

    # This is for sorting groups in an Excel file
    group_order_bb_cooling = {
        "all_data": 4,
        "LOW_TO_HIGHER": 1,
        "HIGH_TO_LOWER": 2,
        "NOTHING_SPECIAL": 3,
    }

    # Up until this point there has been preparation,
    # and now the analysis will be carried out.
    analyze_values_by_group(
        df=combined_ohlc_all,
        group_col_name=GROUP_COL_NAME,
        values_col_name=f"ret_{NUM_DAYS_FWD_RETURN}",
        group_order_map=group_order_bb_cooling,
        excel_file_name=excel_file_name,
    )
    print(
        f"analyze_fwd_ret_by_bb_cooling - complete! Now you may explore the results file {excel_file_name}",
        file=sys.stderr,
    )
