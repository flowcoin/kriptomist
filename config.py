from datetime import datetime, timedelta

DB_FILE = 'kriptomist.sqlite'

NUM_COINS = 10
DATE_START = datetime(2017, 1, 1)

START_DATE_ASTRO = datetime(2016, 1, 1)
STOP_DATE_ASTRO = datetime.now() + timedelta(days=365)
ASTRO_OBJECTS = ['Jupiter', 'Saturn', 'North Node', 'South Node']

SIGNATURE_IN_CHART = True
CHART_SIGNATURE = "github.com/flowcoin/kriptomist"

CHART_METRICS = [
    # Price in USD
    'usd',
    # Price in BTC
    'btc',
    # Circulating supply
    'supply',
    # Subreddit subscribers
    'subs',
    # Twitter followers
    'flw',
    # BTC/USD
    'btcusd',
    # 28 day moving average
    #'ma28',
    # 100 day moving average
    #'ma100',
    # COIN/USD daily price change
    #'xusddiff',
    # BTC/USD daily price change
    #'btcusddiff',
    # BTC/USD correlation to COIN/USD
    #'btcusdxusdcorr',
    # BTC/USD correlation to COIN/BTC
    #'btcusdxbtccorr',
    # COIN/USD next day correlation to BTC/USD
    #'xusdnextdaycorrbtc',
    # COIN/USD prev day correlation to BTC/USD
    #'xusdprevdaycorrbtc',
    # Tether supply
    'tethersupply',
    # Daily transaction count
    #'ntx',
    # Daily transaction count squared
    'ntxsquared',
    # Mining difficulty
    'difficulty',
    # Mining hashrate
    'hashrate',
]

try:
    from local_config import *
except:
    pass

