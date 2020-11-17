""" BCHABC vs BCHN blocks notification
"""


import logging
log = logging.getLogger('bch_blocks')

import re
import random
from collections import OrderedDict
from datetime import datetime
import time

import requests


BCH_BLOCKS_URL = "https://api.blockchair.com/bitcoin-cash/blocks?limit=100&offset={}"
ABC_BLOCKS_URL = "https://api.blockchair.com/bitcoin-abc/blocks?limit=100&offset={}"

LAST_HASH = {}

def sum_tx(blocks, start=datetime(*datetime.now().timetuple()[:3])):
    count = 0
    for block in blocks:
        t = datetime.strptime(block['time'], "%Y-%m-%d %H:%M:%S")
        if t > start:
            count += block['transaction_count']
    return count
    
def fetch_blocks(url, beep=1):
    blocks = []
    for offset in [100 * x for x in range(2)]:
        blocks.extend(requests.get(url.format(offset)).json()["data"])
    tx_count = sum_tx(blocks)
    if url not in LAST_HASH or blocks[0]['hash'] != LAST_HASH[url]:
        LAST_HASH[url] = blocks[0]['hash']
        for i in range(beep):
            print("\a", end='')
            time.sleep(1)
        print(tx_count, url.split('/')[3])    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('matplotlib').setLevel(logging.INFO)

    while True:
        for i, url in enumerate([BCH_BLOCKS_URL, ABC_BLOCKS_URL]):
            fetch_blocks(url, beep=i+1)
        time.sleep(10)
        