import sys
import time

import requests


if __name__ == '__main__':
    sym = sys.argv[1]
    cmp = sys.argv[2]
    price = float(sys.argv[3])

    while True:
        idx_price = float(requests.get("https://fapi.binance.com/fapi/v1/premiumIndex?symbol={}".format(sym)).json()['indexPrice'])
        print(sym, idx_price)
        if cmp == '>' and idx_price > price:
            print("\a")
            print("{} > {}".format(idx_price, price))
        elif cmp == '<' and idx_price < price:
            print("\a")
            print("{} < {}".format(idx_price, price))
        
        time.sleep(1)

