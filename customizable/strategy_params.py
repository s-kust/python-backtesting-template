from dataclasses import dataclass
from typing import Optional


@dataclass
class StrategyParams:
    # NOTE Here you can customize the set of fields,
    # their types and default values.
    max_trade_duration_long: Optional[int] = 100
    max_trade_duration_short: Optional[int] = 100
    profit_target_pct: Optional[float] = 29.9
    stop_loss_default_atr_multiplier: Optional[float] = 2.5
    save_all_trades_in_xlsx: bool = False
