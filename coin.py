import logging
log = logging.getLogger("coin")

import json
from datetime import datetime, timedelta
import time

import requests

from util import div0, series_fill_zeroes, normalize
from fetcher import Fetcher
from db import Db
from coinmarketcap import Coinmarketcap

from config import NUM_COINS


URL_SUBS = "https://www.reddit.com/r/{}/about.json"        
URL_FLW = "https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names={}"

session = requests.Session()

        
class Coin:
    def __init__(self, name, data={}):
        self.name = name
        self.db = Db(name)
        self.data = data
        self.cmc = Coinmarketcap(self.name, data=data)        
        if data:
            self.update()
        self.sync()
    
    def __repr__(self):
        s = "<Coin {}".format(self.name)
        if self.usd:
            s += " ({}, {} USD)".format(self.usd[-1][0].strftime("%Y-%m-%d"), self.usd[-1][1])
        if self.btc:
            s += " ({}, {} satoshis)".format(self.btc[-1][0].strftime("%Y-%m-%d"), round((10**8) * self.btc[-1][1]))
        if self.supply:
            s += " ({}, {} coins)".format(self.supply[-1][0].strftime("%Y-%m-%d"), self.supply[-1][1])
        if self.subs:
            s += " ({}, {} subs)".format(self.subs[-1][0].strftime("%Y-%m-%d"), self.subs[-1][1])
        if self.flw:
            s += " ({}, {} flw)".format(self.flw[-1][0].strftime("%Y-%m-%d"), self.flw[-1][1])
        s += ">"
        return s
    
    @classmethod
    def from_cmc_data(cls, data):
        """
        {
            "id": 1,
            "name": "Bitcoin",
            "symbol": "BTC",
            "slug": "bitcoin",
            "num_market_pairs": 7622,
            "date_added": "2013-04-28T00:00:00.000Z",
            "tags": [
                "mineable"
            ],
            "max_supply": 21000000,
            "circulating_supply": 18106162,
            "total_supply": 18106162,
            "platform": null,
            "cmc_rank": 1,
            "last_updated": "2019-12-19T09:08:34.000Z",
            "quote": {
                "BTC": {
                    "price": 1,
                    "volume_24h": 4582055.85637907,
                    "percent_change_1h": 0,
                    "percent_change_24h": 0,
                    "percent_change_7d": 0,
                    "market_cap": 18106162,
                    "last_updated": "2019-12-19T09:08:34.000Z"
                },
                "USD": {
                    "price": 7055.76806905,
                    "volume_24h": 32329923402.043,
                    "percent_change_1h": -1.11995,
                    "percent_change_24h": 5.51485,
                    "percent_change_7d": -2.13367,
                    "market_cap": 127752879692.64648,
                    "last_updated": "2019-12-19T09:08:34.000Z"
                }
            }
        }        
        """
        return cls(data["slug"], data=data)
    
    def sync(self):
        for k in ["btc", "usd", "supply", "subs", "flw"]:
            setattr(self, k, self.db.get_series(k))
            series_fill_zeroes(getattr(self, k))
            normalize(self, k)
    
    def update(self):
        cmc = self.cmc
        D = {
            'day': datetime.now().strftime("%Y-%m-%d"),
            'btc': self.data["quote"]["BTC"]["price"],
            'usd': self.data["quote"]["USD"]["price"],
            'supply': div0(self.data["quote"]["USD"]["market_cap"], self.data["quote"]["USD"]["price"], z=lambda x: 0),
        }
        headers = {'user-agent': 'flowcoin/kriptomist ({})'.format(self.name)}
        if cmc.sub:
            try:
                D.update(subs=session.get(URL_SUBS.format(cmc.sub), headers=headers).json()["data"]["subscribers"])
            except:
                log.exception("cmc.sub")
        if cmc.twt:
            try:
                D.update(flw=session.get(URL_FLW.format(cmc.twt), headers=headers).json()[0]["followers_count"])
            except:
                log.exception("cmc.twt")
        self.db.write_data(D)
                    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    coin = Coin("bitcoin")
    print(coin.usd[-10:])
    
