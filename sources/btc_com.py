import requests
import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup


class BtcCom:
    URL_DIFF = "https://btc.com/stats/diff" 
    
    @classmethod
    def get_next_diff(cls):
        r = requests.get(cls.URL_DIFF, headers={'user-agent': 'flowcoin/kriptomist'})
        soup = BeautifulSoup(r.text, "html.parser")
        
        next_diff = int(soup.find('div', {'class': 'diff-summary'}).findAll('dd')[2].span.text.replace(",", ""))
        days = int(re.findall('([0-9]+) Day', soup.find('div', {'class': 'diff-summary'}).findAll('dd')[3].text)[0])
        if days < 1:
            days = 1
        return (datetime.now() + timedelta(days=1), next_diff)