"""
Import JPY M2 supply and JPY/USD price data. 
"""

import logging
log = logging.getLogger('jpy')

import sys
from datetime import datetime
import csv

import requests

import db
import draw
import util
import config


def today():
    log.warning("Please manually enter the JPY data into db.")
    
def historical():
    data = [
        ("2000-01-01",  600000000000000.0, 0.0095),
        ("2009-01-01",  748827000000000.0, 0.0110),
        ("2010-11-01",  779000000000000.0, 0.0120),
        ("2017-01-01",  962000000000000.0, 0.0087),
        ("2019-12-01", 1040000000000000.0, 0.0092),
        ("2020-10-01", 1120000000000000.0, 0.0095),
    ]
    for day, supply, usd in data:
        res = db.Db('_jpy_m2_').write_data({'day': day, 'supply': supply, 'usd': usd})    
        log.info('M2 [{}] {} {} {}'.format(res, day, supply, usd))
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    if sys.argv[1:] and sys.argv[1] == 'today':
        today()
    else:
        historical()
