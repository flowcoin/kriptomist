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
        
        
from sources.binance import Binance
from sources.bitstamp import Bitstamp
from sources.tokens import Tokens
from sources.livecoin import Livecoin

def all():
    return [Binance, Bitstamp, Tokens, Livecoin]
    
def price(sym):
    ret = {}
    for Ex in all():
        try:
            price = Ex.price(sym)
            ret[Ex] = price
        except:
            continue
    return ret