"""
Display USD M1 supply data. 
"""

import logging
log = logging.getLogger('usd_m1')

import sys
from datetime import datetime

import requests

import db
import draw
import util
import config


def get_power(tx, usd_supply, btc_cap, usd_supply0):
    delta = 0.01
    p = 1 - delta
    best = (2**256, 0)
    while p < 2:
        p += delta
        s = [(a[0], (usd_supply[i][1] / usd_supply0) * a[1]**p) for i, a in enumerate(tx)]
        stdev = util.stdev(s, btc_mcap)
        if stdev < best[0]:
            best = (stdev, p)
    return best[1]

def get_pivot(tx, usd_supply, btc_cap):
    return int(len(tx) / 2)
    p = -1
    best = (2**256, 0)
    while p < len(usd_supply) - 1:
        p += 1
        s = [(a[0], (usd_supply[i][1] / usd_supply[p][1]) * a[1]**2) for i, a in enumerate(tx)]
        stdev = util.stdev(s, btc_mcap)
        if stdev < best[0]:
            best = (stdev, p)
    return best[1]
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    from sources.blockchain_com import BlockchainCom
    
    if sys.argv[1:]:
        date_start = datetime.strptime(sys.argv[1].split(":")[0], "%Y-%m-%d")
        date_stop = datetime.strptime(sys.argv[1].split(":")[1], "%Y-%m-%d")
    else:
        date_start = datetime(2009, 1, 3)
        date_stop = util.today()
        
    
    S = util.Series(date_start=date_start, date_stop=date_stop)

    usd_supply = S.prepare(db.Db('_usd_').get_series('supply'))
    usd_supply0 = usd_supply[0][1]

    btc = S.prepare(db.Db('bitcoin').get_series('usd'))
    btc_supply = S.prepare(db.Db('bitcoin').get_series('supply'))
    btc_mcap = [(btc[i][0], btc[i][1] * btc_supply[i][1]) for i in range(len(btc))]

    tether_supply = S.prepare(db.Db('tether').get_series('supply'))
    
    tx = S.prepare(BlockchainCom.fetch_data("n-transactions"))
    tx_sqr = [(a[0], a[1]**2) for a in tx]

    tx_m1 = S.prepare([(tx_sqr[i][0], tx_sqr[i][1] * (usd_supply[i][1] / usd_supply0)) for i in range(len(tx_sqr))])
    
    p = get_power(tx, usd_supply, btc_mcap, usd_supply0)
    tx_adj = [(a[0], a[1]**p) for a in tx]
    tx_m1_adj = [(tx_adj[i][0], tx_adj[i][1] * (usd_supply[i][1] / usd_supply0)) for i in range(len(tx_adj))]

    piv = get_pivot(tx, usd_supply, btc_mcap)
    tx_m1_piv_adj = [(a[0], (usd_supply[i][1] / usd_supply[piv][1]) * a[1]**2) for i, a in enumerate(tx)]
    
    draw.draw_custom({
        'TX^{:.2f} M1 adjusted'.format(p): tx_m1_adj,
        'TX^2 M1 pivot({}) adjusted'.format(piv): tx_m1_piv_adj,
        '[:]TX^2 M1': tx_m1,
        '[:]TX^2': tx_sqr,
        'Tether Supply (*10)': [(a[0], a[1]*10) for a in tether_supply],
        'USD M1 Supply (/10)': [(a[0], a[1]/10) for a in usd_supply],
        'BTC market cap': btc_mcap,
    })
