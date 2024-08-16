import logging
import sys

import pandas as pd
from dotenv import load_dotenv

from strategy import run_all_tickers

RESULT_XLSX_FILE = "parameter_values.xlsx"


def compare_parameter_values():
    """
    Run run_all_tickers() with different parameters values,
    save results as pd.DataFrame in Excel for subsequent analysis
    """

    # Here are the strategy parameters
    # whose optimal values ​​you are looking for

    # NOTE These parameters must be the same
    # as those used in the get_desired_current_position_size function.
    param_1_range = [x * 0.01 for x in range(13, 19, 3)]
    param_2_range = [x for x in range(1, 3, 1)]
    logging.debug(f"compare_parameter_values: {param_1_range=}")
    logging.debug(f"compare_parameter_values: {param_2_range=}")

    all_res = list()
    total_count = len(param_1_range) * len(param_2_range)
    counter = 0
    for param_1 in param_1_range:
        for param_2 in param_2_range:
            counter = counter + 1
            print(
                f"Running {param_1=}, {param_2=} - {counter} of {total_count}",
                file=sys.stderr,
            )
            strategy_params: dict = dict()
            strategy_params["param_1"] = param_1
            strategy_params["param_2"] = param_2

            # NOTE What is SQN modified, see in README.md.
            avg_sqn_modified = run_all_tickers(
                max_trade_duration_long=None,
                max_trade_duration_short=None,
                strategy_params=strategy_params,
            )
            res: dict = dict()
            res["param_1"] = param_1
            res["param_2"] = param_2
            res["avg_sqn_m"] = avg_sqn_modified
            print(
                f"Iteration result {res}",
                file=sys.stderr,
            )
            all_res.append(res)
    pd.DataFrame(all_res).to_excel(RESULT_XLSX_FILE, index=False)


if __name__ == "__main__":
    load_dotenv()
    compare_parameter_values()
