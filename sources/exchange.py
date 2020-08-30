import logging
log = logging.getLogger('exchange')

import requests


class Exchange:    
    @classmethod
    def request(cls, url):
        return requests.get(url).json()
    
    @classmethod
    def test(cls):
        ret = cls.prices()
        log.info("prices(): " + str(ret))
        
        ret = cls.price('BTC')
        log.info("price('BTC'): " + str(ret))        
        
        if hasattr(cls, 'price_data'):
            ret = cls.price_data('BTC')
            log.info("price_data('BTC'): " + str(ret))        

        
from sources.coinbasepro import Coinbasepro
from sources.binance import Binance
from sources.bitstamp import Bitstamp
from sources.livecoin import Livecoin
from sources.tokens import Tokens


def all():
    return [Coinbasepro, Binance, Bitstamp, Livecoin, Tokens]
    
def price(sym):
    ret = {}
    for Ex in all():
        try:
            price = Ex.price(sym)
            ret[Ex] = price
        except:
            continue
    return ret