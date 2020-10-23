import sys

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import config
from coin import Coin
from sources.coinmarketcap import Coinmarketcap
from sources.blockchain_com import BlockchainCom
from sources.btc_com import BtcCom
from util import moving_average, price_diff, series_to_dict, series_shift, normalize


def _plot(coin, k, mut=lambda s: s, **kwargs):
    if not kwargs.get("label"):
        kwargs["label"] = k
    s = mut(getattr(coin, k))
    plt.plot(
        [a[0] for a in s],
        [a[1] for a in s],
        **kwargs
    )

def _plot_corr(s1, s2, **kwargs):
    if not kwargs.get("label"):
        kwargs["label"] = "correlation"
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
        **kwargs
    )
    
def draw_coin(coin):
    fig = plt.figure()
    fig.show()
    
    if 'usd' in config.CHART_METRICS:
        _plot(coin, 'usd_norm', label="{}/USD".format(coin.name), color="blue", linestyle="-")
    if coin.name != 'bitcoin':
        if 'btc' in config.CHART_METRICS:
            _plot(coin, 'btc_norm', label="{}/BTC".format(coin.name), color="blue", linestyle="--")
    if 'supply' in config.CHART_METRICS:
        _plot(coin, 'supply_norm', label="supply".format(coin.name), color="green", linestyle="--")
    if coin.cmc.sub:
        if 'subs' in config.CHART_METRICS:
            _plot(coin, 'subs_norm', label="r/{} subscribers".format(coin.cmc.sub), color="red", linestyle="-", linewidth=2)
        if 'asubs' in config.CHART_METRICS:
            _plot(coin, 'asubs_norm', label="r/{} active users".format(coin.cmc.sub), color="red", linestyle=":", linewidth=2)
    if coin.cmc.twt:
        if 'flw' in config.CHART_METRICS:
            _plot(coin, 'flw_norm', label="@{} followers".format(coin.cmc.twt), color="cyan", linestyle="-", linewidth=2)

    if coin.name != 'bitcoin':
        if 'btcusd' in config.CHART_METRICS:
            _plot(Coin('bitcoin'), 'usd_norm', label="BTC/USD", color="orange", linestyle="--")

    if 'ma28' in config.CHART_METRICS:
        _plot(coin, 'usd_norm', label="{}/USD MA28".format(coin.name), mut=lambda s: moving_average(s, days=28))
    if 'ma100' in config.CHART_METRICS:    
        _plot(coin, 'usd_norm', label="{}/USD MA100".format(coin.name), mut=lambda s: moving_average(s, days=100))

    if 'xusddiff' in config.CHART_METRICS:
        _plot(coin, 'usd', label="{}/USD diff".format(coin.name), mut=lambda s: price_diff(s))
    
    if coin.name != 'bitcoin':
        if 'btcusddiff' in config.CHART_METRICS:
            _plot(Coin('bitcoin'), 'usd', label="BTC/USD diff", mut=lambda s: price_diff(s))

    if coin.name != 'bitcoin':
        if 'btcusdxusdcorr' in config.CHART_METRICS:
            _plot_corr(Coin('bitcoin').usd_norm, coin.usd_norm, label="{}/USD corr_btc".format(coin.name), color="black", linestyle="--")
        if 'btcusdxbtccorr' in config.CHART_METRICS:
            _plot_corr(Coin('bitcoin').usd_norm, coin.btc_norm, label="{}/BTC corr_btc".format(coin.name), color="black", linestyle=":")
        if 'xusdnextdaycorrbtc' in config.CHART_METRICS:
            _plot_corr(Coin('bitcoin').usd_norm, series_shift(coin.usd_norm, 1), label="{}/USD next day corr_btc".format(coin.name), style="y:")
        if 'xusdprevdaycorrbtc' in config.CHART_METRICS:
            _plot_corr(Coin('bitcoin').usd_norm, series_shift(coin.usd_norm, -1), label="{}/USD prev day corr_btc".format(coin.name), style="b:")

    if coin.name == 'bitcoin':
        if 'tethersupply' in config.CHART_METRICS:
            _plot(Coin('tether'), "supply_norm", label="Tether supply", color="green", linestyle=":")

        if 'ntx' in config.CHART_METRICS or 'ntxsquared' in config.CHART_METRICS:
            coin.n_transactions = BlockchainCom.fetch_data("n-transactions")
            normalize(coin, "n_transactions")
            coin.n_transactions_squared = [(a[0], a[1]**2) for a in coin.n_transactions]
            normalize(coin, "n_transactions_squared")
            if 'ntx' in config.CHART_METRICS:
                _plot(coin, "n_transactions_norm", label="n_transactions", color="violet", linestyle=":")
            if 'ntxsquared' in config.CHART_METRICS:
                _plot(coin, "n_transactions_squared_norm", label="n_transactions_squared", color="violet", linestyle=":")
    
        if 'difficulty' in config.CHART_METRICS:
            coin.difficulty = BlockchainCom.fetch_data("difficulty")
            coin.difficulty.append(BtcCom.get_next_diff())
            normalize(coin, "difficulty")
            _plot(coin, "difficulty_norm", label="difficulty", color="brown", linestyle="--")

        if 'hashrate' in config.CHART_METRICS:
            coin.hash_rate = BlockchainCom.fetch_data("hash-rate")
            normalize(coin, "hash_rate")
            _plot(coin, "hash_rate_norm", label="hash_rate", color="brown", linestyle=":")
    
    _draw_end(fig)


def _draw_end(fig, show_yaxis=False):
    plt.legend(loc='upper left')

    ax = fig.axes[0]

    ax.get_xaxis().set_major_locator(mdates.MonthLocator(interval=4))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.get_yaxis().set_visible(show_yaxis)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    if config.SIGNATURE_IN_CHART:
        signaturebar(fig, config.CHART_SIGNATURE)

    fig.canvas.draw()
    fig.canvas.flush_events()


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
        linestyle = "-"
        if label.startswith("[:]"):
            linestyle = ":"
        elif label.startswith("[--]"):
            linestyle = "--"
        plt.plot(
            [a[0] for a in series],
            [a[1] for a in series],
            label=label,
            linestyle=linestyle
        )

    _draw_end(fig, show_yaxis=True)

def signaturebar(fig,text,fontsize=10,pad=5,xpos=20,ypos=7.5,
                 rect_kw = {"facecolor":"#EEEEEE", "edgecolor":"#DDDDDD"},
                 text_kw = {"color":"#AAAAAA"}):
    w,h = fig.get_size_inches()
    height = ((fontsize+2*pad)/72.)/h
    rect = plt.Rectangle((0,0),1,height, transform=fig.transFigure, clip_on=False,**rect_kw)
    fig.axes[0].add_patch(rect)
    fig.text(xpos/72./h, ypos/72./h, text,fontsize=fontsize,**text_kw)
    fig.subplots_adjust(bottom=fig.subplotpars.bottom+height)

       
if __name__ == '__main__':    
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
    if args and args[0] == 'ntx':
        btc = Coin('bitcoin')
        btc.n_transactions_squared = [(a[0], a[1]**2) for a in BlockchainCom.fetch_data("n-transactions")]
        btc.difficulty = [(a[0], a[1] / 50) for a in BlockchainCom.fetch_data("difficulty") + [BtcCom.get_next_diff()]]
        btc.hashrate = [(a[0], a[1] * 2828.42) for a in BlockchainCom.fetch_data("hash-rate")]
        draw_custom({
            'tx_count_squared': btc.n_transactions_squared,
            'tx_count_squared MA365': moving_average(btc.n_transactions_squared, days=365),
            'btc_market_cap': [(a[0], a[1] * btc.supply[i][1]) for i, a in enumerate(btc.usd)],
            'btc_market_cap MA100': moving_average([(a[0], a[1] * btc.supply[i][1]) for i, a in enumerate(btc.usd)], days=100),
            'tether_supply (x25)': [(a[0], a[1] * 25) for a in Coin("tether").supply],
            '[--] difficulty (/50)': btc.difficulty,
            #'[:] hashrate': btc.hashrate,
            '[:] hashrate MA7 (x2828.42)': moving_average(btc.hashrate, days=7)
        })

