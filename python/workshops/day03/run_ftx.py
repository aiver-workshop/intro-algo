"""
Register a market data callback to process data in realtime.

This callback will be the entry point to a trading strategy.

"""

import asyncio
from ftx_ans import FtxManager
import logging
import sys
from lib.interface import OrderBook
from lib.metrics import LatencyMetric


# to keep track of market data update frequency
book_latency = LatencyMetric()


# this will be the entry point to a trading strategy
# TODO call mark() on book_latency object
def ftx_depth_callback(contract_name: str, book: OrderBook):
    pass


# TODO log the mean latency
async def print_latency():
    await asyncio.sleep(1)


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

    # start FTX connection and register callbacks.
    contracts = {'ETH-PERP'}
    ftx = FtxManager(symbol=contracts)
    ftx.register_depth_callback(ftx_depth_callback)
    ftx.connect()

    # loop till ready
    while True:
        asyncio.run(print_latency())
