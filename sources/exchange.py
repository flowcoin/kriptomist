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
        
        
from .binance import Binance
from .tokens import Tokens

def all():
    return [Binance, Tokens]