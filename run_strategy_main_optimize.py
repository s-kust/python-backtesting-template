import itertools
import logging
from typing import List

import pandas as pd
from dotenv import load_dotenv

from constants import LOG_FILE, tickers_all
from customizable import StrategyParams, add_features_v1_basic
from strategy import run_all_tickers

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
)


def run_all_tickers_with_parameters(
    max_trade_duration_long: int,
    max_trade_duration_short: int,
    profit_target_long_pct: float,
    profit_target_short_pct: float,
    save_all_trades_in_xlsx: bool,
) -> float:

    # clear LOG_FILE every time
    open(LOG_FILE, "w").close()

    strategy_params = StrategyParams(
        max_trade_duration_long=max_trade_duration_long,
        max_trade_duration_short=max_trade_duration_short,
        profit_target_long_pct=profit_target_long_pct,
        profit_target_short_pct=profit_target_short_pct,
        save_all_trades_in_xlsx=save_all_trades_in_xlsx,
    )

    # NOTE You can use any other tickers
    # instead of those included in the tickers_all list
    SQN_modified_mean = run_all_tickers(
        tickers=tickers_all,
        strategy_params=strategy_params,
        add_features_func=add_features_v1_basic,
    )

    # NOTE Why SQN_modified_mean is used
    # as an optimization criterion,
    # see the README.md file.
    return SQN_modified_mean


if __name__ == "__main__":
    load_dotenv()

    EXCEL_FILE_NAME = "optimization_results.xlsx"
    res: List[dict] = list()

    # Here you list the parameters you want to optimize, as well as their value ranges.
    # The parameters must be a subset of the StrategyParams class fields.

    # These same parameters must be used
    # when calling the run_all_tickers_with_parameters() function.
    max_trade_duration_long_vals = range(3, 5)
    max_trade_duration_short_vals = range(3, 5)
    profit_target_long_pct_vals = [x / 10.0 for x in range(80, 100, 10)]
    profit_target_short_pct_vals = [x / 10.0 for x in range(80, 100, 10)]

    combinations = itertools.product(
        max_trade_duration_long_vals,
        max_trade_duration_short_vals,
        profit_target_long_pct_vals,
        profit_target_short_pct_vals,
    )
    total_count = sum(1 for x in combinations)

    # NOTE this reload is mandatory,
    # because the iterator was consumed
    # when determined the total_count
    combinations = itertools.product(
        max_trade_duration_long_vals,
        max_trade_duration_short_vals,
        profit_target_long_pct_vals,
        profit_target_short_pct_vals,
    )

    counter = 0
    for item in combinations:
        counter = counter + 1
        print(f"Running combination {counter} of {total_count}...")
        max_trade_duration_long = item[0]
        max_trade_duration_short = item[1]
        profit_target_long_pct = item[2]
        profit_target_short_pct = item[3]
        SQN_modified_mean = run_all_tickers_with_parameters(
            max_trade_duration_long=max_trade_duration_long,
            max_trade_duration_short=max_trade_duration_short,
            profit_target_long_pct=profit_target_long_pct,
            profit_target_short_pct=profit_target_short_pct,
            save_all_trades_in_xlsx=False,
        )
        val = {
            "max_duration_long": max_trade_duration_long,
            "max_duration_short": max_trade_duration_short,
            "profit_tgt_lg_pct": profit_target_long_pct,
            "profit_tgt_st_pct": profit_target_short_pct,
            "SQN_m_mean": SQN_modified_mean,
        }
        res.append(val)
    pd.DataFrame.from_records(res).to_excel(EXCEL_FILE_NAME, index=False)
    print(f"Ready! See the file {EXCEL_FILE_NAME}")
