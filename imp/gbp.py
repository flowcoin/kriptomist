"""
Import GBP M2 supply and GBP/USD price data. 
"""

import logging
log = logging.getLogger('gbp')

import sys
from datetime import datetime
import csv

import requests

import db
import draw
import util
import config


def today():
    log.warning("Please manually enter the GBP data into db.")
    
def historical():
    data = [
        ("2000-01-01",  750000000000.0, 1.60),
        ("2010-01-01", 2000000000000.0, 1.63),
        ("2011-01-01", 2080000000000.0, 1.55),
        ("2012-01-01", 2034000000000.0, 1.55),
        ("2013-01-01", 2042000000000.0, 1.61),
        ("2014-01-01", 2078000000000.0, 1.65),
        ("2015-01-01", 2080000000000.0, 1.51),
        ("2016-01-01", 2132000000000.0, 1.47),
        ("2017-01-01", 2279000000000.0, 1.22),
        ("2018-01-01", 2345000000000.0, 1.42),
        ("2019-01-01", 2413000000000.0, 1.29),
        ("2020-01-01", 2446000000000.0, 1.30),
        ("2020-09-01", 2727000000000.0, 1.28),
    ]
    for day, supply, usd in data:
        res = db.Db('_gbp_m2_').write_data({'day': day, 'supply': supply, 'usd': usd})    
        log.info('M2 [{}] {} {} {}'.format(res, day, supply, usd))
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    if sys.argv[1:] and sys.argv[1] == 'today':
        today()
    else:
        historical()
