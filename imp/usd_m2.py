"""
Import USD M2 supply data from the FED. 
"""

import logging
log = logging.getLogger('usd_m2')

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
    
    db.Db('_usd_m2_').write_data({'day': datetime.now().strftime("%Y-%m-%d"), 'supply': supply_m2})

def historical():
    data = [
        ("2001-01-15", 4964900000000.0),
        ("2009-01-12", 8243900000000.0),
        ("2018-10-01", 14235400000000.0),
        ("2018-11-01", 14245400000000.0),
        ("2018-12-01", 14351700000000.0),
        ("2019-01-01", 14434600000000.0),
        ("2019-02-01", 14464300000000.0),
        ("2019-03-01", 14511800000000.0),
        ("2019-04-01", 14558700000000.0),
        ("2019-05-01", 14654300000000.0),
        ("2019-06-01", 14782600000000.0),
        ("2019-07-01", 14862100000000.0),
        ("2019-08-01", 14933300000000.0),
        ("2019-09-01", 15022900000000.0),
        ("2019-10-01", 15149900000000.0),
        ("2019-11-01", 15251200000000.0),
        ("2019-12-01", 15307100000000.0),
        ("2020-01-01", 15402100000000.0),
        ("2020-02-01", 15446900000000.0),
        ("2020-03-01", 15989800000000.0),
        ("2020-04-01", 17019800000000.0),
        ("2020-05-01", 17868100000000.0),
        ("2020-06-01", 18163400000000.0),
        ("2020-07-01", 18321600000000.0),
        ("2020-08-01", 18403600000000.0),
        ("2020-09-01", 18648100000000.0),
    ]
    for day, supply_m2 in data:
        db.Db('_usd_m2_').write_data({'day': day, 'supply': supply_m2})    

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
    
    if sys.argv[1:] and sys.argv[1] == 'import':
        historical()
    else:
        
        from sources.blockchain_com import BlockchainCom
        
        if sys.argv[1:]:
            date_start = datetime.strptime(sys.argv[1].split(":")[0], "%Y-%m-%d")
            date_stop = datetime.strptime(sys.argv[1].split(":")[1], "%Y-%m-%d")
        else:
            date_start = datetime(2009, 1, 3)
            date_stop = util.today()
            
        
        S = util.Series(date_start=date_start, date_stop=date_stop)

        usd_supply = S.prepare(db.Db('_usd_m2_').get_series('supply'))
        usd_supply0 = usd_supply[0][1]

        btc = S.prepare(db.Db('bitcoin').get_series('usd'))
        btc_supply = S.prepare(db.Db('bitcoin').get_series('supply'))
        btc_mcap = [(btc[i][0], btc[i][1] * btc_supply[i][1]) for i in range(len(btc))]

        tether_supply = S.prepare(db.Db('tether').get_series('supply'))
        
        tx = S.prepare(BlockchainCom.fetch_data("n-transactions"))
        tx_sqr = [(a[0], a[1]**2) for a in tx]

        tx_m2 = S.prepare([(tx_sqr[i][0], tx_sqr[i][1] * (usd_supply[i][1] / usd_supply0)) for i in range(len(tx_sqr))])
        
        p = get_power(tx, usd_supply, btc_mcap, usd_supply0)
        tx_adj = [(a[0], a[1]**p) for a in tx]
        tx_m2_adj = [(tx_adj[i][0], tx_adj[i][1] * (usd_supply[i][1] / usd_supply0)) for i in range(len(tx_adj))]

        piv = get_pivot(tx, usd_supply, btc_mcap)
        tx_m2_piv_adj = [(a[0], (usd_supply[i][1] / usd_supply[piv][1]) * a[1]**2) for i, a in enumerate(tx)]
        
        draw.draw_custom({
            'TX^{:.2f} M2 adjusted'.format(p): tx_m2_adj,
            'TX^2 M2 pivot({}) adjusted'.format(piv): tx_m2_piv_adj,
            '[:]TX^2 M2': tx_m2,
            '[:]TX^2': tx_sqr,
            'Tether Supply (*10)': [(a[0], a[1]*10) for a in tether_supply],
            'USD M2 Supply (/100)': [(a[0], a[1]/100) for a in usd_supply],
            'BTC market cap': btc_mcap,
        })
