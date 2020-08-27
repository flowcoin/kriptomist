import logging
log = logging.getLogger('tokens')

from .exchange import Exchange


class Tokens(Exchange):
    URL_PRICES = "https://api.tokens.net/public/currency/all/"
    URL_PRICE = "https://api.tokens.net/public/ticker/{}usdt/"

    @classmethod
    def prices(cls):
        data = cls.request(cls.URL_PRICES)
        return {sym: float(d['usdtValue']) for sym, d in data['currencies'].items()}

    @classmethod
    def price(cls, sym):
        data = cls.request(cls.URL_PRICE.format(sym.lower()))
        return float(data['last'])
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    Tokens.test()