"""
We are going to define a simple strategy that work on the spread between BTC future and spot on a single exchange

"""
import time

from lib.interface import OrderBook
import logging
import sys
from gateways.ftx.ftx import FtxManager


# TODO
class Strategy:
    def __init__(self, symbol_1: str, symbol_2: str):
        pass

    # a callback to process order book event
    def on_book_event(self, contract_name: str, book: OrderBook):
        pass

    def _compute_spread(self):
        pass

    def get_spread(self):
        pass


if __name__ == '__main__':
    # logging stuff
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    handler.setFormatter(logFormatter)
    root.addHandler(handler)

    # define symbols
    symbol_1 = 'BTC-PERP'
    symbol_2 = 'BTC/USD'

    # create strategy
    strategy = Strategy(symbol_1, symbol_2)

    # create FTX manager, and register callback
    ftx = FtxManager(symbol={symbol_1, symbol_2})

    # register callback
    ftx.register_depth_callback(strategy.on_book_event)

    # start connection
    ftx.connect()

    # print the spread once a second
    while True:
        time.sleep(1)
        logging.info('Spread = {}'.format(strategy.get_spread()))

