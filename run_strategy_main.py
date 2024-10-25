import logging
from typing import Optional

from dotenv import load_dotenv

from constants import LOG_FILE, tickers_all
from customizable import StrategyParams
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
        max_trade_duration_long=None,
        max_trade_duration_short=None,
        profit_target_pct=7.7,
    )

    SQN_modified_mean = run_all_tickers(
        tickers=tickers_all,
        strategy_params=strategy_params,
    )
    logging.debug(f"{SQN_modified_mean=}")
