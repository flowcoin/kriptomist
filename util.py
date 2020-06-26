import logging
log = logging.getLogger("util")

import time
from datetime import datetime, timedelta

from jinja2 import Template

from config import DATE_START

def sleep(secs):
    log.debug("sleep: {} seconds".format(secs))
    time.sleep(secs)
    
def div0(x, y, z=lambda x: x * 10):
    if not x:
        x = 0
    if not y:
        y = 0
    if y == 0:
        ret = z(x)
        log.debug("div0: {} / {} = {}".format(x, y, ret))
        return ret
    return x / y

def round100(x):
    return int(100 * x) / 100

def round10k(x):
    return int(10000 * x) / 10000

def round100M(x):
    return int((10**8) * x) / (10**8)
    
def series_fill_zeroes(s):
    if not s:
        s.append( (datetime.date(datetime.now()), 0) )
    while len(s) < 30:
        s.insert(0, (s[0][0] - timedelta(days=1), 0))
        
    for i, a in enumerate(s):
        if a[1] is None:
            s[i] = (s[i][0], 0)
        
def normalize(obj, name):
    minv = maxv = None
    for a in getattr(obj, name):
        if minv is None or a[1] < minv:
            minv = a[1]
        if maxv is None or a[1] > maxv:
            maxv = a[1]
    try:
        setattr(obj, name+'_norm', [(a[0], 100*(a[1]-minv)/(maxv-minv)) for a in getattr(obj, name)])
    except(ZeroDivisionError):
        setattr(obj, name+'_norm', [(a[0], 50) for a in getattr(obj, name)])

def dump_html_old(kms):
    t = Template(open("html/template/table_old.html").read())
    s = t.render(kms=kms, round100=round100, round10k=round10k, round100M=round100M)
    open(datetime.now().strftime("html/table_old_%Y_%m_%d.html"), "w").write(s)

def dump_html(kms, prefix=''):
    t = Template(open("html/template/table.html").read())
    s = t.render(kms=kms, round100=round100, round10k=round10k, round100M=round100M)
    fullname = datetime.now().strftime("html/" + prefix + "table_%Y_%m_%d.html")
    open(fullname, "w").write(s)
    log.info("Wrote {} coins to {}".format(len(kms), fullname))

def series_to_dict(s):
    D = {}
    for day, val in s:
        D[day] = val
    return D

def km_to_dictlist(km):
    ret = []
    
    btc = series_to_dict(km.cmc.btc_series)
    usd = series_to_dict(km.cmc.usd_series)
    supply = series_to_dict(km.cmc.supply)
    subs = series_to_dict(km.srs.series)
    
    day = DATE_START - timedelta(days=1)
    while True:
        day += timedelta(days=1)
        if day > datetime.now() - timedelta(days=1):
            break
        ret.append({
            "day": day.strftime("%Y-%m-%d"),
            "btc": btc.get(day, None),
            "usd": usd.get(day, None),
            "supply": supply.get(day, None),
            "subs": subs.get(day, None)
        })   
    return ret
    
def moving_average(s, days=28):
    ret = []
    for i in range(len(s)):
        if i < days:
            continue
        past = [a[1] for a in s[i-days:i+1]]
        m = sum(past) / len(past)
        ret.append((s[i][0], m))
    return ret

def price_diff(s):
    ret = []
    for i in range(len(s)):
        if i < 1:
            continue
        past = s[i-1][1]
        d = 100 * div0(s[i][1] - past, past, z=lambda x: 0 if x == 0 else 1)
        ret.append((s[i][0], d))
    return ret
    
def series_shift(s, days):
    d = series_to_dict(s)
    ret = []
    day = s[0][0] - timedelta(days=1)
    while True:
        if day > datetime.now():
            break
        try:
            day += timedelta(days=1)
            ret.append((day, d[day+timedelta(days=days)]))
        except:
            pass
    return ret


