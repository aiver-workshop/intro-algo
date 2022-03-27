"""
We are going to define a simple strategy that work on the spread between BTC future and spot on a single exchange

"""
import time

from lib.interface import OrderBook
import logging
import sys
from gateways.ftx.ftx import FtxManager


class Strategy:
    def __init__(self, symbol_1: str, symbol_2: str):
        self._symbol_1 = symbol_1
        self._symbol_2 = symbol_2
        self._book_1 = None
        self._book_2 = None
        self._spread = 0

    # a callback to process order book event
    def on_book_event(self, contract_name: str, book: OrderBook):
        if contract_name == self._symbol_1:
            self._book_1 = book
        elif contract_name == self._symbol_2:
            self._book_2 = book
        else:
            return

        # compute spread
        self._compute_spread()

    def _compute_spread(self):
        if self._book_1 and self._book_2:
            self._spread = get_mid(self._book_1) - get_mid(self._book_2)

    def get_spread(self):
        return self._spread


def get_mid(book: OrderBook) -> float:
    return 0.5 * (book.bids[0].price + book.asks[0].price)


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

