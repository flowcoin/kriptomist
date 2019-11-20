import logging
log = logging.getLogger("subredditstats")

import json
from datetime import datetime, timedelta
import time

from util import div0, round100, series_fill_zeroes, normalize
from fetcher import Fetcher


URL_SUBS = "https://subredditstats.com/api/subreddit?name={}&project=subscriberCountTimeSeries&_={}"


class Subredditstats:
    def __init__(self, sub):
        self.sub = sub
        self.init()
        
    def init(self):    
        self.series = []
        if self.sub is not None:
            s = Fetcher(lambda text: json.loads(text)['subscriberCountTimeSeries']).fetch(
                URL_SUBS.format(self.sub, datetime.now().strftime("%Y_%m_%d")))
            for a in s:
                day = datetime(1970, 1, 1) + timedelta(days=a['utcDay'])
                if day >= datetime(2018, 1, 1):
                    self.series.append((day, a['count']))            
        series_fill_zeroes(self.series)
        normalize(self, "series")

    def _r(self, days):
        return self.series[-(days+2)][1]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    srs = Subredditstats("btc")
    print(srs.series)

