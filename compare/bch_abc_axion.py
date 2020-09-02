import logging
log = logging.getLogger('bch_abc_axion')

import re
from collections import OrderedDict

import requests


BLOCKS_URL = "https://api.blockchair.com/bitcoin-cash/blocks?limit=100"

MINERS = OrderedDict([
    ('antpool', {
        'match': lambda block: 'antpool' in decode_hex_str(block['coinbase_data_hex']),
        'blocks': [],
        'software': 'unknown',
    }),
    ('viabtc', {
        'match': lambda block: 'viabtc' in decode_hex_str(block['coinbase_data_hex']),
        'blocks': [],
        'software': 'abc',
    }),
    ('binance', {
        'match': lambda block: 'pool.binance.com' in decode_hex_str(block['coinbase_data_hex']),
        'blocks': [],
        'software': 'bchn',
    }),
    ('btc.com', {
        'match': lambda block: 'btc.com' in decode_hex_str(block['coinbase_data_hex']),
        'blocks': [],
        'software': 'unknown',
    }),    
    ('bitcoin.com', {
        'match': lambda block: 'bitcoin.com' in decode_hex_str(block['coinbase_data_hex']),
        'blocks': [],
        'software': 'bchn',
    }),
    ('huobi', {
        'match': lambda block: 'huobi' in decode_hex_str(block['coinbase_data_hex']),
        'blocks': [],
        'software': 'bchn',
    }),
    ('btc.top', {
        'match': lambda block: 'btc.top' in decode_hex_str(block['coinbase_data_hex']),
        'blocks': [],
        'software': 'bchn',
    }),
    ('unknown', {
        'match': lambda block: log.debug('Unknown miner: ' + decode_hex_str(block['coinbase_data_hex'])) or True,
        'blocks': [],
        'software': 'unknown',
    }),
])

SOFTWARE = OrderedDict([
    ('bchn', {
        'match': lambda block: 'bchn' in decode_hex_str(block['coinbase_data_hex']),
        'blocks': [],
    }),
    ('unknown', {
        'match': lambda block: log.debug('Unknown software: ' + decode_hex_str(block['coinbase_data_hex'])) or True,
        'blocks': [],
    }),
])

EXCHANGES = OrderedDict([
    ('Coinbase', {
        'software': 'unknown',
        'volume': 15,
    }),
    ('Binance', {
        'software': 'bchn',
        'volume': 210,
    }),
    ('Bitstamp', {
        'software': 'unknown',
        'volume': 10,
    }),
    ('WBF Exchange', {
        'software': 'unknown',
        'volume': 120,
    }),
    ('EXX', {
        'software': 'abc',
        'volume': 110,
    }),
    ('Huobi', {
        'software': 'unknown',
        'volume': 110,
    }),
    ('OKEx', {
        'software': 'unknown',
        'volume': 100,
    }),
    ('HitBTC', {
        'software': 'unknown',
        'volume': 80,
    }),
    ('Bitcoin.com', {
        'software': 'bchn',
        'volume': 80,
    }),
    ('Livecoin', {
        'software': 'abc',
        'volume': 1,
    }),
    ('others', {
        'software': 'unknown',
        'volume': 1000,
    }),
])

def decode_hex_str(s):
    ret = bytes.fromhex(s).decode('utf-8', errors='replace').lower()
    ret = re.sub(r'[^a-z0-9\.\/-]', ' ', ret)
    return ret


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('matplotlib').setLevel(logging.INFO)

    blocks = requests.get(BLOCKS_URL).json()["data"]
    for block in blocks:
        for miner, md in MINERS.items():
            if md['match'](block):
                md['blocks'].append(block)
                break
        for software, sd in SOFTWARE.items():
            if sd['match'](block):
                sd['blocks'].append(block)
                break

    import matplotlib.pyplot as plt

    # -- Miners
    labels = []
    sizes = []
    explode = []
    for miner, md in MINERS.items():
        labels.append(miner + " (" + md['software'].upper() + ")")
        sizes.append(len(md['blocks']))
        #explode.append({'bchn': 0.2, 'abc': 0.0}.get(md['software'], 0.1))
        explode.append(0.1)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')

    # -- Software
    labels = []
    sizes = []
    explode = []
    for software, sd in SOFTWARE.items():
        labels.append(software)
        sizes.append(len(sd['blocks']))
        #explode.append({'bchn': 0.2, 'abc': 0.0}.get(software, 0.1))
        explode.append(0.1)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    
    # -- Exchanges
    labels = []
    sizes = []
    explode = []
    for exchange, ed in EXCHANGES.items():
        labels.append(exchange + " (" + ed['software'].upper() + ")")
        sizes.append(ed['volume'])
        #explode.append({'bchn': 0.2, 'abc': 0.0}.get(ed['software'], 0.1))
        explode.append(0.0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    
    
    plt.show()
    