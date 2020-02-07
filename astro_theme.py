import logging
log = logging.getLogger('astro_theme')

import requests
session = requests.Session()

import re
from datetime import datetime
from collections import OrderedDict
from pprint import pprint
import random

from astro_def import OBJECTS


class AstroTheme:
    def __init__(self):
        r = session.get("https://www.astrotheme.com/transits_ephemerides_chart.php")
        
    def get(self, t):
        global r3
        log.debug(t.strftime("%Y-%m-%d %H:%M"))
        data2 = {
            "date[d]": int(t.strftime("%d")),
            "date[F]": int(t.strftime("%m")),
            "date[Y]": int(t.strftime("%Y")),
            "heure[H]": int(t.strftime("%H")),
            "heure[i]": int(t.strftime("%M")),
            "ville": "Reykjav\u00edk (Capital Region), Iceland",
            "theme": "",
            "prenom": "",
            "date_t[d]": 15,
            "date_t[F]": 7,
            "date_t[Y]": 1970,
            "heure_t[H]": 12,
            "heure_t[i]": 0,
            "ville_t": 0,
            "_qf_s1_next.x": random.randint(1, 10),
            "_qf_s1_next.y": random.randint(1, 10),
            "atlas": "",
            "atlas_t": "",
            "celebrite": "null",            
            "_qf_default": "s1:next",    
        }
        r2 = session.post("https://www.astrotheme.com/transits_ephemerides_chart.php", data=data2)
        
        data3 = {
            "_qf_s2_next.x": random.randint(1, 10),
            "_qf_s2_next.y": random.randint(1, 10),
            "_qf_default": "s2:next",
        }
        r3 = session.post("https://www.astrotheme.com/transits_ephemerides_chart.php", data=data3)
        
        d = OrderedDict()
        for obj in OBJECTS:
            log.debug(obj)
            a = re.findall(obj + r" (\d+)°(\d+)' (&#1071; )?(\w+)", r3.text)[0]
            d[obj] = (a[3], a[0])
        return d

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    at = AstroTheme()
    d = at.get(datetime(2020, 2, 6, 12, 0))
    pprint(d)
    
