import sys

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from util import moving_average


def _plot(coin, k, label=None, mut=lambda s: s):
    if not label:
        label = k
    s = mut(getattr(coin, k))
    plt.plot(
        [a[0] for a in s],
        [a[1] for a in s],
        label=label
    )
    
def draw_coin(coin):
    fig = plt.figure()
    fig.show()
    
    _plot(coin, 'usd_norm', label="{}/USD".format(coin.name))
    _plot(coin, 'btc_norm', label="{}/BTC".format(coin.name))
    _plot(coin, 'supply_norm', label="supply".format(coin.name))
    _plot(coin, 'subs_norm', label="r/{}".format(coin.cmc.sub))
    _plot(coin, 'flw_norm', label="@{}".format(coin.cmc.twt))

    _plot(coin, 'btc_norm', label="{}/BTC MA28".format(coin.name), mut=lambda s: moving_average(s, days=28))
    _plot(coin, 'btc_norm', label="{}/BTC MA100".format(coin.name), mut=lambda s: moving_average(s, days=100))

    _draw_end(fig)


def _draw_end(fig):
    plt.legend(loc='upper left')

    ax = fig.axes[0]
    xa = ax.get_xaxis()

    ax.get_xaxis().set_major_locator(mdates.MonthLocator(interval=1))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

def draw_old(km):
    cmc = km.cmc
    srs = km.srs

    fig = plt.figure()
    fig.show()    
    
    if cmc.coin != 'bitcoin':
        plt.plot(
            [a[0] for a in cmc.btc_series_norm],
            [a[1] for a in cmc.btc_series_norm],
            label="{}/BTC".format(cmc.coin)
        )
    else:
        plt.plot(
            [a[0] for a in cmc.usd_series_norm],
            [a[1] for a in cmc.usd_series_norm],
            label="{}/USD".format(cmc.coin)
        )
    plt.plot(
        [a[0] for a in srs.series_norm],
        [a[1] for a in srs.series_norm],
        label="{}/reddit".format(srs.sub)
    )
    plt.plot(
        [a[0] for a in cmc.supply_norm],
        [a[1] for a in cmc.supply_norm],
        label="supply"
    )

    _draw_end(fig)

def draw_custom(data):
    fig = plt.figure()
    fig.show()    

    for label, series in data.items():
        plt.plot(
            [a[0] for a in series],
            [a[1] for a in series],
            label=label
        )

    _draw_end(fig)
        
if __name__ == '__main__':
    from coinmarketcap import Coinmarketcap
    from util import normalize
    
    args = sys.argv[1:]
    if args and args[0] == 'bch,bsv':
        bch = Coinmarketcap('bitcoin-cash')
        bsv = Coinmarketcap('bitcoin-sv')
        bch.btc_series = bch.btc_series[-4*30:]
        bsv.btc_series = bsv.btc_series[-4*30:]
        normalize(bch, 'btc_series')
        normalize(bsv, 'btc_series')
        draw_custom({'bch': bch.btc_series_norm, 'bsv': bsv.btc_series_norm})
        



