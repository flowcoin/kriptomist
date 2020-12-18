""" Binance trades observer

Requirements:
- cryptoxlib-aio
- requests
"""

import logging
log = logging.getLogger('binance_trades')

import sys, os
import asyncio
from pprint import pprint
import random
from datetime import datetime

import requests

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.Pair import Pair
from cryptoxlib.version_conversions import async_run
from cryptoxlib.clients.binance.BinanceWebsocket import TradeSubscription, AggregateTradeSubscription

from cryptoxlib.clients.binance.BinanceWebsocket import BinanceWebsocket
BinanceWebsocket.WEBSOCKET_URI = "wss://fstream.binance.com/"

client = CryptoXLib.create_binance_client(None, None)
queue = asyncio.Queue()

MIN_QTY = 0
MIN_QTY_VOICE = 0

# -- util

def format_time(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").timestamp()
    

# -- producer

async def trade_update(response : dict) -> None:
    direction = "UP" if response['data']['m'] == False else "DOWN"
    q = int(100 * float(response['data']['q'])) / 100
    text = direction + " " + str(q)
    if q > MIN_QTY:
        print(text)
        if q > MIN_QTY_VOICE:
            await queue.put(text)
    
    
# -- consumer

async def reporter():
    while True:
        try:
            text = await queue.get()
            os.system('''PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('%s');"''' % text)
        except:
            log.exception('reporter')

# -- init

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    MIN_QTY = float(sys.argv[2])
    MIN_QTY_VOICE = float(sys.argv[3])

    client.compose_subscriptions([
        AggregateTradeSubscription(Pair(sys.argv[1], 'USDT'), callbacks = [trade_update]),
    ])

    loop = asyncio.get_event_loop()
    loop.create_task(client.start_websockets())
    loop.create_task(reporter())

    loop.run_forever()
