from dydx import DydxManager
import logging
import sys
import time
import asyncio
from lib.interface import OrderBook
from lib.metrics import LatencyMetric


book_latency = LatencyMetric()


def book_callback(contract_name: str, book: OrderBook):
    book_latency.mark()


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

    symbols = {'ETH-USD'}
    dydx = DydxManager(symbol=symbols, web3_http_provider_url='https://mainnet.infura.io/v3/9a7bac104fd14b5e936862563224f8be')
    dydx.register_depth_callback(book_callback)
    dydx.connect()

    # loop till ready
    while True:
        if dydx.not_ready():
            logging.info("Not ready to trade")
            time.sleep(1)
        else:
            break

    while True:
        if dydx.not_ready():
            logging.info("Not ready to trade")
            time.sleep(1)
        else:
            asyncio.run(print_latency())
