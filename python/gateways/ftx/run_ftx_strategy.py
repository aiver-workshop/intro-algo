from ftx import FtxManager
from lib.interface import OrderBook
import lib.charting as charting
import logging
import sys
import time
import numpy as np


def get_mid(book: OrderBook) -> float:
    return 0.5 * (book.asks[0].price + book.bids[0].price)


if __name__ == '__main__':
    # logging stuff
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    handler.setFormatter(logFormatter)
    root.addHandler(handler)

    logging.info("main program starts")

    # charting setup
    x_vec = np.linspace(0, 1, 100)[0:-1]
    y_vec = np.zeros(len(x_vec))
    line1 = []

    # start FTX connection
    symbols = {'BTC/USD', 'BTC-PERP'}
    ftx = FtxManager(symbol=symbols)
    ftx.connect()

    while True:

        if ftx.not_ready():
            logging.info("Not ready to trade")
        else:
            spot_book = ftx.get_ticker('BTC/USD')
            future_book = ftx.get_ticker('BTC-PERP')

            if spot_book is None:
                logging.info('Error - spot book')

            if future_book is None:
                logging.info('Error - swap book')

            spread = get_mid(future_book) - get_mid(spot_book)
            logging.info('Spread: %s' % spread)

            y_vec[-1] = spread
            line1 = charting.live_plotter(x_vec, y_vec, line1, title='(Future - Spot) Spread')
            y_vec = np.append(y_vec[1:], 0.0)

        time.sleep(0.5)
