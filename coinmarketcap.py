import logging
log = logging.getLogger("coinmarketcap")

import json
from datetime import datetime, timedelta
import time

from bs4 import BeautifulSoup as Soup
import requests

from util import div0, series_fill_zeroes, normalize
from fetcher import Fetcher

NUM_COINS = 5000

URL_ALLPAGE = "https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?convert=USD,BTC&cryptocurrency_type=all&limit={}&sort=market_cap&sort_dir=desc&start=1"
URL_COINPAGE = "https://coinmarketcap.com/currencies/{}/"
URL_PRICES = "https://web-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical?convert=USD,BTC&format=chart_crypto_details&id={}&interval=1d&time_end={}&time_start=2018-01-01"

def _get_coins_from_allpage():
    return requests.get(URL_ALLPAGE.format(NUM_COINS)).json()

def _get_data_from_coinpage(text):
    soup = Soup(text, "html.parser")
    d = json.loads(soup.find('script', {'id': '__NEXT_DATA__'}).text)
    
    """
    d["mydata"] = dd = {}
    dd["max_supply"] = _get_supply("Max Supply", soup)
    if dd["max_supply"] == 0:
        dd["max_supply"] = _get_supply("Total Supply", soup)
    dd["circ_supply"] = _get_supply("Circulating Supply", soup)
    dd["supply_rel"] = div0(dd["circ_supply"], dd["max_supply"], z=lambda x: 0)
    """
    
    return d
    
def _get_supply(name, soup):
    try:
        t = soup.find("h5", text=name)
        return int(t.parent()[1].text.split(" ")[0].replace(",", ""))
    except:
        return 0
        
        
class Coinmarketcap:
    def __init__(self, coin, data={}):
        self.coin = coin
        self.data = data
        self.rank = data.get("cmc_rank", 0)
        self.init()
    
    def __repr__(self):
        s = "<cmc {}".format(self.coin)
        if self.usd_series:
            s += " ({}, {} USD)".format(self.usd_series[-1][0].strftime("%Y-%m-%d"), self.usd_series[-1][1])
        if self.btc_series:
            s += " ({}, {} satoshis)".format(self.btc_series[-1][0].strftime("%Y-%m-%d"), round((10**8) * self.btc_series[-1][1]))
        s += ">"
        return s
    
    @classmethod
    def list_coins(cls):
        return _get_coins_from_allpage()["data"]
        
    def init(self):        
        d = Fetcher(_get_data_from_coinpage).fetch(URL_COINPAGE.format(self.coin))
        
        self.id = list(d['props']['initialState']['cryptocurrency']['info']['data'].keys())[0]
        self.info = d['props']['initialState']['cryptocurrency']['info']['data'][self.id]
        if self.rank is None:
            self.rank = d['props']['initialState']['cryptocurrency']['quotesLatest']['data'][self.id]['cmc_rank']
        
        self.max_supply = round(self.data.get("max_supply", 0))
        if not self.max_supply:
            self.max_supply = round(self.data.get("total_supply", 0))
        if not self.max_supply:
            self.max_supply = 0
        self.circ_supply = round(self.data.get("circulating_supply", 0))
        if not self.circ_supply:
            self.circ_supply = 0
        
        self.supply_rel = div0(self.circ_supply, self.max_supply, z=lambda x: 0)
        
        self.sub = None
        try:
            self.sub = self.info['urls']['reddit'][0].split("/")[-1]
        except:
            log.debug("sub = None")
        
        self.fetch_prices()
            
    def fetch_prices(self):
        t = 6*3600 * int(time.time()/(6*3600)) + 6*3600        
        js = Fetcher(json.loads).fetch(URL_PRICES.format(self.id, t))
        

        self.rawdata = js['data']

        self.btc_series = [(datetime.strptime(k.split("T")[0], "%Y-%m-%d"), v['BTC'][0])
            for k, v in self.rawdata.items()
        ]
        if self.data:
            self.btc_series.append((datetime.now(), self.data["quote"]["BTC"]["price"]))
        series_fill_zeroes(self.btc_series)
        normalize(self, "btc_series")
        
        self.usd_series = [(datetime.strptime(k.split("T")[0], "%Y-%m-%d"), v['USD'][0])
            for k, v in self.rawdata.items()
        ]
        if self.data:
            self.usd_series.append((datetime.now(), self.data["quote"]["USD"]["price"]))
        series_fill_zeroes(self.usd_series)
        normalize(self, "usd_series")
        
        self.supply = []
        try:
            self.supply = [(datetime.strptime(k.split("T")[0], "%Y-%m-%d"), 10 * round(0.1 * div0(v['USD'][2], v['USD'][0])))
                for k, v in self.rawdata.items()
            ]
        except:
            pass
        series_fill_zeroes(self.supply)
        normalize(self, "supply")
        

    def _p(self, days):
        if self.coin == 'bitcoin':
            return self.usd_series[-(days+1)][1]
        else:
            return self.btc_series[-(days+1)][1]
            

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cmc = Coinmarketcap('bitcoin-cash')
    print(cmc.btc_series[-10:])

    
