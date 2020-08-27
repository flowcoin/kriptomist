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
    def __init__(self, sym='BTC', exchanges=exchange.all()):        
        self.sym = sym
        self.exchanges = exchanges
        
        self.prices = defaultdict(list)
        for ex in self.exchanges:
            price = ex.price(sym)
            self.prices[ex].extend([price * 1.01, price * 0.99] + [price] * (HIST_COUNT - 2))
        
        self.lines = {}
        self.threads = {threading.Thread(target=self.price_fetcher, args=(ex,)) for ex in self.exchanges}

    def price_fetcher(self, ex):
        while not STOP:
            t = time.time()
            try:
                price = ex.price(self.sym)
                self.prices[ex].append(price)
                log.info(ex.__name__ + " " + str(price))
            except:
                log.exception(ex.__name__)
                self.prices[ex].append(None)
            dt = time.time() - t
            if dt < 1:
                time.sleep(1 - dt)

    def live(self):
        plt.ion()

        fig = plt.figure()

        for i, ex in enumerate(self.exchanges):
            self.lines[ex], = plt.plot(self.prices[ex], label=ex.__name__)

        plt.legend(loc='upper left')

        while True:
            for i, ex in enumerate(self.exchanges):
                line = self.lines[ex]
                line.set_ydata(self.prices[ex][-HIST_COUNT:])
        
            fig.canvas.draw()
            fig.canvas.flush_events()

            time.sleep(1)            
            
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    abby = Abby()
    for thread in abby.threads:
        thread.start()
    try:
        abby.live()
    except KeyboardInterrupt:
        STOP = True
        raise KeyboardInterrupt()