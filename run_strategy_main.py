import logging
from typing import Optional

from dotenv import load_dotenv

from constants import LOG_FILE, tickers_all
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

    # here you can set maximum duration
    # for long and short trades - number of days
    max_trade_duration_long: Optional[int] = None
    max_trade_duration_short: Optional[int] = 4

    # Here you can add different parameters of your strategy.
    # They will eventually be passed to get_desired_current_position_size()
    strategy_params: Optional[dict] = None

    SQN_modified_mean = run_all_tickers(
        tickers=tickers_all,
        max_trade_duration_long=max_trade_duration_long,
        max_trade_duration_short=max_trade_duration_short,
        strategy_params=strategy_params,
    )
    logging.debug(f"{SQN_modified_mean=}")
