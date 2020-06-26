import logging
log = logging.getLogger('astro')

import sys
from datetime import datetime, timedelta
from collections import OrderedDict

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

import requests

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from astro_def import COIN_DEF
from coin import Coin

from config import START_DATE_ASTRO, STOP_DATE_ASTRO, ASTRO_OBJECTS

class Astro:
    def __init__(self, coin_name):
        self.coin = Coin(coin_name)
        self.sign = COIN_DEF[coin_name]['sign']   
        self.D = OrderedDict()
        
    def get_angle_on_day(self, o, day):
        global date, pos, chart, obj
        date = Datetime(day.strftime("%Y/%m/%d"), '00:00', '+00:00')
        pos = GeoPos(0, 0)
        chart = Chart(date, pos)
        
        obj = chart.get(o)
        if obj.sign != self.sign:
            return None
        return obj.signlon

    def populate_astro(self):
        day = START_DATE_ASTRO - timedelta(days=1)
        
        for o in ASTRO_OBJECTS:
            self.D[o] = []

        while True:
            day += timedelta(days=1)
            if day > STOP_DATE_ASTRO:
                break
            
            log.debug(day.strftime("%Y/%m/%d"))
            for o, series in self.D.items():
                series.append((day, self.get_angle_on_day(o, day)))

    def populate_prices(self):
        prices = self.coin.cmc.get_prices(START_DATE_ASTRO, STOP_DATE_ASTRO)
        for y, s in prices.items():
            self.D["{}/{}".format(self.coin.name, y)] = normalize(s)

    def draw(self):
        fig = plt.figure()
        fig.show()
        for o, s in self.D.items():
            _plot(s, label=o)
        _draw_end(fig)
    
def _plot(s, label=None):
    plt.plot(
        [a[0] for a in s],
        [a[1] for a in s],
        label=label
    )

def _draw_end(fig):
    plt.legend(loc='upper left')

    ax = fig.axes[0]
    xa = ax.get_xaxis()

    ax.get_xaxis().set_major_locator(mdates.MonthLocator(interval=3))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    
def normalize(s):
    minv = maxv = None
    for a in s:
        if minv is None or a[1] < minv:
            minv = a[1]
        if maxv is None or a[1] > maxv:
            maxv = a[1]
    try:
        return [(a[0], 30*(a[1]-minv)/(maxv-minv)) for a in s]
    except(ZeroDivisionError):
        return [(a[0], 15) for a in s]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    astro = Astro(sys.argv[1])
    astro.populate_astro()
    astro.populate_prices()
    astro.draw()
            

