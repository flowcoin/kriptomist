"""
Import EUR M2 & M3 supply and EUR/USD price data. 
"""

import logging
log = logging.getLogger('eur')

import sys
from datetime import datetime
import csv

import requests

import db
import draw
import util
import config


def today():
    log.warning("Please manually enter the EUR data into db.")
    
def historical():
    data = [
        ("2000-01-01",  4000000000000.0, 1.00),
        ("2009-01-01",  8000000000000.0, 1.30),
        ("2017-01-01", 10750000000000.0, 1.06),
        ("2019-12-01", 12380000000000.0, 1.10),
        ("2020-09-01", 13460000000000.0, 1.18),
    ]
    for day, supply, usd in data:
        res = db.Db('_eur_m2_').write_data({'day': day, 'supply': supply, 'usd': usd})    
        log.info('M2 [{}] {} {} {}'.format(res, day, supply, usd))
    
    data = [
        ("2000-01-01",  4723291000000.0, 1.00),
        ("2009-01-01",  9400007000000.0, 1.30),
        ("2017-01-01", 11431525000000.0, 1.06),
        ("2019-12-01", 13000000000000.0, 1.10),
    ]
    for day, supply, usd in data:
        res = db.Db('_eur_m3_').write_data({'day': day, 'supply': supply, 'usd': usd})    
        log.info('M3 [{}] {} {} {}'.format(res, day, supply, usd))
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    if sys.argv[1:] and sys.argv[1] == 'today':
        today()
    else:
        historical()
