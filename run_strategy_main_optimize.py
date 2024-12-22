import itertools
import logging
from functools import partial
from typing import List

import pandas as pd
from dotenv import load_dotenv

from constants import LOG_FILE, tickers_all
from customizable import StrategyParams
from features.f_v1_basic import add_features_v1_basic
from strategy import run_all_tickers
from utils.local_data import TickersData

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
)


def run_all_tickers_with_parameters(
    max_trade_duration_long: int,
    profit_target_long_pct: float,
    atr_multiplier_threshold: int,
    save_all_trades_in_xlsx: bool,
) -> float:

    # NOTE
    # This is almost the same code as in the run_strategy_main_simple.py file,
    # with some minor changes explained below.

    # clear LOG_FILE every time
    open(LOG_FILE, "w", encoding="UTF-8").close()

    strategy_params = StrategyParams(
        max_trade_duration_long=max_trade_duration_long,
        max_trade_duration_short=100,
        profit_target_long_pct=profit_target_long_pct,
        profit_target_short_pct=17.999,
        save_all_trades_in_xlsx=save_all_trades_in_xlsx,
    )

    # NOTE
    # In the educational example, we take only long positions,
    # so max_trade_duration_short and profit_target_short_pct parameters
    # are not meaningful.

    # NOTE You can use any other tickers
    # instead of those included in the tickers_all list

    # make add_features_v1_basic function
    # use the atr_multiplier_threshold input
    # instead of default value
    p_add_features_v1 = partial(
        add_features_v1_basic, atr_multiplier_threshold=atr_multiplier_threshold
    )
    tickers_data = TickersData(
        add_feature_cols_func=p_add_features_v1,
        tickers=tickers_all,
        recreate_columns_every_time=True,
        # NOTE If recreate_columns_every_time=False,
        # atr_multiplier_threshold optimization won't work
    )

    sqn_modified_mean = run_all_tickers(
        tickers=tickers_all, strategy_params=strategy_params, tickers_data=tickers_data
    )

    # NOTE Why SQN_modified_mean is used
    # as an optimization criterion,
    # see the README.md file.
    return sqn_modified_mean


if __name__ == "__main__":
    load_dotenv()

    EXCEL_FILE_NAME = "optimization_results.xlsx"
    all_results: List[dict] = list()

    # Here you list the parameters you want to optimize, as well as their value ranges.
    # These same parameters must be used
    # when calling the run_all_tickers_with_parameters() function.
    max_trade_duration_long_vals = range(9, 11)
    profit_target_long_pct_vals = [x / 10.0 for x in range(25, 45, 10)]
    atr_multiplier_threshold_vals = range(6, 8)

    combinations = itertools.product(
        max_trade_duration_long_vals,
        profit_target_long_pct_vals,
        atr_multiplier_threshold_vals,
    )
    total_count = sum(1 for x in combinations)

    # NOTE this reload is mandatory,
    # because the iterator was consumed
    # when determined the total_count
    combinations = itertools.product(
        max_trade_duration_long_vals,
        profit_target_long_pct_vals,
        atr_multiplier_threshold_vals,
    )

    counter = 0  # pylint: disable=C0103
    for item in combinations:
        counter = counter + 1  # pylint: disable=C0103
        print(f"Running combination {counter} of {total_count}...")
        max_trade_duration_long_val = item[0]
        profit_target_long_pct_val = item[1]
        atr_multiplier_threshold_val = item[2]
        SQN_modified_mean_val = run_all_tickers_with_parameters(
            max_trade_duration_long=max_trade_duration_long_val,
            profit_target_long_pct=profit_target_long_pct_val,
            atr_multiplier_threshold=atr_multiplier_threshold_val,
            save_all_trades_in_xlsx=False,
        )
        result = {
            "max_duration_long": max_trade_duration_long_val,
            "profit_tgt_lg_pct": profit_target_long_pct_val,
            "atr_multiplier": atr_multiplier_threshold_val,
            "SQN_m_mean": SQN_modified_mean_val,
        }
        all_results.append(result)
        # save to Excel file every time in case the script execution is interrupted.
        # The next time you run it, you won't have to process the same parameter sets again.
        pd.DataFrame.from_records(all_results).to_excel(EXCEL_FILE_NAME, index=False)
    print(f"Ready! See the file {EXCEL_FILE_NAME}")
