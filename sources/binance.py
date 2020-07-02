import logging
log = logging.getLogger('binance')

import requests
from pprint import pprint


URL_PRICES = "https://api.binance.com/api/v3/ticker/price"


class Binance:
    coin_symbol_prices = {}   
    
    @classmethod
    def get_coin_symbol_prices(cls):
        if not cls.coin_symbol_prices:
            csp = requests.get(URL_PRICES).json()
            for sp in csp:
                if sp["symbol"].endswith("USDT"):
                    sym = sp["symbol"][:-4]
                    cls.coin_symbol_prices[sym] = float(sp["price"])
        return cls.coin_symbol_prices
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    pprint(Binance.get_coin_symbol_prices())
