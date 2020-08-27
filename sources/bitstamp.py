import logging
log = logging.getLogger('bitstamp')

from sources.exchange import Exchange


class Bitstamp(Exchange):
    URL_PRICES = None
    URL_PRICE = "https://www.bitstamp.net/api/v2/ticker/{}usd/"

    @classmethod
    def prices(cls):
        return {'BTC': cls.price('BTC')}

    @classmethod
    def price(cls, sym):
        data = cls.request(cls.URL_PRICE.format(sym.lower()))
        return float(data['last'])
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    Bitstamp.test()