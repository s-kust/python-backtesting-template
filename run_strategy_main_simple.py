# pylint: disable=E2515
import logging
import sys

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


if __name__ == "__main__":
    load_dotenv()

    # clear LOG_FILE every time
    open(LOG_FILE, "w", encoding="UTF-8").close()

    # Here you can set different parameters of your strategy.
    # They will eventually be passed
    # to get_desired_current_position_size()
    # and process_special_situations()
    # See also the internals of the StrategyParams class

    strategy_params = StrategyParams(
        max_trade_duration_long=8,
        max_trade_duration_short=100,
        profit_target_long_pct=5.5,
        profit_target_short_pct=17.999,
        save_all_trades_in_xlsx=False,
    )

    # NOTE 1.
    # In the educational example, we take only long positions,
    # so max_trade_duration_short and profit_target_short_pct parameters
    # are not meaningful.

    # NOTE 2. The values ​​of the max_trade_duration_long
    # and profit_target_long_pct parameters
    # are selected arbitrarily.
    # See in the run_strategy_main_optimize.py file
    # how to optimize them.

    # Now we collect DataFrames with data and derived columns
    # for all the tickers we are interested in.
    # This data is stored in the TickersData class instance
    # as a dictionary whose keys are tickers and values ​​are DFs.
    # For more details, see the class TickersData internals,
    # and the add_features_v1_basic function.
    required_feature_columns = {"ma_200", "atr_14", "feature_basic", "feature_advanced"}
    tickers_data = TickersData(
        add_feature_cols_func=add_features_v1_basic,
        tickers=tickers_all,
        required_feature_cols=required_feature_columns,
    )

    SQN_modified_mean = run_all_tickers(
        tickers_data=tickers_data,
        tickers=tickers_all,
        strategy_params=strategy_params,
    )
    logging.debug(f"{SQN_modified_mean=}")  # pylint: disable=W1203
    print(f"{SQN_modified_mean=}, see also output.xslx", file=sys.stderr)
