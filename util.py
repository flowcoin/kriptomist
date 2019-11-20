import logging
log = logging.getLogger("util")

import time
from datetime import datetime, timedelta

from jinja2 import Template

def sleep(secs):
    log.debug("sleep: {} seconds".format(secs))
    time.sleep(secs)
    
def div0(x, y, z=lambda x: x * 100):
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

def dump_html(kms):
    t = Template(open("html/table.html").read())
    s = t.render(kms=kms, round100=round100, round10k=round10k, round100M=round100M)
    open(datetime.now().strftime("html/table_%Y_%m_%d.html"), "w").write(s)


