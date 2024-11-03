from typing import Optional, Tuple

from backtesting.backtesting import Strategy

from constants import DPS_STUB
from utils.strategy_exec.misc import get_current_position_size


def get_desired_current_position_size(
    strategy: Strategy,
) -> Tuple[Optional[float], float, str]:
    """
    Extract data from the strategy, as well as from strategy_params,
    calculate the desired position size and return it.
    Also, return the current position size and an explanatory text message.

    Return desired_position_size None - means do nothing today.
    desired_position_size 0 - means close all active trades.
    desired_position_size must be float in [-1.0; 1.0].
    desired_position_size -1.0 - 100% short;
    desired_position_size 1.0 - 100% long.
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

    # These are examples of data that you can extract from a strategy
    # and use to calculate the desired position size
    today_date = strategy._data.index[-1]
    last_trade = strategy.closed_trades[-1] if strategy.closed_trades else None
    current_pl = strategy.trades[-1].pl if strategy.trades else None

    # NOTE param_1 and param_2 are fake examples
    # of some parameters that you may use
    # to calculate the desired position size.
    # You can have from zero to a large number of such parameters.
    # See also the internals of the class StrategyParams.

    # default values
    param_1 = 1.3
    param_2 = 2

    if (
        hasattr(strategy.parameters, "param_1")
        and strategy.parameters.param_1 is not None
    ):
        param_1 = strategy.parameters.param_1
    if (
        hasattr(strategy.parameters, "param_2")
        and strategy.parameters.param_2 is not None
    ):
        param_2 = strategy.parameters.param_2

    # Below is a simplified educational example
    # that you will substitute with your code.

    # If the current position size is not zero,
    # the function returns it as the desired position size.
    # The settings of the stop losses, take profits,
    # maximum duration of the trades, and processing of special situations
    # will take care about the timely closing of the position.

    # If the current position size is zero,
    # the function may order the system
    # to take a 100% long position depending on condition.

    desired_position_size: Optional[float] = None

    if current_position_size != 0:
        desired_position_size = current_position_size
        return desired_position_size, current_position_size, DPS_STUB

    # NOTE see details of feature_advanced
    # inside the add_features_v1_basic function
    if strategy._data.feature_advanced[-1] == True:
        desired_position_size = 1.0
    # otherwise, it remains None, i.e. signal do nothing

    return desired_position_size, current_position_size, DPS_STUB
