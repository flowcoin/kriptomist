import logging
log = logging.getLogger('sim')

import sys
from datetime import datetime, timedelta
import copy
from pprint import pprint
import math
import random

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from coin import Coin
import util
import config
import draw
from sources.blockchain_com import BlockchainCom

btc = Coin('bitcoin')
btc.usd += [(btc.usd[-1][0] + timedelta(days=i), util.series_avg(btc.usd[-365:])) for i in range(1, 365)]
btc.usd_d = util.series_to_dict(btc.usd)
btc.supply += [(btc.supply[-1][0] + timedelta(days=i), btc.supply[-1][1]) for i in range(1, 365)]
btc.mcap = [(btc.usd[i][0], btc.usd[i][1] * btc.supply[i][1]) for i in range(len(btc.usd))]

btc.ntx = [(a[0], a[1]) for a in BlockchainCom.fetch_data("n-transactions") if a[0] in btc.usd_d]
_avg = util.series_avg(btc.ntx[-28:])
btc.ntx += [(btc.ntx[-1][0] + timedelta(days=i), _avg) for i in range(1, 400)]

tether = Coin('tether')
_avg = util.series_avg(util.series_abs_diff(tether.supply))
tether.supply += [(tether.supply[-1][0] + timedelta(days=i), tether.supply[-1][1] + _avg * i) for i in range(1, 365)]

world = {
    'tether_q': 0.5,
    'ntx_pwr': 0.5,
    'ntx_q': 0.5,
}

state = {}

def reset_state():
    state.update({
        'base_tether': 0,
        'base_ntx': 0,
        'series': [],
    })

reset_state()

best = {
    'series': [],
    'stdev': 2**256,
    'world': {},
}

scripts = open('compare/sim.txt').read().split('\n\n')

def exec_script(code):
    exec(code)
        
def evolve():
    for k, v in list(world.items()):
        if random.random() < 0.8:
            world[k] = random.random()
    
lines = {}

plt.ion()
fig = plt.figure()
lines['bitcoin'], = plt.plot([a[0] for a in btc.mcap], [a[1] for a in btc.mcap], label='bitcoin')
lines['tether'], = plt.plot([a[0] for a in tether.supply], [a[1] for a in tether.supply], label='tether')
lines['ntx_sqr'], = plt.plot([a[0] for a in btc.ntx], [a[1]**2 for a in btc.ntx], label='ntx_sqr')
lines['sim'], = plt.plot([a[0] for a in btc.mcap], [0 for a in btc.usd], label='sim')
plt.legend(loc='upper left')

def run_sim():
    global t, i
    state['series'] = []

    t = config.DATE_START - timedelta(days=1)
    i = -1
    while t < datetime.now() + timedelta(days=365):
        t += timedelta(days=1)
        if t not in btc.usd_d:
            continue
        
        for code in scripts:
            exec_script(code)

        i += 1
        state['series'].append((t, state['base_tether'] + state['base_ntx']))

    std = util.stdev(state['series'][100:-365], btc.mcap)
    if  std < best['stdev']:
        best['series'] = state['series']
        best['stdev'] = std
        best['world'] = copy.deepcopy(world)
        print()
        print("stdev = ", best['stdev'])
        pprint(best['world'])

        lines['sim'].set_ydata([a[1] for a in best['series']])
        fig.canvas.draw()
        fig.canvas.flush_events()

if __name__ == '__main__':
    while True:
        reset_state()
        evolve()
        run_sim()
    
    
    
    