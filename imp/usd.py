"""
Import USD M1 & M2 supply data from the FED. 
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
                #log.info("{} M1:{} M2:{} Base:{}".format(date, supply, supply_m2, supply_base))
    
    if date > db.Db('_usd_').get_series('supply')[-1][0]:
        res = db.Db('_usd_').write_data({'day': date, 'supply': supply})
        log.info('M1 [{}] {} {}'.format(res, date, supply))
        res = db.Db('_usd_m2_').write_data({'day': date, 'supply': supply_m2})
        log.info('M2 [{}] {} {}'.format(res, date, supply_m2))
    else:
        log.info("No new USD supply data at this time.")
    
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
        res = db.Db('_usd_').write_data({'day': day, 'supply': supply})    
        log.info('M1 [{}] {} {}'.format(res, day, supply))

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
    for day, supply in data:
        res = db.Db('_usd_m2_').write_data({'day': day, 'supply': supply})    
        log.info('M2 [{}] {} {}'.format(res, day, supply))
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    if sys.argv[1:] and sys.argv[1] == 'today':
        today()
    else:
        historical()
