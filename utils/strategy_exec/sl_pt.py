from typing import Optional

import numpy as np
from backtesting import Strategy

from constants import SL_TIGHTENED

# sl_pt -> stop-losses and profit targets


def _get_n_atr(strategy: Strategy) -> float:
    """
    Get ATR multiplier for stop-loss calculation.
    If volatility is high (tr_delta high)
    and current trade is profitable, tighten the stop-loss,
    i.e lower ATR multiplier to 1.1.
    """
    index = len(strategy.data) - 1
    if (
        strategy.data.tr_delta[index] > 1.98
        and strategy.trades
        and strategy.trades[-1].pl > 0
    ):
        return 1.1
    return strategy.parameters.stop_loss_default_atr_multiplier


def update_stop_losses(strategy: Strategy):
    """
    Update trailing stop-losses in all open trades. 
    This function is called daily by the next() function of your strategy.
    In normal situations, trailing stop-loss is equal 
    to Average True Range 50 multiplied by 2.5 
    (strategy.parameters.stop_loss_default_atr_multiplier). 
    If volatility spike is detected (tr_delta > 1.98), 
    the stop-loss is tightened, 
    i.e. the multiplier is reduced from 2.5 to 1.1.
    """
    if strategy.trades is None:
        return
    n_atr = _get_n_atr(strategy=strategy)
    index = len(strategy.data) - 1
    for trade in strategy.trades:
        if trade.is_long:
            sl_price = max(
                trade.sl or -np.inf,
                strategy.data.Open[index] - strategy.atr[index] * n_atr,
            )
        else:
            sl_price = min(
                trade.sl or np.inf,
                strategy.data.Open[index] + strategy.atr[index] * n_atr,
            )
        if sl_price < 0:
            sl_price = None
        if sl_price and (trade.sl != sl_price):
            trade.sl = sl_price
            if n_atr == 1.1 and SL_TIGHTENED not in (trade.tag or ""):
                attr = f"_{trade.__class__.__qualname__}__tag"
                setattr(trade, attr, (trade.tag or "") + SL_TIGHTENED)


def check_set_profit_targets_long_trades(strategy: Strategy):
    """
    Set profit target in all long trades where it is None
    """

    # NOTE 
    # This function uses strategy.parameters.profit_target_long_pct. 
    # Call this function only after you have made sure 
    # that strategy.parameters.profit_target_long_pct is not None. 
    # See in the run_backtest_for_ticker.py file 
    # how it is done inside the next() function of the strategy.

    last_price = strategy._data.Open[-1]
    min_profit_target_long: Optional[float] = None
    trades_long = [trade for trade in strategy.trades if trade.is_long]

    for trade in trades_long:
        if trade.tp is not None:
            if min_profit_target_long is None:
                min_profit_target_long = trade.tp
            else:
                min_profit_target_long = min(min_profit_target_long, trade.tp)

    if trades_long:
        if min_profit_target_long is None:
            min_profit_target_long = (
                float(strategy.parameters.profit_target_long_pct + 100) / 100
            ) * last_price
        for trade in trades_long:
            if trade.tp is None:
                trade.tp = min_profit_target_long


def check_set_profit_targets_short_trades(strategy: Strategy):
    """
    Set profit target in all short trades where it is None
    """

    # NOTE 
    # This function uses strategy.parameters.profit_target_short_pct. 
    # Call this function only after you have made sure 
    # that strategy.parameters.profit_target_short_pct is not None. 
    # See in the run_backtest_for_ticker.py file 
    # how it is done inside the next() function of the strategy.

    last_price = strategy._data.Open[-1]
    max_profit_target_short: Optional[float] = None
    trades_short = [trade for trade in strategy.trades if not trade.is_long]

    for trade in trades_short:
        if trade.tp is not None:
            if max_profit_target_short is None:
                max_profit_target_short = trade.tp
            else:
                max_profit_target_short = max(max_profit_target_short, trade.tp)

    if trades_short:
        if max_profit_target_short is None:
            max_profit_target_short = (
                float(100 - strategy.parameters.profit_target_short_pct) / 100
            ) * last_price
        for trade in trades_short:
            if trade.tp is None:
                trade.tp = max_profit_target_short
