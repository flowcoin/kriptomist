""" [2020-11-15] Bitcoin Cash fork analysis

- BCHABC vs BCHN

"""


import logging
log = logging.getLogger('bch_abc_axion')

import re
import random
from collections import OrderedDict

import requests


BLOCKS_URL = "https://api.blockchair.com/bitcoin-cash/blocks?limit=100"

MINERS = OrderedDict([
    ('antpool', {
        'match': lambda block: 'antpool' in decode_hex_str(block['coinbase_data_hex']),
        'blocks': [],
        'software': 'bchn',
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
        'software': 'bchn',
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
        'volume': 0,
    }),
    ('Binance', {
        'software': 'both',
        'volume': 0,
    }),
    ('Bitstamp', {
        'software': 'unknown',
        'volume': 0,
    }),
    ('WBF', {
        'software': 'unknown',
        'volume': 0,
    }),
    ('EXX', {
        'software': 'abc',
        'volume': 0,
    }),
    ('Huobi', {
        'software': 'both',
        'volume': 0,
    }),
    ('OKEx', {
        'software': 'both',
        'volume': 0,
    }),
    ('HitBTC', {
        'software': 'unknown',
        'volume': 0,
    }),
    ('Bitcoin.com', {
        'software': 'bchn',
        'volume': 0,
    }),
    ('Livecoin', {
        'software': 'abc',
        'volume': 0,
    }),
    ('BitZ', {
        'software': 'abc',
        'volume': 0,
    }),
    ('DragonEX', {
        'software': 'abc',
        'volume': 0,
    }),
    ('YoBit', {
        'software': 'abc',
        'volume': 0,
    }),
    ('FEX', {
        'software': 'abc',
        'volume': 0,
    }),
    ('ZBG', {
        'software': 'abc',
        'volume': 0,
    }),
    ('KuCoin', {
        'software': 'abc',
        'volume': 0,
    }),
    ('BW.com', {
        'software': 'abc',
        'volume': 0,
    }),
    ('CoinTiger', {
        'software': 'abc',
        'volume': 0,
    }),
    ('Mercatox', {
        'software': 'abc',
        'volume': 0,
    }),
    ('YunEx', {
        'software': 'abc',
        'volume': 0,
    }),
    ('Poloniex', {
        'software': 'abc',
        'volume': 0,
    }),
    ('Indodax', {
        'software': 'abc',
        'volume': 0,
    }),
    ('CROSS', {
        'software': 'abc',
        'volume': 0,
    }),
    ('STEX', {
        'software': 'abc',
        'volume': 0,
    }),
    ('digitalexchange.id', {
        'software': 'abc',
        'volume': 0,
    }),
    ('WaziriX', {
        'software': 'abc',
        'volume': 0,
    }),
    ('Dex-Trade', {
        'software': 'abc',
        'volume': 0,
    }),
    ('Tokenomy', {
        'software': 'abc',
        'volume': 0,
    }),
    ('Coinsuper', {
        'software': 'abc',
        'volume': 0,
    }),
    ('Upbit', {
        'software': 'bchn',
        'volume': 0,
    }),
    ('others', {
        'software': 'unknown',
        'volume': 0,
    }),
])

EXCHANGES_SUM = OrderedDict([
    ('abc', 0),
    ('bchn', 0),
    ('both', 0),    
    ('unknown', 0),    
])

def print_market_pair_data(d, volume=1):
    print(
        d['exchange']['name'],
        d['market_pair_base']['exchange_symbol'],
        d['market_pair_quote']['exchange_symbol'],
        volume,
        d['category'],
        d['market_score'],
        d['market_reputation'],
    )


def update_exchanges():
    url = "https://web-api.coinmarketcap.com/v1/cryptocurrency/market-pairs/latest?aux=num_market_pairs,category,market_url,notice,price_quote,effective_liquidity,market_score,market_reputation&convert=USD&id=1831&limit=1000&sort=cmc_rank"
    data = requests.get(url).json()['data']['market_pairs']
    print()
    for d in data:
        volume = d['quote']['USD']['volume_24h']
        if volume:
            volume = int(volume / (10**6)) + 1
        else:
            volume = 1
        exchange_name = d['exchange']['name'].split()[0]
        
        ex = EXCHANGES.get(exchange_name)
        if ex:
            ex['volume'] += volume
        else:
            EXCHANGES['others']['volume'] += volume

        software = 'unknown'
        if ex:
            software = ex['software']
        if 'ABC' in d['market_pair_base']['exchange_symbol']:
            software = 'abc'        
            print_market_pair_data(d, volume)
        EXCHANGES_SUM[software] += volume

            
    print()
    for name, d in EXCHANGES.items():
        print(name, d['volume'], d['software'])
        
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
                for software, sd in SOFTWARE.items():
                    if sd['match'](block):
                        if md['software'] != software:
                            log.warning("Miner {} runs {}, not {}".format(miner, software, md['software']))
                        break
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
        labels.append("Miner " + miner + " (" + md['software'].upper() + ")")
        sizes.append(len(md['blocks']))
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
        labels.append("Mining " + software.upper())
        sizes.append(len(sd['blocks']))
        explode.append(0.1)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    
    # -- Exchanges
    update_exchanges()
    labels = []
    sizes = []
    explode = []
    expl_factor = 0
    for exchange, ed in sorted(EXCHANGES.items(), key=lambda a: a[1]['volume'], reverse=True):
        if ed['software'] == 'unknown':
            continue
        labels.append(exchange + " (" + ed['software'].upper() + ")")
        sizes.append(ed['volume'])
        if True or ed['volume'] < 10:
            expl_factor += 0.1
            explode.append(expl_factor)
        else:
            explode.append(0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='', shadow=True, startangle=90)
    ax1.axis('equal')

    # -- Exchanges SUM
    labels = []
    sizes = []
    explode = []
    for software, volume in EXCHANGES_SUM.items():
        labels.append("Exchanges using " + software.upper())
        sizes.append(volume)
        explode.append(0.0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    
    
    plt.show()
    