"""
== Kriptomist ==

Analyze flow in the world of crypto.
"""

import logging
log = logging.getLogger('kriptomist')

import sys
from pprint import pprint

from coinmarketcap import Coinmarketcap
from redditmetrics import Redditmetrics
from util import div0, dump_html
from draw import draw

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
        srs = Redditmetrics(cmc.sub)
        km = Kriptomist(cmc, srs)
        km.display()
        draw(km)
    else:
        KMS = []
        coins = Coinmarketcap.list_coins()
        for i, coin in enumerate(coins):
            try:
                cmc = Coinmarketcap(coin, rank=i+1)
                srs = Redditmetrics(cmc.sub)
                km = Kriptomist(cmc, srs)
                km.display()
                KMS.append(km)
            except:
                log.exception("Skipping {}".format(coin))
        dump_html(KMS)
        
    
