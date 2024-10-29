LOCAL_FOLDER = "/tmp/"

TICKER_DATA_RAW_FILENAME_PREFIX = "single_raw_"
TICKER_DATA_W_FEATURES_FILENAME_PREFIX = "single_with_features_"
DATA_FILES_EXTENSION = ".xlsx"

TRADE_ALREADY_HALF_CLOSED = "; partially_closed"
CLOSED_VOLATILITY_SPIKE = "; closed_due to volatility spike"
CLOSED_SIDE_CHANGE = "; closed_due to forecast side change"
CLOSED_HAMMER = "; closed_due to hammer candle"
CLOSED_SHOOTING_STAR = "; closed_due to shooting star candle"
CLOSED_MAX_DURATION = "; closed because max duration exceeded"
SL_TRIGGERED = "; stop-loss triggered"
TP_TRIGGERED = "; take profit triggered"
SL_TIGHTENED = "; stop-loss tightened during volatility spike"

# SS - special situation
SS_NO_TODAY = "No special situation today"
SS_PARTIAL_CLOSE = "SS Partial close"
SS_HAMMER = "SS Hammer"
SS_SHOOTING_STAR = "SS Shooting star"
SS_VOLATILITY_SPIKE = "SS Volatility spike"
SS_OVERBOUGHT_OVERSOLD = "SS Overbought / Oversold"
SS_MAX_DURATION = "SS Max trade duration exceeded"

# DPS - desired position size
DPS_NO_START_HIGH_VOLATILITY = "DPS Don't start new position when high ATR"
DPS_NO_ADD_HIGH_VOLATILITY = "DPS Don't add to position when high ATR"
DPS_NO_START_HIGH_MTUM = "DPS Don't start new position when high momentum"
DPS_WAIT_SL_TRIGGERED_TODAY = "DPS last_trade stop loss triggered today, wait"
DPS_WAIT_VOLATILITY_SPIKE = "DPS Last trade was closed volatility spike, wait"
DPS_WAIT_SL_SAME_SIDE = "DPS Last trade closed SL. To enter the same side, wait"
DPS_WAIT_SHOOTING_STAR = "DPS Last trade was closed shooting star, wait to get long"
DPS_WAIT_HAMMER = "DPS Last trade was closed hammer, wait to get short"
DPS_TAKE_BET = "DPS risk/reward is good, take the bet"
DPS_BAD_RR_PASS = "DPS risk/reward is bad, pass"
DPS_BAD_RR_NO_ADD = "DPS risk/reward is bad, don't add to trades"
DPS_NO_CLOSE_LOSERS = "DPS no partial close of loosing trades"
DPS_ADD_WINNER_YES = "DPS add to winner in good R/R - YES"
DPS_ADD_WINNER_NO = "DPS add to winner in good R/R - NO"
DPS_MAIN_FLOW_YES = "DPS Main flow - yes"
DPS_MAIN_FLOW_NO = "DPS Main flow - no"
DPS_STUB = "DPS get_desired_current_position_size stub"

tickers_all = [
    "GLD",
    "SLV",
    "USO",
    "WEAT",
    "SOYB",
    "SPY",
    "ARKK",
    "QQQ",
    "CORN",
    "GDX",
    "XME",
    "TLT",
]
tickers_precious = [
    "GLD",
    "SLV",
    "GDX",
]
tickers_commodities = [
    "USO",
    "WEAT",
    "SOYB",
    "CORN",
]
tickers_stocks = [
    "SPY",
    "ARKK",
    "QQQ",
    "XME",
]


LOG_FILE = "app_run.log"

ACTION_BUY = "Buy"
ACTION_SELL = "Sell"
ACTION_DO_NOTHING = "Do nothing"
ACTION_CLOSE_POSITION = "Close position"
ACTION_SHARE_COUNT_0 = "Shares count 0"

BOOTSTRAP_CONFIDENCE_LEVEL = 0.95

NUM_DAYS_FWD_RETURN = 4
