import logging
log = logging.getLogger("coinmarketcap")

import json
from datetime import datetime, timedelta
import time

from bs4 import BeautifulSoup as Soup

from util import div0, series_fill_zeroes, normalize
from fetcher import Fetcher

NUM_COINS = 100

URL_ALLPAGE = "https://coinmarketcap.com/all/views/all/?_={}"
URL_COINPAGE = "https://coinmarketcap.com/currencies/{}/"
URL_PRICES = "https://web-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical?convert=USD,BTC&format=chart_crypto_details&id={}&interval=1d&time_end={}&time_start=2018-01-01"


def _get_coins_from_allpage(text):
        coins = []
        soup = Soup(text, "html.parser")
        table = soup.find("table", {'class': 'summary-table'})
        rows = table.findAll('tr')
        for row in rows[1:NUM_COINS+1]:
            coin = row.findAll('td')[1].a['href'].split("/")[-2] 
            coins.append(coin)
        return coins

def _get_data_from_coinpage(text):
    soup = Soup(text, "html.parser")
    return json.loads(soup.find('script', {'id': '__NEXT_DATA__'}).text)


class Coinmarketcap:
    def __init__(self, coin):
        self.coin = coin
        self.init()
    
    @classmethod
    def list_coins(cls):
        return Fetcher(_get_coins_from_allpage).get(URL_ALLPAGE.format(datetime.now().strftime("%Y_%m_%d")))
    
    def init(self):        
        d = Fetcher(_get_data_from_coinpage).get(URL_COINPAGE.format(self.coin))
        
        self.id = list(d['props']['initialState']['cryptocurrency']['info']['data'].keys())[0]
        self.info = d['props']['initialState']['cryptocurrency']['info']['data'][self.id]
        self.rank = d['props']['initialState']['cryptocurrency']['quotesLatest']['data'][self.id]['cmc_rank']
        
        self.sub = None
        try:
            self.sub = self.info['urls']['reddit'][0].split("/")[-1]
        except:
            print("sub = None")
        
        t = 6*3600 * int(time.time()/(6*3600)) + 6*3600        
        js = Fetcher(json.loads).get(URL_PRICES.format(self.id, t))
        

        self.rawdata = js['data']

        self.btc_series = [(datetime.strptime(k.split("T")[0], "%Y-%m-%d"), v['BTC'][0])
            for k, v in self.rawdata.items()
        ]
        series_fill_zeroes(self.btc_series)
        normalize(self, "btc_series")
        
        self.usd_series = [(datetime.strptime(k.split("T")[0], "%Y-%m-%d"), v['USD'][0])
            for k, v in self.rawdata.items()
        ]
        series_fill_zeroes(self.usd_series)
        normalize(self, "usd_series")

    def _p(self, days):
        if self.coin == 'bitcoin':
            return self.usd_series[-(days+1)][1]
        else:
            return self.btc_series[-(days+1)][1]
            

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cmc = Coinmarketcap('bitcoin-cash')
    print(cmc.btc_series[-10:])

    
