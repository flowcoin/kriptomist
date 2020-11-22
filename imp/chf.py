"""
Import CHF M2 supply and CHF/USD price data. 
"""

import logging
log = logging.getLogger('chf')

import sys
from datetime import datetime
import csv

import requests

import db
import draw
import util
import config


def today():
    log.warning("Please manually enter the CHF data into db.")
    
def historical():
    data = [
        ("2000-01-01",  400000000000.0, 0.70),
        ("2009-01-01",  500000000000.0, 0.90),
        ("2011-01-01",  700000000000.0, 1.04),
        ("2012-01-01",  771000000000.0, 1.06),
        ("2013-01-01",  847000000000.0, 1.09),
        ("2014-01-01",  881000000000.0, 1.12),
        ("2015-01-01",  897000000000.0, 0.99),
        ("2016-01-01",  911000000000.0, 1.00),
        ("2017-01-01",  944000000000.0, 0.98),
        ("2018-01-01",  986000000000.0, 1.03),
        ("2019-01-01", 1020000000000.0, 1.02),
        ("2020-01-01", 1010000000000.0, 1.03),
        ("2020-09-01", 1060000000000.0, 1.10),
    ]
    for day, supply, usd in data:
        res = db.Db('_chf_m2_').write_data({'day': day, 'supply': supply, 'usd': usd})    
        log.info('M2 [{}] {} {} {}'.format(res, day, supply, usd))
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    if sys.argv[1:] and sys.argv[1] == 'today':
        today()
    else:
        historical()
