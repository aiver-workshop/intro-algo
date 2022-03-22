import asyncio
from ftx import FtxManager
import logging
import sys
import time
from lib.events import OrderEvent
from lib.interface import OrderBook
from lib.metrics import LatencyMetric


# to keep track of market data update frequency
book_latency = LatencyMetric()


def ftx_depth_callback(contract_name: str, book: OrderBook):
    book_latency.mark()


def ftx_execution_callback(order_event: OrderEvent):
    logging.info('Execution callback: {}'.format(order_event))


async def print_latency():
    logging.info('Processing latency: %.2f ms' % book_latency.get_mean())

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
    ftx.register_execution_callback(ftx_execution_callback)
    ftx.connect()

    # loop till ready
    while True:
        if ftx.not_ready():
            logging.info("Not ready to trade")
            time.sleep(1)
        else:
            asyncio.run(print_latency())