import requests
from datetime import datetime

from config import DATE_START

class BlockchainCom:
    API_URL = "https://api.blockchain.info/charts/{}?timespan=all&sampled=true&metadata=false&cors=true&format=json"
    
    @classmethod
    def fetch_data(cls, name):
        vals = requests.get(cls.API_URL.format(name)).json()["values"]
        return [
            (datetime.fromtimestamp(d["x"]), d["y"])
            for d in vals
            if datetime.fromtimestamp(d["x"]) > DATE_START
        ]
        