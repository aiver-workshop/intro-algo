import asyncio
import logging
import sys
from lib.interface import OrderBook
ftx = __import__('2_ftx_ans')   # note how we import filename that starts with a number


class Bar:
    def __init__(self):
        self.reset()

    def reset(self):
        self.open = None
        self.high = 0
        self.low = 10000000
        self.close = None


bar = Bar()


# this callback will be the entry point to a trading strategy
def ftx_depth_callback(contract_name: str, book: OrderBook):
    mid = 0.5 * (book.bids[0].price + book.asks[0].price)

    if not bar.open:
        bar.open = mid

    if mid > bar.high:
        bar.high = mid

    if mid < bar.low:
        bar.low = mid

    bar.close = mid


async def capture_bar():
   print('O: ' + str(bar.open) + ' H: ' + str(bar.high) + ' L: ' + str(bar.low) + ' C: ' + str(bar.close))
   bar.reset()
   await asyncio.sleep(5)


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
        asyncio.run(capture_bar())
