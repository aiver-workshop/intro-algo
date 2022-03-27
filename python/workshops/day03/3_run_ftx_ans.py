
import asyncio
import logging
import sys
from lib.interface import OrderBook
from lib.metrics import LatencyMetric
ftx = __import__('2_ftx_ans')   # note how we import filename that starts with a number


# to keep track of market data update frequency
book_latency = LatencyMetric()


# this callback will be the entry point to a trading strategy
def ftx_depth_callback(contract_name: str, book: OrderBook):
    book_latency.mark()


async def print_latency():
    await asyncio.sleep(1)
    logging.info('Market data latency: %.2f ms' % book_latency.get_mean())


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
    ftx = ftx.FtxManager(symbol=contracts)
    ftx.register_depth_callback(ftx_depth_callback)
    ftx.connect()

    # loop till ready
    while True:
        asyncio.run(print_latency())
