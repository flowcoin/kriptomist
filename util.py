import logging
log = logging.getLogger("util")

import time
from datetime import datetime, timedelta
import copy

from jinja2 import Template

from config import DATE_START


def today():
    return datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")

class Series:
    def __init__(self, date_start=DATE_START, date_stop=today()):
        self.date_start = date_start
        self.date_stop = date_stop

    def prepare(self, s):
        return series_prepare(s, date_start=self.date_start, date_stop=self.date_stop)


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
        #log.debug("div0: {} / {} = {}".format(x, y, ret))
        return ret
    return x / y

def avg(lst):
    if not lst:
        return 0
    return div0(sum(lst), len(lst), 0)

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
        
def series_normalize(s):
    minv = maxv = None
    for a in s:
        if minv is None or a[1] < minv:
            minv = a[1]
        if maxv is None or a[1] > maxv:
            maxv = a[1]
    return [(a[0], 100 * div0(a[1]-minv, maxv-minv, lambda x: 0.5)) for a in s]
    
def normalize(obj, name):
    setattr(obj, name+'_norm', series_normalize(getattr(obj, name)))

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

def series_abs_diff(s):
    ret = []
    for i in range(len(s)):
        if i < 1:
            continue
        past = s[i-1][1]
        d = s[i][1] - past
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

def get_cumulative_series(kms, name):
    ret = []
    D = {}
    for km in kms:
        D[km.coin.name] = series_to_dict(getattr(km.coin, name))
    day = DATE_START - timedelta(days=1)
    while day < datetime.now():
        day += timedelta(days=1)
        y = 0
        for s in D.values():
            y += s.get(day, 0)
        ret.append((day, y))
    return ret

def series_min_max(s, count=28):
    _min = min(a[1] for a in s[-count:])
    _max = max(a[1] for a in s[-count:])
    last = s[-1][1]
    return {
        'last': last,
        'min': (_min, round10k((_min-last) / last)),
        'max': (_max, round10k((_max-last) / last)),
    }

def stdev(s1, s2):    
    return sum([(s2[i][1] - s1[i][1])**2 for i in range(len(s1)) if s1[i][1] and s2[i][1]])**0.5

def rel_change(start, end):
    return div0(end - start, start, 0)

def series_avg(s):
    if not s:
        return 0
    return div0(sum(a[1] for a in s), len(s), 0)

def series_interpolate(s):
    if not s:
        return []
    if len(s) == 1:
        return s

    if len(s) == 2:
        ret = []
        delta = (s[1][1] - s[0][1]) / (s[1][0] - s[0][0]).days
        day = s[0][0] - timedelta(days=1)
        yy = s[0][1] - delta
        while day < s[1][0]:
            day += timedelta(days=1)
            yy += delta
            ret.append((day, yy))
        return ret
    ret = []
    for i in range(1, len(s)):
        a = s[i-1]
        b = s[i]
        ret.extend(series_interpolate([a, b])[:-1])
    ret.append(b)
    return ret
    
def series_prepare(s, date_start=DATE_START, date_stop=today()):
    ret = copy.copy(s)
    if not ret or len(ret) < 2:
        return ret

    ret = [a for a in ret if a[1] is not None]

    if date_start < ret[0][0]:
        ret.insert(0, (date_start, 0))
    if date_stop > ret[-1][0]:
        ret.append((date_stop, ret[-1][1]))

    ret = series_interpolate(ret)
    ret = [a for a in ret if a[0] >= date_start and a[0] <= date_stop]
    return ret


if __name__ == '__main__':
    import draw
    s = [(datetime(2020, 10, 10), 10), (datetime(2020, 10, 19), 100), (datetime(2020, 10, 20), 50)]
    si = series_interpolate(s)
    sp = series_prepare(s, date_start=datetime(2020, 10, 1), date_stop=datetime(2020, 10, 30))
    print(s)
    print(si)
    print(sp)
    draw.draw_custom_dots({
        's': s,
        'si': [(a[0], a[1] + 10) for a in si],
        'sp': [(a[0], a[1] + 20) for a in sp],
    })
    