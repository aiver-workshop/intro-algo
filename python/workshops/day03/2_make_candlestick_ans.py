import asyncio
import logging
import sys
from lib.interface import OrderBook
ftx = __import__('2_ftx_ans')


# Create a class to represent a candlestick (or bar) with open, high, low and close variables
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
        self.open = _bar.open
        self.high = _bar.high
        self.low = _bar.low
        self.close = _bar.close

    # reset the values
    def reset(self):
        self.open = None
        self.high = 0
        self.low = 10000000
        self.close = None


# A global variable to capture candlestick info in the current period that is still developing
liveBar = Bar()

# A global variable to capture last candlestick
bar = Bar()


# This callback captures the open, high, low and close of a bar
def ftx_depth_callback(contract_name: str, book: OrderBook):
    mid = 0.5 * (book.bids[0].price + book.asks[0].price)

    if not liveBar.open:
        liveBar.open = mid

    if mid > liveBar.high:
        liveBar.high = mid

    if mid < liveBar.low:
        liveBar.low = mid

    liveBar.close = mid


# This method is triggered periodically to conclude a bar
async def capture_bar(period):
    await asyncio.sleep(period)
    bar.copy(liveBar)
    liveBar.reset()
    print('O: ' + str(bar.open) + ' H: ' + str(bar.high) + ' L: ' + str(bar.low) + ' C: ' + str(bar.close))


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
