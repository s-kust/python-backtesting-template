import logging

from backtesting import Strategy
from constants import (
    ACTION_BUY,
    ACTION_CLOSE_POSITION,
    ACTION_DO_NOTHING,
    ACTION_SELL,
    ACTION_SHARE_COUNT_0,
    CLOSED_SIDE_CHANGE,
)

from .misc import get_shares_count, log_all_trades


def adjust_position(
    strategy: Strategy, current_position_size: float, desired_size: float
) -> str:
    """
    Calculate the difference between current and desired position size
    and adjust position in the given strategy accordingly.
    """
    if desired_size is None:
        log_all_trades(strategy=strategy)
        return ACTION_DO_NOTHING

    if desired_size == 0:
        logging.debug("filtered_desired_size == 0")
        log_all_trades(strategy=strategy)
        if strategy.trades:
            strategy.position.close()
        return ACTION_CLOSE_POSITION

    position_size_delta = desired_size - current_position_size
    if position_size_delta == 0:
        log_all_trades(strategy=strategy)
        return ACTION_DO_NOTHING

    # If position long / short side changes,
    # all active trades will be closed now.
    # Log it in their tags.
    if (desired_size * current_position_size) < 0:
        for trade in strategy.trades:
            attr = f"_{trade.__class__.__qualname__}__tag"
            setattr(trade, attr, (trade.tag or "") + CLOSED_SIDE_CHANGE)

    # NOTE better don't try to simplify it
    # because it may lead to errors and wrong results
    if abs(position_size_delta) >= 1:
        strategy.position.close()
        shares_count = get_shares_count(
            equity=strategy.equity,
            position_size_delta=abs(desired_size),
            last_price=strategy.data.Close[-1],
        )
    else:
        shares_count = get_shares_count(
            equity=strategy.equity,
            position_size_delta=abs(position_size_delta),
            last_price=strategy.data.Close[-1],
        )

    if shares_count == 0:
        logging.debug(f"ZERO {shares_count=}, so DO NOTHING")
        log_all_trades(strategy=strategy)
        return ACTION_SHARE_COUNT_0

    if position_size_delta > 0:
        strategy.buy(size=shares_count)
        logging.debug(f"BUY {position_size_delta=}, {shares_count=}")
        log_all_trades(strategy=strategy)
        return ACTION_BUY
    else:
        strategy.sell(size=shares_count)
        logging.debug(f"SELL {position_size_delta=}, {shares_count=}")
        log_all_trades(strategy=strategy)
        return ACTION_SELL
