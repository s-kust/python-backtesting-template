import logging
from typing import Tuple

from backtesting import Strategy

from constants import (
    CLOSED_MAX_DURATION,
    CLOSED_VOLATILITY_SPIKE,
    SS_MAX_DURATION,
    SS_NO_TODAY,
    SS_PARTIAL_CLOSE,
    SS_VOLATILITY_SPIKE,
)

from .misc import add_tag_to_trades_and_close_position, log_all_trades
from .partial_close import process_partial_close


def process_volatility_spike(strategy: Strategy) -> bool:
    if strategy.data.tr_delta[-1] < 2.5:
        return False
    add_tag_to_trades_and_close_position(
        strategy=strategy, text_to_add=CLOSED_VOLATILITY_SPIKE
    )
    logging.debug(
        "Closing position because volatility is too high, probable trend change..."
    )
    return True


def process_max_duration(
    strategy: Strategy,
) -> bool:

    max_trade_duration_long = strategy.parameters.max_trade_duration_long
    max_trade_duration_short = strategy.parameters.max_trade_duration_short

    if max_trade_duration_long is None and max_trade_duration_short is None:
        return False
    all_trade_durations = [
        (strategy.data.index[-1] - trade.entry_time).days for trade in strategy.trades
    ]
    max_trade_duration = max(all_trade_durations)
    # NOTE here we assume that strategy trades are either all long or all short,
    # i.e. Backtest(hedging=False)
    condition_long = (
        (max_trade_duration_long is not None)
        and (strategy.trades[-1].is_long)
        and (max_trade_duration > max_trade_duration_long)
    )
    condition_short = (
        (max_trade_duration_short is not None)
        and (strategy.trades[-1].is_short)
        and (max_trade_duration > max_trade_duration_short)
    )
    if condition_long or condition_short:
        add_tag_to_trades_and_close_position(
            strategy=strategy, text_to_add=CLOSED_MAX_DURATION
        )
        logging.debug("Closing position because max duration exceeded...")
        return True
    return False


def process_special_situations(
    strategy: Strategy,
) -> Tuple[bool, str]:
    """
    If some special situation (SS) occurred today,
    process it (usually close all trades)
    and return True as a signal to do nothing else today
    """
    # NOTE Recommended actions here are:
    # - Comment out special situations that you don't want to handle.
    # - Add your custom special situations.
    # - Try to change the order in which special situations are handled.

    if process_max_duration(
        strategy=strategy,
    ):
        log_all_trades(strategy=strategy)
        return True, SS_MAX_DURATION

    if process_volatility_spike(strategy=strategy):
        log_all_trades(strategy=strategy)
        return True, SS_VOLATILITY_SPIKE

    if process_partial_close(strategy=strategy):
        log_all_trades(strategy=strategy)
        return True, SS_PARTIAL_CLOSE

    return False, SS_NO_TODAY
