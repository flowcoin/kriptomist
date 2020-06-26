import sys

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from util import moving_average, price_diff, series_to_dict, series_shift
from coin import Coin


def _plot(coin, k, label=None, mut=lambda s: s):
    if not label:
        label = k
    s = mut(getattr(coin, k))
    plt.plot(
        [a[0] for a in s],
        [a[1] for a in s],
        label=label
    )

def _plot_corr(s1, s2, label=None, style="k--"):
    if not label:
        label = "correlation"
    d1 = series_to_dict(price_diff(s1))
    d2 = series_to_dict(price_diff(s2))
    s = []
    for a in s1:
        if a[0] not in d2:
            continue
        if d1[a[0]] * d2[a[0]] > 0:
            s.append((a[0], 100))
        else:
            s.append((a[0], 0))
    s = moving_average(s, days=28)
    plt.plot(
        [a[0] for a in s],
        [a[1] for a in s],
        style,
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

    #_plot(coin, 'usd_norm', label="{}/USD MA28".format(coin.name), mut=lambda s: moving_average(s, days=28))
    #_plot(coin, 'usd_norm', label="{}/USD MA100".format(coin.name), mut=lambda s: moving_average(s, days=100))

    #_plot(coin, 'usd', label="{}/USD diff".format(coin.name), mut=lambda s: price_diff(s))
    #_plot(Coin('bitcoin'), 'usd', label="bitcoin/USD diff", mut=lambda s: price_diff(s))

    _plot_corr(Coin('bitcoin').usd_norm, coin.usd_norm, label="{}/USD corr_btc".format(coin.name))
    _plot_corr(Coin('bitcoin').usd_norm, coin.btc_norm, label="{}/BTC corr_btc".format(coin.name), style="k:")
    _plot_corr(Coin('bitcoin').usd_norm, series_shift(coin.usd_norm, 1), label="{}/USD next day corr_btc".format(coin.name), style="y:")
    _plot_corr(Coin('bitcoin').usd_norm, series_shift(coin.usd_norm, -1), label="{}/USD next day corr_btc".format(coin.name), style="b:")

    _draw_end(fig)


def _draw_end(fig):
    plt.legend(loc='upper left')

    ax = fig.axes[0]

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
    from coin import Coin
    from coinmarketcap import Coinmarketcap
    from util import normalize
    
    args = sys.argv[1:]
    if args and args[0] == 'bch,bsv':
        bch = Coin('bitcoin-cash')
        bsv = Coin('bitcoin-sv')
        bch.btc = bch.btc[-4*30:]
        bsv.btc = bsv.btc[-4*30:]
        normalize(bch, 'btc')
        normalize(bsv, 'btc')
        draw_custom({'bch': bch.btc_norm, 'bsv': bsv.btc_norm})
    if args and args[0] == 'btc,tether':
        btc = Coin('bitcoin')
        tether = Coin('tether')
        draw_custom({'tether supply': tether.supply_norm, 'btc': btc.usd_norm})
    if args and args[0] == 'cro,mco':
        cro = Coin('crypto-com-coin')
        mco = Coin('crypto-com')
        draw_custom({
            'cro': cro.usd_norm,
            'mco': mco.usd_norm,
            'r/{}'.format(cro.cmc.sub): cro.subs_norm,
            '@{}'.format(cro.cmc.twt): cro.flw_norm,
        })
        



