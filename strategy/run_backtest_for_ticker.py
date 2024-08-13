import logging
import os
from typing import Optional, Tuple

import pandas as pd
from backtesting import Backtest, Strategy

from get_position_size_main import get_desired_current_position_size
from utils.prepare_df import get_forecast_bb
from utils.strategy_exec import (
    adjust_position,
    all_current_trades_info,
    create_last_day_results,
    log_initial_data_for_today,
    process_special_situations,
    update_stop_losses,
)


def run_backtest_for_ticker(
    ticker: str,
    data: pd.DataFrame,
    max_trade_duration_long: Optional[int] = None,
    max_trade_duration_short: Optional[int] = None,
    strategy_params: Optional[dict] = None,
) -> Tuple[pd.Series, pd.DataFrame, dict]:
    local_env = os.environ.get("environment", default="prod")
    last_day_result = dict()
    last_day_result["last_day_index"] = data.index[-1]

    class CustomTradingStrategy1(Strategy):
        def init(self):
            # create some forecast and use it here
            self.forecast = self.I(get_forecast_bb, data)
            # NOTE ATR is used in update_stop_losses
            self.atr = pd.Series(self.data.tr).rolling(50).mean().bfill().values

        def next(self):
            """
            1. For every open trade, update stop-loss.

            2. Process special situations. If special situation detected,
            it is already processed, so don't execute step 3 at this day, only step 4.

            3. Call get_desired_current_position_size and adjust_position.

            4. If it's the last day of data series, fill last_day_result.
            """

            # 1
            logging.debug("\n")
            update_stop_losses(strategy=self)

            # preparations for 4
            current_position_num_stocks = self.position.size
            all_current_trades = all_current_trades_info(strategy=self)
            log_initial_data_for_today(strategy=self, ticker=ticker)

            # 2
            ss_today = False
            today_special_situation_msg = None
            if self.trades:
                ss_today, today_special_situation_msg = process_special_situations(
                    strategy=self,
                    max_trade_duration_long=max_trade_duration_long,
                    max_trade_duration_short=max_trade_duration_short,
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
                strategy_params=strategy_params,
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
        trade_on_close=True,  # Execute trading signals on today's close price
        exclusive_orders=False,
        # hedging=False - can't hold long and short position simultaneously,
        # see also process_max_duration function
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
