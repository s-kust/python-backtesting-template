import logging
import os
from typing import Tuple

import pandas as pd
from backtesting import Backtest, Strategy

from customizable import StrategyParams, get_desired_current_position_size
from utils.misc import get_forecast_bb
from utils.strategy_exec import (
    adjust_position,
    all_current_trades_info,
    check_set_profit_targets_long_trades,
    check_set_profit_targets_short_trades,
    create_last_day_results,
    log_initial_data_for_today,
    process_special_situations,
    update_stop_losses,
)


def run_backtest_for_ticker(
    ticker: str,
    data: pd.DataFrame,
    strategy_params: StrategyParams,
) -> Tuple[pd.Series, pd.DataFrame, dict]:
    local_env = os.environ.get("environment", default="prod")
    last_day_result = dict()
    last_day_result["last_day_index"] = data.index[-1]

    class CustomTradingStrategy1(Strategy):
        def init(self):

            # self.parameters are heavily used
            # in get_desired_current_position_size()
            # and process_special_situations()
            self.parameters = strategy_params

            # NOTE This forecast is used only
            # in several special situations, not very meaningful.
            # You configure the really important stuff
            # inside get_desired_current_position_size and add_features_XXX functions
            # and in special situations.
            self.forecast = self.I(get_forecast_bb, data)

            # NOTE ATR is used in update_stop_losses
            self.atr = pd.Series(self.data.tr).rolling(50).mean().bfill().values

        def next(self):
            """
            1. For every open trade, update stop-loss and process profit target.

            2. Process special situations.

            If at least one special situation is detected,
            it means that we need to close all open positions
            and don't open any new positions at this day.
            The system calls the add_tag_to_trades_and_close_position().
            No need to execute step 3 at this day, only step 4.

            3. Call get_desired_current_position_size() and adjust_position().

            4. If it's the last day of data series, fill the last_day_result dict.
            """

            # 1
            logging.debug("\n")
            update_stop_losses(strategy=self)
            if self.parameters.profit_target_long_pct is not None:
                check_set_profit_targets_long_trades(strategy=self)
            if self.parameters.profit_target_short_pct is not None:
                check_set_profit_targets_short_trades(strategy=self)

            # preparations for 4
            current_position_num_stocks = self.position.size
            all_current_trades = all_current_trades_info(strategy=self)
            log_initial_data_for_today(strategy=self, ticker=ticker)

            # 2 -
            # NOTE ss - special situation
            ss_today = False
            today_special_situation_msg = None
            if self.trades:
                ss_today, today_special_situation_msg = process_special_situations(
                    strategy=self
                )
            if ss_today:
                # extraordinary step 4, because now we’ll finish
                # and won’t get to the main step 4
                if self.data.index[-1] == data.index[-1]:
                    last_day_result.update(
                        create_last_day_results(
                            current_position_num_stocks,
                            all_current_trades,
                            today_special_situation_msg,
                        )
                    )
                return

            # 3
            (
                desired_size,
                current_position_size,
                desired_size_msg,
            ) = get_desired_current_position_size(
                strategy=self,
            )
            logging.debug(f"{desired_size=}")
            today_action = adjust_position(
                strategy=self,
                current_position_size=current_position_size,
                desired_size=desired_size,
            )

            # 4
            if self.data.index[-1] == data.index[-1]:
                last_day_result.update(
                    create_last_day_results(
                        current_position_num_stocks,
                        all_current_trades,
                        today_special_situation_msg,
                        current_position_size,
                        desired_size,
                        desired_size_msg,
                        today_action,
                    )
                )

    bt = Backtest(
        data,
        CustomTradingStrategy1,
        cash=10000,
        # Commission set to 0.1% for trade enter and the same for exit,
        # so you need average profit at least 0.2%.
        commission=0.001,
        trade_on_close=False,  # Execute trading signals on today's close price or tomorrow at the open
        exclusive_orders=False,
        # NOTE hedging=False - can't hold long and short position simultaneously,
        # If you set hedging=True, you'll have to improve process_max_duration function,
        # split it into two separate functions
        # for max_trade_duration_long and max_trade_duration_short
        hedging=False,
        margin=0.02,
    )
    stats = bt.run()
    if local_env == "dev":
        logging.debug(stats)
        logging.debug(stats._trades.columns)
        bt.plot(filename=f"res_plot_{ticker}.html", plot_volume=False)

    # NOTE here you can add custom stuff to stats

    # stats["tr_delta_min"] = data["tr_delta"].min()
    # stats["tr_delta_001"] = data["tr_delta"].quantile(0.01)
    # stats["tr_delta_005"] = data["tr_delta"].quantile(0.05)
    # stats["tr_delta_50"] = data["tr_delta"].quantile(0.5)
    # stats["tr_delta_095"] = data["tr_delta"].quantile(0.95)
    # stats["tr_delta_099"] = data["tr_delta"].quantile(0.99)
    # stats["tr_delta_max"] = data["tr_delta"].max()

    logging.debug(f"{last_day_result=}")
    logging.debug("\n")
    return stats, stats._trades, last_day_result
