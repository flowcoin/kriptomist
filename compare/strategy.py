import logging
log = logging.getLogger('strategy')

import sys

from sources.binance import Binance
import draw
import util


FEE = 0.2
COLORS = ['blue', 'purple', 'green', 'red']
PLOT_PARAMS = [
    [('linestyle', '-')],
    [('linestyle', '--')],
    [('linestyle', ':')],
    [('linestyle', '-.')],
]


def profit_series(klines, wait):
    ret = []
    for i, d in enumerate(klines[:-wait]):
        delta = 100 * (d['close'] / d['open'] - 1)
        profit = 0
        if delta > FEE:
            profit = 1000 * (max(dd['high'] for dd in klines[i+1:i+1+wait]) / d['close'] - 1) 
        elif delta < -FEE:
            profit = 1000 * (1 - min(dd['low'] for dd in klines[i+1:i+1+wait]) / d['close'])
        ret.append((d['time'], profit))
    return ret
    
    
if __name__ == '__main__':
    syms = sys.argv[1:]
    
    D = {}
    for i, sym in enumerate(syms):
        klines = Binance.klines(sym)
        for ii, wait in enumerate([120//5]):
            D['{} {}m'.format(sym, wait*5)] = (profit_series(klines, wait), dict(PLOT_PARAMS[ii] + [('color', COLORS[i])]))
        D['{} delta'.format(sym)] = ([(d['time'], 1000 * (d['close'] / d['open'] - 1)) for d in klines], {'color': COLORS[i], 'marker': '.'})    
    
    draw.draw_custom_params(D)