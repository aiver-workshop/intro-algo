"""
Build a FTX gateway to receive market data.

To start, first take a look at the main() to see how we will use the FtxManager object. The main requirements are:
    1. connect to FTX exchange
    2. print static data for BTC perpetual future
    3. print order book data once per second

"""

import websockets
import asyncio
from lib.interface import OrderBook, Tier, InstrumentDetails
from lib.callback_utils import assert_param_counts
import logging
import sys
import time


URL_WS = 'wss://ftx.com/ws/'
URL_REST = 'https://ftx.com/api'


class FtxManager:
    def __init__(self, symbol: {str}, name='FTX'):

        # support string or set of string
        if isinstance(symbol, str):
            self._symbol = {symbol}
        elif isinstance(symbol, set):
            self._symbol = symbol
        else:
            raise ValueError('symbol must either be str or {str}')

        # web socket connection
        self._conn = None
        self._ws = None

        # create an empty dictionary to store static data
        self._instrument_static: {str, InstrumentDetails} = {}

        # TODO create an empty dictionary to store latest order books

        # TODO create a new async event loop to run async tasks

        # TODO create a dedicated thread to run the method _run_async_tasks()

        # order book processor, one per symbol
        self._book_processors = {}
        for sym in self._symbol:
            self._book_processors[sym] = OrderBookProcessor(sym)

        # order book callback
        self._book_callback = None

    # start connection to FTX
    def connect(self):
        logging.info('Initializing connection')

        # get instrument static data
        self._get_static()

        self._loop.run_until_complete(self._reconnect_ws())

        logging.info("starting event loop thread")
        self._loop_thread.start()

    # TODO make a REST call to /markets and store the price and size increments for all given symbols in the response
    def _get_static(self):
        logging.info('REST - Requesting static data')

    # reconnect websocket session to FTX
    async def _reconnect_ws(self):
        # ws connect
        await self._connect_ws()

        # subscribe to channels
        await self._subscribe_all()

    # establish web socket connection
    async def _connect_ws(self):
        logging.info('WebSocket - Connecting')
        self._conn = websockets.connect(self._url)

        try:
            # connecting
            self._ws = await self._conn.__aenter__()

            # connected
            logging.info('WebSocket - connection established')

        except Exception as e:
            logging.error(e)

    # TODO subscribe to orderbook channel
    async def _subscribe_all(self):
        if not self._ws:
            logging.error("websocket disconnected, unable to subscribe")
            return

        logging.info('WS - Subscribing to order book')
        # TODO for each symbol, send a subscription message

    def _run_async_tasks(self):
        """ Run the following tasks concurrently in the current thread """
        self._loop.create_task(self._listen_forever())
        self._loop.create_task(self._keep_alive_websocket())
        self._loop.run_forever()

    async def _keep_alive_websocket(self):
        while True:
            await asyncio.sleep(15)
            logging.info("Sending ping to WebSocket server")
            await self._ws.send('{"op": "ping"}')

    async def _listen_forever(self):
        """ This is the main callback that process incoming WebSocket messages from server """

        logging.info("start listening on incoming messages")
        while True:
            if not self._ws:
                logging.error("websocket disconnected, reconnecting")
                await self._reconnect_ws()

            # wait for incoming message
            try:
                # wait for incoming message, with a maximum wait time
                response = await asyncio.wait_for(self._ws.recv(), timeout=10)

                # process the message
                self._process_websocket_message(response)

            except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                logging.error('connection issue, resetting ws: %s' % e)
                self._ws = None

            except Exception as e:
                logging.error('encountered issue, resetting ws: %s' % e)
                self._ws = None

    # TODO parse and process incoming websocket message
    def _process_websocket_message(self, message: str):
        logging.info(message)

    """ ----------------------------------- """
    """             Interface               """
    """ ----------------------------------- """

    # TODO To get latest order book
    def get_ticker(self, contract_name: str) -> OrderBook:
        pass

    # TODO To get tick size
    def get_tick_size(self, contract_name: str):
        pass

    # TODO To get quantity size
    def get_quantity_size(self, contract_name: str):
        pass

    def register_depth_callback(self, callback):
        """ a depth callback function takes two argument: (contract_name:str, book: OrderBook) """
        assert_param_counts(callback, 2)
        self._book_callback = callback


# A helper class to process order book message
class OrderBookProcessor:
    # TODO
    def __init__(self, symbol: str, depth=5):
        pass

    # TODO
    def handle(self, message: str):
        pass

    # TODO
    def get_orderbook(self) -> OrderBook:
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

    # connect to FTX
    logging.info("main program starts")
    contract = 'BTC-PERP'
    ftx = FtxManager(contract)
    ftx.connect()

    # print tick and quantity size
    logging.info('Contract[{}]: tick size = {}, quantity size = {}'.format(
        contract, ftx.get_tick_size(contract), ftx.get_quantity_size(contract)))

    # print order book once a second
    while True:
        time.sleep(1)
        logging.info('Order book: %s' % ftx.get_ticker(contract))
