import logging

from dotenv import load_dotenv

from analysis.fwd_returns import (
    analyze_fwd_ret_by_bb_cooling,
    analyze_fwd_ret_by_bb_group,
)
from constants import LOG_FILE

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

    # analyze_fwd_ret_by_bb_group()

    # AND / OR

    analyze_fwd_ret_by_bb_cooling()
