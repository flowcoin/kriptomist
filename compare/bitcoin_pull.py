import sys
from datetime import datetime, timedelta
import math

from coin import Coin
import util
from util import div0

import config
import draw

if __name__ == '__main__':
    btc = Coin('bitcoin')
    coin = Coin(sys.argv[1])
    
    btc_usd = util.series_to_dict(btc.usd)
    coin_usd = util.series_to_dict(coin.usd)
    
    series_up = []
    series_down = []
    
    t = config.DATE_START - timedelta(days=1)
    while t < datetime.now():
        t += timedelta(days=1)
        
        btc_now = btc_usd.get(t)
        coin_now = coin_usd.get(t)
        
        if not btc_now or not coin_now:
            series_up.append((t, None))
            series_down.append((t, None))
            continue

        btc_prev = btc_usd.get(t - timedelta(days=1))
        coin_prev = coin_usd.get(t - timedelta(days=1))
        
        if not btc_prev or not coin_prev:
            series_up.append((t, None))
            series_down.append((t, None))
            continue
    
        coin_diff = (coin_now - coin_prev) / coin_prev
        btc_diff = (btc_now - btc_prev) / btc_prev
        diff = 100 * (coin_diff - btc_diff)
    
        if btc_now > btc_prev:
            series_up.append((t, diff))
            series_down.append((t, None))
        else:
            series_up.append((t, None))
            series_down.append((t, diff))
    
    draw.draw_custom_dots({coin.name: coin.usd_norm, 'bitcoin': btc.usd_norm, 'up': series_up, 'down': series_down})