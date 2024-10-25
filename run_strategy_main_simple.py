import logging
import sys
from typing import Optional

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


if __name__ == "__main__":
    load_dotenv()

    # clear LOG_FILE every time
    open(LOG_FILE, "w").close()

    # Here you can set different parameters of your strategy.
    # They will eventually be passed
    # to get_desired_current_position_size()
    # and process_special_situations()
    # See also the internals of the StrategyParams class

    strategy_params = StrategyParams(
        max_trade_duration_long=4,
        max_trade_duration_short=4,
        profit_target_long_pct=0.92,
        profit_target_short_pct=1.912,
        save_all_trades_in_xlsx=True,
    )

    SQN_modified_mean = run_all_tickers(
        tickers=tickers_all,
        strategy_params=strategy_params,
        add_features_func=add_features_v1_basic,
    )
    logging.debug(f"{SQN_modified_mean=}")
    print(f"{SQN_modified_mean=}", file=sys.stderr)
