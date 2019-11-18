import logging
log = logging.getLogger("util")

import time
from datetime import datetime, timedelta

def sleep(secs):
    log.debug("sleep: {} seconds".format(secs))
    time.sleep(secs)
    
def div0(x, y, z=lambda x: x * 100):
    if y == 0:
        ret = z(x)
        log.debug("div0: {x} / {y} = {ret}".format(x, y, ret))
        return ret
    return x / y
    
def series_fill_zeroes(s):
    while len(s) < 30:
        s.insert(0, (s[0][0] - timedelta(days=1), 0))
