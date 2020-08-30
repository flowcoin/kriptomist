import logging
log = logging.getLogger('abby')

import sys
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict
import threading

import requests

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from sources import exchange

STOP = False

HIST_COUNT = 100

class Abby:
    def __init__(self, sym='BTC', exchanges=exchange.all(), show_more=[exchange.Livecoin]):
        self.sym = sym
        self.exchanges = exchanges
        self.show_more = show_more
        
        self.prices = defaultdict(list)
        for ex in self.exchanges:
            price = ex.price(sym)
            for key in [(ex, 'price'), (ex, 'bid'), (ex, 'ask')]:
                if key[1] != 'price' and key[0] not in self.show_more:
                    continue
                self.prices[key].extend([price * 1.01, price * 0.99] + [price] * (HIST_COUNT - 2))
        
        self.lines = {}
        self.threads = {threading.Thread(target=self.price_fetcher, args=(ex,)) for ex in self.exchanges}

    def price_fetcher(self, ex):
        if ex in self.show_more:
            return self.price_data_fetcher(ex)
        while not STOP:
            t = time.time()
            try:
                price = ex.price(self.sym)
                self.prices[(ex, 'price')].append(price)
                log.info(ex.__name__ + " " + str(price))
            except:
                log.exception(ex.__name__)
                self.prices[(ex, 'price')].append(None)
            dt = time.time() - t
            if dt < 1:
                time.sleep(1 - dt)

    def price_data_fetcher(self, ex):
        while not STOP:
            t = time.time()
            try:
                data = ex.price_data(self.sym)
                self.prices[(ex, 'price')].append(data['price'])
                self.prices[(ex, 'bid')].append(data['bid'])
                self.prices[(ex, 'ask')].append(data['ask'])
                log.info(ex.__name__ + " " + str(data['price']))
            except:
                log.exception(ex.__name__)
                self.prices[ex].append(None)
            dt = time.time() - t
            if dt < 1:
                time.sleep(1 - dt)
        

    def live(self):
        plt.ion()

        fig = plt.figure()

        for i, ((ex, typ), prices) in enumerate(self.prices.items()):
            style = {'bid': 'k:', 'ask': 'k--'}.get(typ, '-')
            self.lines[(ex, typ)], = plt.plot(prices, style, label=ex.__name__ + " " + typ)
                    
        plt.legend(loc='upper left')

        while True:
            for i, ((ex, typ), prices) in enumerate(self.prices.items()):
                line = self.lines[(ex, typ)]
                line.set_ydata(self.prices[(ex, typ)][-HIST_COUNT:])
            
                fig.canvas.draw()
                fig.canvas.flush_events()

            time.sleep(1)            
            
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    
    abby = Abby()
    for thread in abby.threads:
        thread.start()
    try:
        abby.live()
    except:
        log.exception('main')
        STOP = True
