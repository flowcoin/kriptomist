""" Money usd mcap class 
"""

import logging
log = logging.getLogger('money')

import sys
from datetime import datetime

import requests

import db
import draw
import util
import config
from sources.blockchain_com import BlockchainCom


class Money:
    def __init__(self, db_key, currency, date_start=datetime(2009, 1, 3), date_stop=util.today(), tx=BlockchainCom.fetch_data("n-transactions")):
        self.S = util.Series(date_start=date_start, date_stop=date_stop)
        self.db_key = db_key
        self.currency = currency
        self.db = db.Db(self.db_key)
        
        self.tx = self.S.prepare(tx)
        if currency == 'USD':
            self.usd = [(a[0], 1.0) for a in self.tx]
        else:
            self.usd = self.S.prepare(self.db.get_series('usd'))
        self.supply = self.S.prepare(self.db.get_series('supply'))
        self.mcap = [(a[0], a[1] * self.usd[i][1]) for i, a in enumerate(self.supply)]
        
        self.tx_sqr_m = [(a[0], (self.mcap[i][1] / self.mcap[0][1]) * a[1]**2) for i, a in enumerate(self.tx)]

    
def get_power(tx, mcap0, mcap, ref_mcap):
    delta = 0.01
    p = 1 - delta
    best = (2**256, 0)
    while p < 2.4:
        p += delta
        s = [(a[0], (mcap[i][1] / mcap0) * a[1]**p) for i, a in enumerate(tx)]
        stdev = util.stdev(s, ref_mcap)
        if stdev < best[0]:
            best = (stdev, p)
    return best[1]

def get_pivot(s):
    return int(len(s) / 2)

    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    M_usd = Money('_usd_m2_', 'USD')
    M_eur = Money('_eur_m2_', 'EUR')
    M_cny = Money('_cny_m2_', 'CNY')
    M_jpy = Money('_jpy_m2_', 'JPY')
    M_chf = Money('_chf_m2_', 'CHF')
    M_gbp = Money('_gbp_m2_', 'GBP')
    M_tether = Money('tether', 'USD')
    M_btc = Money('bitcoin', 'BTC')

    tx_sqr = [(a[0], a[1]**2) for a in M_usd.tx]

    mcap = [
        (M_usd.mcap[i][0], M_usd.mcap[i][1] + M_eur.mcap[i][1] + M_cny.mcap[i][1] + M_jpy.mcap[i][1] + M_chf.mcap[i][1] + M_gbp.mcap[i][1] + M_tether.mcap[i][1])
        for i in range(len(M_usd.mcap))
    ]
    tx_sqr_m = [(a[0], a[1] * (mcap[i][1] / mcap[0][1])) for i, a in enumerate(tx_sqr)]
    

    p = get_power(M_usd.tx[-28*1:], mcap[0][1], mcap[-28*1:], M_btc.mcap[-28*1:])
    tx_p = [(a[0], a[1]**p) for a in M_usd.tx]
    tx_p_m = [(a[0], a[1] * (mcap[i][1] / mcap[0][1])) for i, a in enumerate(tx_p)]

    draw.draw_custom({
        'TX^{:.2f} M'.format(p): tx_p_m,
        '[:]TX^2 M': tx_sqr_m,
        'Tether mcap (*10)': [(a[0], a[1]*10) for a in M_tether.mcap],
        'Money mcap (/100)': [(a[0], a[1]/100) for a in mcap],
        'BTC mcap': M_btc.mcap,        
    })
