"""
== Kriptomist OLD ==

Analyze flow in the world of crypto.
"""

import logging
log = logging.getLogger('kriptomist_old')

import sys
from pprint import pprint

from coinmarketcap import Coinmarketcap
from redditmetrics import Redditmetrics
from util import div0, dump_html_old, km_to_dictlist
import draw
from db import Db

class Kriptomist:
    def __init__(self, cmc, srs):
        self.cmc = cmc
        self.srs = srs
        self.compute_stats()
        
    def compute_stats(self):
        cmc = self.cmc
        srs = self.srs
        
        self.price = cmc._p(0)
        self.subs = srs._r(0)
        
        # cmc
        self.price28 = self.price - cmc._p(28)
        self.price28_rel = div0(self.price, cmc._p(28))
        
        # reddit
        self.subs28 = self.subs - srs._r(28)
        self.subs7 = self.subs - srs._r(7)
        self.subs1 = self.subs - srs._r(1)

        self.subs28_rel = div0(self.subs, srs._r(28))
        self.subs7_rel = div0(self.subs, srs._r(7))
        self.subs1_rel = div0(self.subs, srs._r(1))
        
        self.subs7_acc = div0( (self.subs7_rel * 4 - 3), self.subs28_rel )
        self.subs1_acc = div0( (self.subs1_rel * 7 - 6), self.subs7_rel )
        
        # compare
        self.cmp28 = div0(self.subs28_rel**2, self.price28_rel)
        self.cmp7 = div0(self.subs7_rel**2, (3 + self.price28_rel) / 4)
        self.cmp1 = div0(self.subs1_rel**2, (27 + self.price28_rel) / 28)

        # score
        self.score = self.cmp28 * (self.subs1_acc ** 4) * (self.subs7_acc ** 2)

    def display(self):
        print("[#{}: {}]".format(self.cmc.rank, self.cmc.coin))
        pprint(self.__dict__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    if sys.argv[1:]:
        coin = sys.argv[1]
        cmc = Coinmarketcap(coin)
        cmc.fetch_prices()
        srs = Redditmetrics(cmc.sub)
        km = Kriptomist(cmc, srs)
        km.display()
        draw.draw_old(km)
    else:
        KMS = []
        coins = Coinmarketcap.list_coins()
        for i, coin in enumerate(coins):
            try:
                cmc = Coinmarketcap(coin["slug"], data=coin)
                cmc.fetch_prices()
                srs = Redditmetrics(cmc.sub)
                km = Kriptomist(cmc, srs)
                km.display()
                KMS.append(km)
            except:
                log.exception("Skipping {}".format(coin))
        dump_html_old(KMS)
        
        from db import Db
        
        for i, km in enumerate(KMS):
            db = Db(km.cmc.coin)
            log.debug("#{}: Writing {}".format(i, km.cmc.coin))
            for d in km_to_dictlist(km):
                db.write_data(d)
    
