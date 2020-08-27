import logging
log = logging.getLogger('livecoin')

from sources.exchange import Exchange


class Livecoin(Exchange):
    URL_PRICES = "https://api.livecoin.net/exchange/ticker"
    URL_PRICE = "https://api.livecoin.net/exchange/ticker?currencyPair={}/USDT"

    @classmethod
    def prices(cls):
        data = cls.request(cls.URL_PRICES)
        return {d['symbol'][:-5]: float(d['last']) for d in data if d['symbol'].endswith("/USDT")}

    @classmethod
    def price(cls, sym):
        data = cls.request(cls.URL_PRICE.format(sym))
        assert data['symbol'] == f'{sym}/USDT'
        assert data['cur'] == sym
        return float(data['last'])
        

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    Livecoin.test()