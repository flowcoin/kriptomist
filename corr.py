import logging
log = logging.getLogger('corr')

import time
import random
from datetime import datetime, timedelta
from collections import defaultdict
import requests

import numpy as np
import matplotlib.pyplot as plt

from draw import _draw_end


NUM_COINS = 20
URL_ALLPAGE = "https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?convert=USD,BTC&cryptocurrency_type=all&limit={}&sort=market_cap&sort_dir=desc&start=1".format(NUM_COINS)

COINS = []
for d in requests.get(URL_ALLPAGE).json()["data"]:
    COINS.append(d["slug"])

PRICES = defaultdict(list)
DIFFS = defaultdict(list)

LINES = {}

OFFSET = 0.1
HISTCOUNT = 100

def get_prices():
    js = requests.get(URL_ALLPAGE).json()
    for d in js["data"]:        
        PRICES[d["slug"]].append(d["quote"]["USD"]["price"])
        if len(PRICES[d["slug"]]) > 1:
            DIFFS[d["slug"]].append( 100 * (PRICES[d["slug"]][-1] - PRICES[d["slug"]][-2]) / PRICES[d["slug"]][-2] )
        else:
            DIFFS[d["slug"]].append(0)
plt.ion()

fig = plt.figure()
#ax = fig.add_subplot(111)

s = [(HISTCOUNT+1, 0), (0, 0)]

plt.plot([a[0] for a in s], [a[1] + OFFSET for a in s], label="_")
for i, coin in enumerate(COINS):
    LINES[coin], = plt.plot([a[0] for a in s], [a[1] - i * OFFSET for a in s], label=coin)
plt.plot([a[0] for a in s], [a[1] - len(COINS) * OFFSET for a in s], label="_")

plt.legend(loc='upper left')
#_draw_end(fig)

while True:
    get_prices()
    
    for ii, coin in enumerate(COINS):
        line = LINES[coin]
        line.set_data(
            [iii for iii, a in enumerate(DIFFS[coin][-HISTCOUNT:])],
            [a - ii * OFFSET for a in DIFFS[coin][-HISTCOUNT:]]
        )
        
    fig.canvas.draw()
    fig.canvas.flush_events()

    time.sleep(1)

"""
x = np.linspace(0, 6*np.pi, 100)
y = np.sin(x)

# You probably won't need this if you're embedding things in a tkinter plot...
plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot(x, y, 'r-') # Returns a tuple of line objects, thus the comma

for phase in np.linspace(0, 10*np.pi, 500):
    line1.set_ydata(np.sin(x + phase))
    fig.canvas.draw()
    fig.canvas.flush_events()
"""

"""
fig = plt.figure()
fig.show()

day = datetime.now()
plt.plot(day, 1, label="test")
_draw_end(fig)

for i in range(10):
    
    plt.plot(day + timedelta(days=i), 10, label="test", marker="o")
    plt.pause(0.05)
"""
