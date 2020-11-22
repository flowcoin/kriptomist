""" Display USD M2 supply data. 
"""

import logging
log = logging.getLogger('usd_m2')

import sys
from datetime import datetime

import requests

import db
import draw
import util
import config
from money import Money, get_power, get_pivot
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    M_usd = Money('_usd_m2_', 'USD')
    M_tether = Money('tether', 'USD')
    M_btc = Money('bitcoin', 'BTC')

    tx_sqr = [(a[0], a[1]**2) for a in M_usd.tx]

    mcap = M_usd.mcap
    tx_sqr_m = [(a[0], a[1] * (mcap[i][1] / mcap[0][1])) for i, a in enumerate(tx_sqr)]
    
    p = get_power(M_usd.tx[-400:], mcap[0][1], mcap[-400:], M_btc.mcap[-400:])
    tx_p = [(a[0], a[1]**p) for a in M_usd.tx]
    tx_p_m = [(a[0], a[1] * (mcap[i][1] / mcap[0][1])) for i, a in enumerate(tx_p)]

    draw.draw_custom({
        'TX^{:.2f} M'.format(p): tx_p_m,
        '[:]TX^2 M': tx_sqr_m,
        'Tether mcap (*10)': [(a[0], a[1]*10) for a in M_tether.mcap],
        'USD M2 mcap (/100)': [(a[0], a[1]/100) for a in mcap],
        'BTC mcap': M_btc.mcap,        
    })
