
import websockets
import asyncio
import requests
import json
from threading import Thread
from lib.interface import OrderBook, Tier, InstrumentDetails
from lib.callback_utils import assert_param_counts
import logging
import sys
import time
from collections import defaultdict
from typing import DefaultDict
from operator import itemgetter


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
        self._instrument_static = {}

        # create an empty dictionary to store latest order books
        self._order_books = {}

        # create a new async event loop to run async tasks
        self._loop = asyncio.new_event_loop()

        # create a dedicated thread to run the event loop
        self._loop_thread = Thread(target=self._run_async_tasks, daemon=True, name=name)

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

    # make a REST call to /markets and store the price and size increments for all given symbols in the response
    def _get_static(self):
        logging.info('REST - Requesting static data')
        resp = requests.get(URL_REST + '/markets')
        message = resp.json()
        for data in message['result']:
            contract_name = data.get('name')
            instrument_static = InstrumentDetails(contract_name=contract_name,
                                                  tick_size=float(data.get('priceIncrement')),
                                                  quantity_size=float(data.get('sizeIncrement')))
            self._instrument_static[contract_name] = instrument_static

    # reconnect websocket session to FTX
    async def _reconnect_ws(self):
        # ws connect
        await self._connect_ws()

        # subscribe to channels
        await self._subscribe_all()

    async def _connect_ws(self):
        logging.info('WebSocket - Connecting')
        self._conn = websockets.connect(URL_WS)

        try:
            # connecting
            self._ws = await self._conn.__aenter__()

            # connected
            logging.info('WebSocket - connection established')

        except Exception as e:
            logging.error(e)

    async def _send_ws(self, request: str):
        logging.info(request)
        await self._ws.send(request)

    # subscribe to orderbook channel
    async def _subscribe_all(self):
        if not self._ws:
            logging.error("websocket disconnected, unable to subscribe")
            return

        logging.info('WS - Subscribing to order book')
        for sym in self._symbol:
            request_msg = \
                {
                    "op": "subscribe",
                    "channel": "orderbook",
                    "market": sym
                }
            await self._send_ws(json.dumps(request_msg))

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

    # parse and process incoming websocket message
    def _process_websocket_message(self, message: str):
        data = json.loads(message)

        if 'type' in data and data['type'] == 'subscribed':
            logging.info('Received subscription response: ' + message)

        elif 'channel' in data and data['channel'] == 'orderbook':
            market = data['market']
            processor = self._book_processors.get(market)
            processor.handle(data)
            order_book = processor.get_orderbook()
            self._order_books[market] = order_book

            if self._book_callback:
                self._book_callback(market, order_book)
        else:
            logging.info(message)

    """ ----------------------------------- """
    """             Interface               """
    """ ----------------------------------- """

    # To get latest order book
    def get_ticker(self, contract_name: str) -> OrderBook:
        return self._order_books.get(contract_name)

    # To get tick size
    def get_tick_size(self, contract_name: str):
        if contract_name in self._instrument_static:
            instrument_static = self._instrument_static.get(contract_name)
            return instrument_static.tick_size
        else:
            return None

    # To get quantity size
    def get_quantity_size(self, contract_name: str):
        if contract_name in self._instrument_static:
            instrument_static = self._instrument_static.get(contract_name)
            return instrument_static.quantity_size
        else:
            return 0

    def register_depth_callback(self, callback):
        """ a depth callback function takes two argument: (contract_name:str, book: OrderBook) """
        assert_param_counts(callback, 2)
        self._book_callback = callback


# A helper class to process order book message
class OrderBookProcessor:
    def __init__(self, symbol: str, depth=5):
        self._symbol = symbol
        self._depth = depth

        # a map that contain bids and asks sides
        self._orderbooks: DefaultDict[str, DefaultDict[float, float]] = defaultdict(lambda: defaultdict(float))
        self._timestamp = 0

    def handle(self, message: str):
        market = message['market']
        if market != self._symbol:
            raise ValueError("Received message for market {} but this processor is for {}".format(market, self._symbol))

        data = message['data']

        if data['action'] == 'partial':
            self._reset()

        for side in {'bids', 'asks'}:
            book = self._orderbooks[side]
            for price, size in data[side]:
                if size:
                    book[price] = size
                else:
                    del book[price]

        self._timestamp = data['time']

    def get_orderbook(self) -> OrderBook:
        if self._timestamp == 0:
            return 0

        sorted_orderbooks = {side: sorted(
            [(price, quantity) for price, quantity in list(self._orderbooks[side].items())
             if quantity],
            key=itemgetter(0),
            reverse=(True if side == 'bids' else False)
        )
        for side in {'bids', 'asks'}}

        return OrderBook(timestamp=self._timestamp,
                         bids=[Tier(price=p, size=s) for (p, s) in sorted_orderbooks['bids'][:self._depth]],
                         asks=[Tier(price=p, size=s) for (p, s) in sorted_orderbooks['asks'][:self._depth]])

    def _reset(self) -> None:
        if 'bids' in self._orderbooks:
            del self._orderbooks['bids']

        if 'asks' in self._orderbooks:
            del self._orderbooks['asks']

        self._timestamp = 0


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
