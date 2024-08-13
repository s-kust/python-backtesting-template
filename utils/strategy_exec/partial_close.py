import logging
import math
from typing import Optional

from backtesting import Strategy
from constants import TRADE_ALREADY_HALF_CLOSED

from .misc import add_tag_to_trades_and_close_position


def get_avg_sl_for_all_open_trades(strategy: Strategy) -> Optional[float]:
    """
    Get average stop-loss for all open trades
    """
    res = 0.0
    for trade in strategy.trades:

        if not trade.sl or trade.sl <= 0:
            logging.debug(
                f"get_avg_stop_loss: {trade} - no trade.sl or trade.sl <= 0, return None"
            )
            return None

        # check for abnormal situations
        # if trade.is_long and trade.sl >= strategy._broker.last_price:
        #     print(
        #         f"get_avg_stop_loss: {trade} - trade.is_long and trade.sl >= self._broker.last_price, return None"
        #     )
        #     return None
        # if trade.is_short and trade.sl <= strategy._broker.last_price:
        #     print(
        #         f"get_avg_stop_loss: {trade} - trade.is_short and trade.sl <= self._broker.last_price, return None"
        #     )
        #     return None

        res += (abs(trade.size) / abs(strategy.position.size)) * trade.sl
    return res


def _process_partial_close(strategy: Strategy, avg_stop_loss: float) -> bool:
    _, size_to_close = math.modf(abs(strategy.position.size) / 2)
    size_to_close = int(size_to_close)
    size_to_remain: int = abs(strategy.position.size) - size_to_close
    potential_losses: float = (
        abs(avg_stop_loss - strategy._broker.last_price) * size_to_remain
    )
    profit_to_take_now: float = (
        size_to_close / abs(strategy.position.size)
    ) * strategy.position.pl
    logging.debug(
        f"_process_partial_close: {avg_stop_loss=}, {size_to_close=}, {size_to_remain=}, {profit_to_take_now=}, {potential_losses=}"
    )
    if profit_to_take_now > potential_losses:
        return True
    return False


def process_partial_close(strategy: Strategy) -> bool:
    """
    Close half of position to make the rest risk-free
    """
    if strategy.position.pl < 0:
        return False

    if strategy.trades[-1].tag and TRADE_ALREADY_HALF_CLOSED in strategy.trades[-1].tag:
        logging.debug("Trades already partially closed, do nothing else today...")
        return True

    avg_stop_loss = get_avg_sl_for_all_open_trades(strategy)
    if avg_stop_loss is None:
        return False
    close_part_now = _process_partial_close(
        strategy=strategy, avg_stop_loss=avg_stop_loss
    )
    if close_part_now:
        logging.debug("Here self.position.close partially")
        add_tag_to_trades_and_close_position(
            strategy=strategy,
            text_to_add=TRADE_ALREADY_HALF_CLOSED,
            portion_to_close=0.5,
        )
        return True
    return False
