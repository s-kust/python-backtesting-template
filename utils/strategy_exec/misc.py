import inspect
import logging
import math
from typing import List, Optional

from backtesting import Strategy
from backtesting.backtesting import Trade


def add_tag_to_trades_and_close_position(
    strategy: Strategy, text_to_add: str, portion_to_close: float = 1.0
):
    for trade in strategy.trades:
        attr = f"_{trade.__class__.__qualname__}__tag"
        setattr(trade, attr, (trade.tag or "") + text_to_add)
    strategy.position.close(portion=portion_to_close)


def trade_custom_repr(strategy: Strategy, trade: Trade):
    duration = (strategy.data.index[-1] - trade.entry_time).days
    price = round(trade.entry_price, 2)
    pl = round(trade.pl, 2)
    sl = round(trade.sl, 2) if trade.sl is not None else None
    tp = round(trade.tp, 2) if trade.tp is not None else None
    tag = trade.tag if trade.tag is not None else ""
    return f"<Trade size={trade.size}, price={price}, pl={pl}, sl={sl}, tp={tp}, duration={duration} days, tag={tag}>"


def log_all_trades(strategy: Strategy):
    for trade in strategy.trades:
        logging.debug(trade_custom_repr(strategy=strategy, trade=trade))


def get_current_position_size(
    shares_count: int, equity: float, last_price: float
) -> float:
    """
    Return current position size as a fraction of equity
    """
    if not int(shares_count) == shares_count:
        raise ValueError(
            f"get_current_position_size: input {shares_count=} should be integer number"
        )
    if not equity >= 0:
        raise ValueError(f"get_current_position_size: input {equity=} should be >= 0")
    return round(shares_count * last_price / equity, 2)


def all_current_trades_info(strategy: Strategy) -> Optional[List[dict]]:
    if not strategy.trades:
        return None
    all_current_trades = list()
    for trade in strategy.trades:
        all_current_trades.append(
            {
                "size": trade.size,
                "entry_time": trade.entry_time,
                "entry_price": round(trade.entry_price, 2),
                "tag": trade.tag,
                "pl": round(trade.pl, 2),
            }
        )
    return all_current_trades


def retrieve_variable_name(var) -> str:
    # NOTE it is for calling from another functions,
    # not from main script,
    # see https://stackoverflow.com/a/18425523/3139228
    callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()  # type: ignore
    return [var_name for var_name, var_val in callers_local_vars if var_val is var][0]


def get_shares_count(equity: float, position_size_delta: float, last_price: float):
    if (
        position_size_delta <= 0
        or position_size_delta > 1
        or not isinstance(position_size_delta, float)
    ):
        raise ValueError(
            f"get_shares_count: input {position_size_delta=} must be float in (0.0; 1.0]"
        )
    if equity <= 0:
        raise ValueError(f"get_shares_count: input {equity=} must be float > 0")

    if last_price <= 0:
        raise ValueError(f"get_shares_count: input {last_price=} must be float > 0")

    res = (equity * position_size_delta) / last_price
    _, whole = math.modf(res)
    return whole


def log_initial_data_for_today(strategy: Strategy, ticker: str):
    logging.debug(f"{ticker=}, today's date {strategy.forecast.s.index[-1]}")
    logging.debug(f"shares_count {strategy.position.size}")
    logging.debug(f"today's open price {strategy._data.Open[-1]}")
    logging.debug(f"equity {strategy.equity}")
    logging.debug(f"tr_delta {strategy.data.tr_delta[-1]}")
    logging.debug(f"forecast {strategy.forecast.s.iloc[-1]}")
