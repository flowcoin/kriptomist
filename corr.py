import logging
log = logging.getLogger('corr')

import sys
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict
import requests

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


NUM_COINS_DISPLAYED = 20

class Corr:
    URL_ALLPAGE = "https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?convert=USD,BTC&cryptocurrency_type=all&limit={}&sort=market_cap&sort_dir=desc&start=1"
    OFFSET = 0.1
    HISTCOUNT = 100
    
    def __init__(self, pairs=None):
        self.pairs = pairs
        self.set_num_coins()
        self.prices = defaultdict(list)
        self.diffs = defaultdict(list)
        self.lines = {}

    def set_num_coins(self):
        self.num_coins = 0
        if not self.pairs:
            self.pairs = {d["slug"] + "/" + "USD": "b--" for d in requests.get(self.URL_ALLPAGE.format(NUM_COINS_DISPLAYED)).json()["data"]}
        self.all_coins = {d["slug"]: i for i, d in enumerate(requests.get(self.URL_ALLPAGE.format(5000)).json()["data"])}
        for pair in self.pairs:
            coin = pair.split("/")[0]
            if self.all_coins[coin] > self.num_coins:
                self.num_coins = self.all_coins[coin] + 100

    def get_prices(self):
        js = requests.get(self.URL_ALLPAGE.format(self.num_coins)).json()
        for d in js["data"]:
            if (d["slug"] + "/USD") not in self.pairs and (d["slug"] + "/BTC") not in self.pairs:
                continue
            for currency in ["USD", "BTC"]:
                pair = d["slug"] + "/" + currency
                self.prices[pair].append(d["quote"][currency]["price"])            
                if len(self.prices[pair]) > 1:
                    self.diffs[pair].append(
                        100 * (self.prices[pair][-1] - self.prices[pair][-2]) / self.prices[pair][-2]
                    )
                else:
                    self.diffs[pair].append(0)
                
    def live(self):
        plt.ion()

        fig = plt.figure()
        s = [(self.HISTCOUNT+1, 0), (0, 0)]

        plt.plot([a[0] for a in s], [a[1] + self.OFFSET for a in s], "k-.", label="_")
        for i, (pair, style) in enumerate(self.pairs.items()):
            self.lines[pair], = plt.plot([a[0] for a in s], [a[1] - i * self.OFFSET for a in s], style, label=pair)
        plt.plot([a[0] for a in s], [a[1] - len(self.pairs) * self.OFFSET for a in s], "k-.", label="_")

        plt.legend(loc='upper left')

        while True:
            self.get_prices()
    
            for ii, pair in enumerate(self.pairs):
                line = self.lines[pair]
                line.set_data(
                    [iii for iii, a in enumerate(self.diffs[pair][-self.HISTCOUNT:])],
                    [a - ii * self.OFFSET for a in self.diffs[pair][-self.HISTCOUNT:]]
                )
        
            fig.canvas.draw()
            fig.canvas.flush_events()

            time.sleep(4)
            
if __name__ == '__main__':
    coins = sys.argv[1:]
    c = Corr({pair: style for x in coins for pair, style in [x.split(":")]}) 
    c.live()
