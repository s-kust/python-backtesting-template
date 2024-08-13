from typing import Optional, Tuple

import numpy as np
from backtesting.backtesting import Strategy
from constants import DPS_STUB
from utils.strategy_exec.misc import get_current_position_size

np.random.seed(47)  # to make results reproducible


def get_desired_current_position_size(
    strategy: Strategy,
    strategy_params: Optional[dict] = None,
) -> Tuple[Optional[float], float, str]:
    """
    Extract data from the strategy, as well as from strategy_params,
    calculate the desired position size and return it.
    Also, return the current position size and an explanatory text message.

    Return desired_position_size None - means do nothing today.
    desired_position_size 0 - means close all active trades.
    desired_position_size must be float in [-1.0; 1.0].
    desired_position_size -1.0 - means 100% short;
    desired_position_size 1.0 - means 100% long.
    """
    # NOTE You are expected to work mostly on this function.
    current_position_size = (
        get_current_position_size(
            shares_count=strategy.position.size,
            equity=strategy.equity,
            last_price=strategy._data.Open[-1],
        )
        if strategy.position.size != 0
        else 0
    )
    # NOTE strategy always has some forecast, see Strategy init()
    forecast = strategy.forecast.s.iloc[-1]

    # These are examples of data that you can extract from a strategy
    # and use to calculate the desired position size
    today_date = strategy.forecast.s.index[-1]
    last_trade = strategy.closed_trades[-1] if strategy.closed_trades else None
    current_pl = strategy.trades[-1].pl if strategy.trades else None

    # NOTE momentum_threshold is a fake example of some parameter that you may want to optimize.
    # You can have from zero to a large number of such parameters.

    momentum_threshold = 0.06  # default value
    if strategy_params:
        if (
            "momentum_threshold" in strategy_params
            and strategy_params["momentum_threshold"] is not None
        ):
            momentum_threshold = strategy_params["momentum_threshold"]

    # Below is a stub that you can substitute with your code.
    # If the current position size is not zero,
    # stub returns it as the desired position size.
    # Otherwise, it returns a random float in [-1.0; 1.0]
    # as the desired position size.

    # NOTE Don't forget to remove np.random.seed(47)

    if current_position_size != 0:
        desired_position_size = current_position_size
        return desired_position_size, current_position_size, DPS_STUB

    # random float in [-1.0; 1.0]
    desired_position_size = np.random.random() * 2 - 1
    return desired_position_size, current_position_size, DPS_STUB
