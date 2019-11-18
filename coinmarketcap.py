import logging
log = logging.getLogger("coinmarketcap")

import json
from datetime import datetime, timedelta
import time

from bs4 import BeautifulSoup as Soup

from util import div0, series_fill_zeroes
from fetcher import Fetcher


URL_COINPAGE = "https://coinmarketcap.com/currencies/{}/"
URL_PRICES = "https://web-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical?convert=USD,BTC&format=chart_crypto_details&id={}&interval=1d&time_end={}&time_start=2018-01-01"


def _get_data_from_coinpage(text):
    soup = Soup(text, "html.parser")
    return json.loads(soup.find('script', {'id': '__NEXT_DATA__'}).text)


class Coinmarketcap:
    def __init__(self, coin):
        self.coin = coin
        self.init()
        
    def init(self):        
        d = Fetcher(_get_data_from_coinpage).get(URL_COINPAGE.format(self.coin))
        
        self.id = list(d['props']['initialState']['cryptocurrency']['info']['data'].keys())[0]
        self.info = d['props']['initialState']['cryptocurrency']['info']['data'][self.id]
        self.rank = d['props']['initialState']['cryptocurrency']['quotesLatest']['data'][self.id]['cmc_rank']
        
        self.subreddit = None
        try:
            self.subreddit = self.info['urls']['reddit'][0].split("/")[-1]
        except:
            print("subreddit = None")
        
        t = 1000 * int(time.time()/1000) + 1000        
        js = Fetcher(json.loads).get(URL_PRICES.format(self.id, t))
        

        self.rawdata = js['data']

        self.btc_series = [(datetime.strptime(k.split("T")[0], "%Y-%m-%d"), v['BTC'][0])
            for k, v in self.rawdata.items()
        ]
        series_fill_zeroes(self.btc_series)
        
        self.usd_series = [(datetime.strptime(k.split("T")[0], "%Y-%m-%d"), v['USD'][0])
            for k, v in self.rawdata.items()
        ]
        series_fill_zeroes(self.usd_series)
            

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cmc = Coinmarketcap('bitcoin-cash')
    print(cmc.btc_series[-10:])

    
