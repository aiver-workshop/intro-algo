import asyncio
import logging
import sys
from lib.interface import OrderBook
ftx = __import__('2_ftx_ans')


# TODO create a class to represent a candlestick (or bar) with open, high, low and close variables
class Bar:
    # create an empty bar
    def __init__(self):
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.reset()

    # copy the values of the provided bar
    def copy(self, _bar):
        pass

    # reset the values
    def reset(self):
        pass


# TODO this callback captures the open, high, low and close of a bar
def ftx_depth_callback(contract_name: str, book: OrderBook):
    pass


# TODO this method is triggered periodically to conclude a bar
async def capture_bar(period):
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

    logging.info("main program starts")

    # start FTX connection and register callbacks.
    contracts = {'BTC-PERP'}
    ftx = ftx.FtxManager(symbol=contracts)
    ftx.register_depth_callback(ftx_depth_callback)
    ftx.connect()

    # loop to capture candlestick periodically
    while True:
        asyncio.run(capture_bar(60))
