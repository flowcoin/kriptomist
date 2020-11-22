"""
Import CNY M2 supply and CNY/USD price data. 
"""

import logging
log = logging.getLogger('cny')

import sys
from datetime import datetime
import csv

import requests

import db
import draw
import util
import config


def today():
    log.warning("Please manually enter the CNY data into db.")
    
def historical():
    data = [
        ("2000-01-01",  12122040000000.0, 0.10),
        ("2009-01-01",  50000000000000.0, 0.15),
        ("2017-01-01", 157600000000000.0, 0.15),
        ("2019-12-01", 198650000000000.0, 0.14),
        ("2020-10-01", 214970000000000.0, 0.15),
    ]
    for day, supply, usd in data:
        res = db.Db('_cny_m2_').write_data({'day': day, 'supply': supply, 'usd': usd})    
        log.info('M2 [{}] {} {} {}'.format(res, day, supply, usd))
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    if sys.argv[1:] and sys.argv[1] == 'today':
        today()
    else:
        historical()
