import numpy as np
from backtesting import Strategy
from constants import SL_TIGHTENED


def _get_n_atr(strategy: Strategy) -> float:
    """
    Get ATR multiplier for stop-loss calculation.
    If volatility is high (tr_delta high)
    and current trade is profitable, tighten the stop-loss,
    i.e lower ATR multiplier.
    """
    index = len(strategy.data) - 1
    if (
        strategy.data.tr_delta[index] > 1.98
        and strategy.trades
        and strategy.trades[-1].pl > 0
    ):
        return 1.1
    return 2.5


def update_stop_losses(strategy: Strategy):
    """
    Update stop-losses in all open trades
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
