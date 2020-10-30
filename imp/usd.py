"""
Import USD M1 supply data from the FED. 
"""

import logging
log = logging.getLogger('usd')

import sys
from datetime import datetime
import csv

import requests

import db
import draw
import util
import config

FED_USD_URL = "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H6&series=6bf40962b4915bc16c2ef1276faee57a&lastobs=24&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package"
CSV_FILE = "tmp/usd.csv"


def today():
    open(CSV_FILE, "w").write(requests.get(FED_USD_URL).text)
    log.info('Downloaded USD data to {}'.format(CSV_FILE))

    multiplier = 1.0
    date = None
    supply = None
    supply_m2 = None
    supply_base = None
    with open(CSV_FILE) as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row:
                continue
    
            if i == 4:
                multiplier = float(row[1])
                
            if i > 10:
                date = datetime.strptime(row[0], "%Y-%m")
                supply = float(row[1]) * multiplier
                supply_m2 = float(row[2]) * multiplier
                supply_base = float(row[3]) * multiplier
                log.info("{} M1:{} M2:{} Base:{}".format(date, supply, supply_m2, supply_base))
    
    db.Db('_usd_').write_data({'day': datetime.now().strftime("%Y-%m-%d"), 'supply': supply})

def historical():
    data = [
        ("2001-01-20", 1096300000000.0),
        ("2009-01-20", 1585600000000.0),
        ("2017-01-20", 3396200000000.0),
        ("2018-10-01", 3719100000000.0),
        ("2018-11-01", 3698100000000.0),
        ("2018-12-01", 3746400000000.0),
        ("2019-01-01", 3740400000000.0),
        ("2019-02-01", 3759600000000.0),
        ("2019-03-01", 3729800000000.0),
        ("2019-04-01", 3780900000000.0),
        ("2019-05-01", 3792400000000.0),
        ("2019-06-01", 3832800000000.0),
        ("2019-07-01", 3858100000000.0),
        ("2019-08-01", 3853200000000.0),
        ("2019-09-01", 3903000000000.0),
        ("2019-10-01", 3922800000000.0),
        ("2019-11-01", 3947400000000.0),
        ("2019-12-01", 3976900000000.0),
        ("2020-01-01", 3975100000000.0),
        ("2020-02-01", 4003100000000.0),
        ("2020-03-01", 4256700000000.0),
        ("2020-04-01", 4798900000000.0),
        ("2020-05-01", 5035000000000.0),
        ("2020-06-01", 5214600000000.0),
        ("2020-07-01", 5331300000000.0),
        ("2020-08-01", 5390800000000.0),
        ("2020-09-01", 5502200000000.0),
    ]
    for day, supply in data:
        db.Db('_usd_').write_data({'day': day, 'supply': supply})    

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
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    if sys.argv[1:] and sys.argv[1] == 'import':
        historical()
    else:
        
        from sources.blockchain_com import BlockchainCom
        
        if sys.argv[1:]:
            date_start = datetime.strptime(sys.argv[1].split(":")[0], "%Y-%m-%d")
            date_stop = datetime.strptime(sys.argv[1].split(":")[1], "%Y-%m-%d")
        else:
            date_start = config.DATE_START
            date_stop = util.today()
            
        usd_supply0 = db.Db('_usd_').get_series('supply')[0][1]
        
        S = util.Series(date_start=date_start, date_stop=date_stop)

        usd_supply = S.prepare(db.Db('_usd_').get_series('supply'))

        btc = S.prepare(db.Db('bitcoin').get_series('usd'))
        btc_supply = S.prepare(db.Db('bitcoin').get_series('supply'))
        btc_mcap = [(btc[i][0], btc[i][1] * btc_supply[i][1]) for i in range(len(btc))]

        tether_supply = S.prepare(db.Db('tether').get_series('supply'))
        
        tx = S.prepare(util.moving_average(BlockchainCom.fetch_data("n-transactions"), days=7))
        tx_sqr = [(a[0], a[1]**2) for a in tx]

        tx_m1 = S.prepare(util.moving_average([(tx_sqr[i][0], tx_sqr[i][1] * (usd_supply[i][1] / usd_supply0)) for i in range(len(tx_sqr))], days=7))
        
        p = get_power(tx, usd_supply, btc_mcap, usd_supply0)
        tx_adj = [(a[0], a[1]**p) for a in tx]
        tx_m1_adj = [(tx_adj[i][0], tx_adj[i][1] * (usd_supply[i][1] / usd_supply0)) for i in range(len(tx_adj))]
        
        draw.draw_custom({
            'TX^{:.2f} M1 adjusted'.format(p): tx_m1_adj,
            'BTC market cap': btc_mcap,
            '[:]TX^2 M1': tx_m1,
            '[:]TX^2': tx_sqr,
            'Tether Supply (*10)': [(a[0], a[1]*10) for a in tether_supply],
            'USD M1 Supply (/10)': [(a[0], a[1]/10) for a in usd_supply],
        })
