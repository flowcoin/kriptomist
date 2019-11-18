import logging
log = logging.getLogger("util")

import time

def sleep(secs):
    log.debug("sleep: {} seconds".format(secs))
    time.sleep(secs)
