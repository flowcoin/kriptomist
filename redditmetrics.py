import logging
log = logging.getLogger("redditmetrics")

import json
from datetime import datetime, timedelta
import time

from util import div0, round100, series_fill_zeroes, normalize
from fetcher import Fetcher


URL_SUBS = "https://redditmetrics.com/ajax/compare.reddits"


class Redditmetrics:
    def __init__(self, sub):
        self.sub = sub
        self.init()

    def __repr__(self):
        s = "<rm {}".format(self.sub)
        if self.series:
            s += " ({}, {} subs)".format(self.series[-1][0].strftime("%Y-%m-%d"), self.series[-1][1])
        s += ">"
        return s
        
    def init(self):    
        self.series = []
        if self.sub:
            s = Fetcher(lambda text: json.loads(text)['message']['total']['data']).fetch(
                URL_SUBS, data={'reddit0': self.sub, '_': datetime.now().strftime("%Y_%m_%d")})
            for a in s:
                day = datetime.strptime(a['y'], '%Y-%m-%d')
                if day >= datetime(2018, 1, 1):
                    self.series.append((day, int(a['a'])))            
        series_fill_zeroes(self.series)
        normalize(self, "series")

    def _r(self, days):
        return self.series[-(days+1)][1]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    #d = Fetcher(lambda text: json.loads(text)['message']).fetch(URL_SUBS, data={'reddit0': 'btc', '_': datetime.now().strftime("%Y_%m_%d")})
    
    rm = Redditmetrics("pics")
    
    
