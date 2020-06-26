from datetime import datetime, timedelta

NUM_COINS = 10
DATE_START = datetime(2018, 1, 1)

START_DATE_ASTRO = datetime(2016, 1, 1)
STOP_DATE_ASTRO = datetime.now() + timedelta(days=365)
ASTRO_OBJECTS = ['Jupiter', 'Saturn', 'North Node', 'South Node']

try:
    from local_config import *
except:
    pass

