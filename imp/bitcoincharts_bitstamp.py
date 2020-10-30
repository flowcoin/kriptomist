""" Import Bitstamp BTC/USD data from Bitcoincharts.com

First you need to:
 - Download http://api.bitcoincharts.com/v1/csv/bitstampUSD.csv.gz
 - unpack to /tmp/bitstampUSD.csv
"""

import logging
log = logging.getLogger('bitcoincharts_bitstamp')
logging.basicConfig(level=logging.INFO)

import csv
from datetime import datetime

import db

CSV_FILE = "tmp/bitstampUSD.csv"

btc_db = db.Db('bitcoin')

with open(CSV_FILE) as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if not row:
            continue
        
        day = datetime.fromtimestamp(int(row[0]))
        price = float(row[1])
       
        if btc_db.write_data({'day': day, 'usd': price}):
            log.info("{} {}".format(day, price))
            
