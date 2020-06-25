from datetime import datetime

import sqlite3

conn = sqlite3.connect('db/db.sqlite', isolation_level=None)
c = conn.cursor()

class Db:
    def __init__(self, coin):
        self.coin = coin
    
    @classmethod
    def create_tables(cls):
        c.execute("""
            CREATE TABLE coinday
            (
                coin text,
                day text,
                btc real,
                usd real,
                supply real,
                subs integer,
                flw integer,
                PRIMARY KEY (coin, day)
            )
        """)
    

    def write_data(self, d):
        try:
            c.execute("""
                insert into coinday values (?, ?, ?, ?, ?, ?, ?)    
            """, (
                self.coin,
                d["day"],
                d.get("btc", None),
                d.get("usd", None),
                d.get("supply", None),
                d.get("subs", None),
                d.get("flw", None),
            ))
        except sqlite3.IntegrityError:
            pass
            
    def get_series(self, s):
        c.execute("select day, {} from coinday where coin = ?".format(s), (self.coin,))
        return [(datetime.strptime(k, "%Y-%m-%d"), v) for k,v in c.fetchall() if v is not None]


if __name__ == '__main__':
    import os
    try:
        os.mkdir("db")
    except:
        pass
    Db.create_tables()

