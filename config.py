
SLEEP_MIN = 60
SLEEP_MAX = 120

SLEEP_APPROVE_MIN = 10
SLEEP_APPROVE_MAX = 20

TIME_OUT_LIMIT = 120

RETRY = 10

MAX_GAS_PRICE = 5_000_000_000_000 * 1
MAX_GAS_LIMIT = 50_000 * 1
MAX_RETRY = 0

# TRANSFER MODE
MIN_AMOUNT = 0.65
MAX_AMOUNT = 0.80

# INSCRIPTION MODE
INSCRIPTION_TICKER = 'FAIR'  # название инскрипшена  FAIR, ZKFI, FBTC
SELL_BY_FLOOR = True        # продавать по флору
FIX_PRICE = 0.000001        # цена за 1 шт

# COLLECT MODE
WALLET_COLLECT = ''  # ваш кошелек куда надо собрать монеты
AMOUNT_MIN_LEFT_USDC = 1.5       # сколько оставлять на кошельке (в будущем возможны дропы для держателей ЗКФ, я бы оставлял на кошельке 1-2 доллара для клейма)
AMOUNT_MAX_LEFT_USDC = 1.7 
COLLECT_TOKEN = 'ZKF' # 'ZKF', 'USDC'

# Режим работы скрипта: 
# 1. TRANSFER - трансфер монет на много кошельков
# 2. COLLECT - сбор монет на 1 кошелек со  многих кошельков
# 3. INSCRIPTION - продажа инскрипшенов
# 4. INSCRIPTION_ON_ACCOUNT - выводит список кошельков, на которых  хранятся либо выставлены на продажу инскрипшены
MODE = 'COLLECT' # 'TRANSFER', 'COLLECT', 'INSCRIPTION', 'INSCRIPTION_ON_ACCOUNT'