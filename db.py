import logging
log = logging.getLogger("db")

import os
from datetime import datetime

import sqlite3

import config


conn = sqlite3.connect(os.path.join('db', config.DB_FILE), isolation_level=None)
c = conn.cursor()


class Db:
    def __init__(self, coin):
        self.coin = coin
    
    @classmethod
    def create_tables(cls):
        try:
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
                    asubs integer,
                    PRIMARY KEY (coin, day)
                )
            """)
            log.info("Database table `coinday` created")
        except sqlite3.OperationalError as e:
            log.warning(e)

            try:
                c.execute("""
                    ALTER TABLE coinday
                    ADD asubs integer
                """)
                log.info("Added field `coinday.asubs` - active subscribers")
            except sqlite3.OperationalError as e:
                log.warning(e)


    def write_data(self, d):
        try:
            c.execute("""
                insert into coinday values (?, ?, ?, ?, ?, ?, ?, ?)    
            """, (
                self.coin,
                d["day"],
                d.get("btc", None),
                d.get("usd", None),
                d.get("supply", None),
                d.get("subs", None),
                d.get("flw", None),
                d.get("asubs", None),
            ))
        except sqlite3.IntegrityError:
            pass
            
    def get_series(self, s):
        c.execute(f"select day, {s} from coinday where coin = ?", (self.coin,))
        return [(datetime.strptime(k, "%Y-%m-%d"), v) for k,v in c.fetchall() if v is not None]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Db.create_tables()
