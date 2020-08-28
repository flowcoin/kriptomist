import logging
log = logging.getLogger('coinbasepro')

from sources.exchange import Exchange


class Coinbasepro(Exchange):
    URL_PRICES = None
    URL_PRICE = "https://api.pro.coinbase.com/products/{}-USD/ticker"

    @classmethod
    def prices(cls):
        return {'BTC': cls.price('BTC')}

    @classmethod
    def price(cls, sym):
        data = cls.request(cls.URL_PRICE.format(sym))
        return float(data['price'])
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    Coinbasepro.test()