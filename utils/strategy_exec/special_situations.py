import logging
from typing import Optional, Tuple

from backtesting import Strategy

from constants import (
    CLOSED_HAMMER,
    CLOSED_MAX_DURATION,
    CLOSED_SHOOTING_STAR,
    CLOSED_VOLATILITY_SPIKE,
    SS_HAMMER,
    SS_MAX_DURATION,
    SS_NO_TODAY,
    SS_OVERBOUGHT_OVERSOLD,
    SS_PARTIAL_CLOSE,
    SS_SHOOTING_STAR,
    SS_VOLATILITY_SPIKE,
    TP_TRIGGERED,
)
from features.hammer import check_hammer_candle
from features.shooting_star import check_shooting_star_candle

from .misc import add_tag_to_trades_and_close_position, log_all_trades
from .partial_close import process_partial_close


def process_overbought_oversold(strategy: Strategy) -> bool:
    """
    Take profit if yesterday close price
    was above Bollinger band (abs(yesterday_forecast) > 2.1)
    and today abs(today_forecast) < abs(yesterday_forecast).
    """

    # TODO split to two special situations: overbought and oversold,
    # process them separately and test

    if strategy.trades:

        # NOTE This is worse than using PnL of the last trade
        # current_pl = sum([trade.pl for trade in self.trades])

        current_pl = strategy.trades[-1].pl
    else:
        return False

    today_forecast = strategy.forecast.s.iloc[-1]
    yesterday_forecast = strategy.forecast.s.iloc[-2]
    if (
        (abs(yesterday_forecast) > 2.1)
        and (abs(today_forecast) < abs(yesterday_forecast))
        and current_pl
        and current_pl > 0
    ):
        logging.debug("Here take profit")
        add_tag_to_trades_and_close_position(
            strategy=strategy, text_to_add=TP_TRIGGERED
        )
        return True
    return False


def process_shooting_star(strategy: Strategy) -> bool:
    """
    return True - do nothing else today
    return False - continue executing next()
    """
    is_shooting_star = check_shooting_star_candle(
        yesterday_high=strategy._data.High[-2],
        yesterday_low=strategy._data.Low[-2],
        yesterday_close=strategy._data.Close[-2],
        today_high=strategy._data.High[-1],
        today_low=strategy._data.Low[-1],
        today_open=strategy._data.Open[-1],
        today_close=strategy._data.Close[-1],
    )
    if not is_shooting_star:
        return False
    if strategy.position and strategy.position.size > 0:
        logging.debug("Close long position because shooting star today")
        add_tag_to_trades_and_close_position(
            strategy=strategy, text_to_add=CLOSED_SHOOTING_STAR
        )
        return True

    # don't take long position when shooting star
    if strategy.forecast.s.iloc[-1] > 0:
        logging.debug("Don't take long position when shooting star, do nothing today")
        return True

    # NOTE is_shooting_star and forecast < 0 - OK,
    # return False to continue processing
    return False


def process_hammer(strategy: Strategy) -> bool:
    """
    return True - do nothing else today
    return False - continue executing next()
    """
    is_hammer = check_hammer_candle(
        yesterday_high=strategy._data.High[-2],
        yesterday_low=strategy._data.Low[-2],
        yesterday_close=strategy._data.Close[-2],
        today_high=strategy._data.High[-1],
        today_low=strategy._data.Low[-1],
        today_open=strategy._data.Open[-1],
        today_close=strategy._data.Close[-1],
    )
    if not is_hammer:
        return False
    if strategy.position and strategy.position.size < 0:
        logging.debug("Close short position because hammer candle today")
        add_tag_to_trades_and_close_position(
            strategy=strategy, text_to_add=CLOSED_HAMMER
        )
        return True

    # don't take short position when hammer candle
    if strategy.forecast.s.iloc[-1] < 0:
        logging.debug("Don't take short position when hammer candle, do nothing today")
        return True

    # NOTE is_hammer and forecast > 0 - OK,
    # return False to continue processing
    return False


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

    # if process_overbought_oversold(strategy=strategy):
    #     log_all_trades(strategy=strategy)
    #     return True, SS_OVERBOUGHT_OVERSOLD

    if process_volatility_spike(strategy=strategy):
        log_all_trades(strategy=strategy)
        return True, SS_VOLATILITY_SPIKE

    # NOTE shooting_star doesn't work,
    # so don't check it, maybe later
    # use it as a signal to get long

    # if process_shooting_star(strategy=strategy):
    #     log_all_trades(strategy=strategy)
    #     return True, SS_SHOOTING_STAR

    if process_hammer(strategy=strategy):
        log_all_trades(strategy=strategy)
        return True, SS_HAMMER

    if process_partial_close(strategy=strategy):
        log_all_trades(strategy=strategy)
        return True, SS_PARTIAL_CLOSE

    return False, SS_NO_TODAY
