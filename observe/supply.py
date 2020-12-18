""" Notify on coin supply change
"""


import logging
log = logging.getLogger('supply')

import sys
import re
import random
from collections import OrderedDict
from datetime import datetime
import time

import requests

from sources.coinmarketcap import Coinmarketcap

SUPPLY = [1]

def fetch_supply(name):
    for coin in Coinmarketcap.list_coins():
        if coin['slug'] == name:
            SUPPLY.append(coin['circulating_supply'])
            delta = SUPPLY[-1] - SUPPLY[-2]
            delta_rel = delta / SUPPLY[-2]
            if delta != 0:
                print('{}: {} {:.2f} ({:.4f}%)'.format(coin['slug'], coin['circulating_supply'], delta, 100 * delta_rel))
                if delta > 0:
                    print("\a", end='')
                else:
                    print("\a", end='')
                    time.sleep(1)
                    print("\a", end='')
            return

if __name__ == '__main__':
    while True:
        fetch_supply(sys.argv[1])
        time.sleep(60)
        