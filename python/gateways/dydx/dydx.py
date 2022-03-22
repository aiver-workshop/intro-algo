#
# The following dependencies are required:
#   https://pypi.org/project/dydx-v3-python/ - pip install dydx-v3-python
#   https://pypi.org/project/web3/ - pip install web3
#
# Reference: https://github.com/dydxprotocol/dydx-v3-python
#

from dydx3 import Client
from dydx3.helpers.request_helpers import generate_now_iso
from dydx3.constants import API_HOST_MAINNET
from dydx3.constants import NETWORK_ID_MAINNET
from dydx3.constants import WS_HOST_MAINNET
from dydx3.constants import POSITION_STATUS_OPEN
from dydx3.constants import ORDER_SIDE_BUY, ORDER_SIDE_SELL, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTT, TIME_IN_FORCE_IOC
from web3 import Web3
from lib.events import OrderEvent, OrderStatus
from lib.callback_utils import assert_param_counts
import websockets
import asyncio
import time
import json
from threading import Thread
from lib.interface import OrderBook, Tier, Order, Side, NewOrderSingle, OrderType, InstrumentDetails
import logging
from lib.math_utils import to_nearest
from collections import defaultdict
from typing import DefaultDict
from operator import itemgetter
from datetime import datetime, timedelta
from lib.identifier import OrderIdGenerator


class ReadyCheck:
    """ Class to maintain readiness check """
    def __init__(self):
        self.ws_connected = False
        self.snapshot_ready = False
        self.depth_stream_ready = False
        self.account_stream_ready = False
        self.wrong_ioc_count = 0

    def streams_ready(self) -> bool:
        """ Return a boolean to indicate streams readiness (True = all ready) or not (False = one or more not ready) """
        return self.snapshot_ready & self.ws_connected & self.depth_stream_ready & self.account_stream_ready

    def not_ready(self) -> bool:
        """ Return a boolean to indicate if algo should sleep (True = should not trade) or not (True = ok to trade) """
        return not self.streams_ready()


class DydxManager:
    def __init__(self,
                 symbol: {str},
                 web3_http_provider_url: str,
                 ethereum_address=None,
                 stark_private_key=None,
                 api_s=None,
                 api_k=None,
                 api_p=None,
                 name='dydx',
                 depth_levels=5):

        # support string or set of string
        if isinstance(symbol, str):
            self._symbol = {symbol}
        elif isinstance(symbol, set):
            self._symbol = symbol
        else:
            raise ValueError('symbol must either be str or {str}')

        self._web3_http_provider_url = web3_http_provider_url

        # dydx client interface
        if ethereum_address and stark_private_key and api_s and api_k and api_p:
            self._has_keys = True
            self._client = Client(
                network_id=NETWORK_ID_MAINNET,
                host=API_HOST_MAINNET,
                default_ethereum_address=ethereum_address,
                api_key_credentials={'secret': api_s, 'key': api_k, 'passphrase': api_p},
                web3=Web3(Web3.HTTPProvider(web3_http_provider_url)),
                stark_private_key=stark_private_key
            )
        else:
            self._has_keys = False
            self._client = Client(
                network_id=NETWORK_ID_MAINNET,
                host=API_HOST_MAINNET,
                web3=Web3(Web3.HTTPProvider(web3_http_provider_url)),
            )

        self._client_public = self._client.public
        self._client_private = None

        # websocket connection
        self._ws_url = WS_HOST_MAINNET
        self._conn = None
        self._ws = None

        # to run async io
        self._loop = asyncio.new_event_loop()

        # to store instrument static data
        self._instrument_static = {}

        # positions
        self._positions = {}

        # open orders
        self._open_orders = {}

        # StarkWare-specific positionId. This is required for signing and can be fetched from the account endpoints.
        self._position_id = None

        # to signal reconnect
        self._signal_reconnect = False

        # this is a dedicated thread to run all async concurrent tasks
        self._loop_thread = Thread(target=self._run_async_tasks, daemon=True, name=name)

        # readiness and circuit breaker flag
        self._ready_check = ReadyCheck()

        # order book processor, one per symbol
        self._orderbook_processors = {}
        self._orderbooks = {}
        for sym in self._symbol:
            self._orderbook_processors[sym] = OrderBookProcessor(sym, depth=depth_levels)
            self._orderbooks[sym] = None

        # to measure price cross duration
        self._price_cross_timer = None

        # callbacks
        self._depth_callback = None
        self._execution_callback = None

        # client order id generator
        self._id_generator = OrderIdGenerator(prefix=name)

    def connect(self):
        logging.info('Initializing connection')

        # get instrument static data
        self._get_static()

        self._loop.run_until_complete(self._reconnect_ws())

        logging.info("starting event loop thread")
        self._loop_thread.start()

    def reconnect(self):
        """ A signal to reconnect """
        self._signal_reconnect = True

    def _init_cache(self):
        # initialize data with REST APIs
        if self._has_keys:
            self._get_account()
            self._get_positions()
            self._get_orders()
        else:
            logging.info('Not getting account, position and order snapshot due to missing keys')

        self._ready_check.snapshot_ready = True

    async def _reconnect_ws(self):
        self._ready_check = ReadyCheck()

        # get the private module
        if self._has_keys:
            self._client_private = self._client.private

        # initialize cache
        self._init_cache()

        # ws connect and authenticate
        await self._connect_authenticate_ws()

        # subscribe to all channel
        await self._subscribe_all()

        logging.info('WS - Connected')
        self._ready_check.ws_connected = True

    async def _connect_authenticate_ws(self):
        logging.info('WS - Connecting')
        self._conn = websockets.connect(self._ws_url)
        try:
            self._ws = await self._conn.__aenter__()
        except Exception as e:
            logging.error(e)

    async def _subscribe_all(self):
        if not self._ws:
            logging.error("websocket disconnected, unable to subscribe")
            return

        if self._has_keys:
            logging.info('WS - Subscribing to account channel')
            now_iso_string = generate_now_iso()
            signature = self._client_private.sign(
                request_path='/ws/accounts',
                method='GET',
                iso_timestamp=now_iso_string,
                data={},
            )
            req = {
                'type': 'subscribe',
                'channel': 'v3_accounts',
                'accountNumber': '0',
                'apiKey': self._client.api_key_credentials['key'],
                'passphrase': self._client.api_key_credentials['passphrase'],
                'timestamp': now_iso_string,
                'signature': signature,
            }
            await self._send_ws(json.dumps(req))
        else:
            logging.info('WS - Not subscribing to account channel due to missing keys')
            self._ready_check.account_stream_ready = True

        logging.info('WS - Subscribing to order books')
        for sym in self._symbol:
            req = {
                'type': 'subscribe',
                'channel': 'v3_orderbook',
                'id': sym,
                'includeOffsets': True
            }
            await self._send_ws(json.dumps(req))

    async def _send_ws(self, request: str):
        logging.info(request)
        await self._ws.send(request)

    def stop(self):
        logging.info("stopping")
        self._loop.stop()
        self._ready_check = None

    def _run_async_tasks(self):
        """ Run the following tasks concurrently in the current thread """
        self._loop.create_task(self._listen_forever())
        self._loop.run_forever()

    async def _listen_forever(self):
        """ This is the main callback that process incoming WebSocket messages from server """

        logging.info("start listening on incoming messages")
        while True:
            if not self._ws:
                logging.error("websocket disconnected, reconnecting")
                self._ready_check.ws_connected = False
                await self._reconnect_ws()

            if self._signal_reconnect:
                logging.info("received reconnect signal")
                self._ws = None
                self._signal_reconnect = False
                continue

            # wait for incoming message
            try:
                # wait for incoming message, with a maximum wait time
                response = await asyncio.wait_for(self._ws.recv(), timeout=10)

                # process the message
                if response == 'ping':
                    logging.info("Received ping")
                    await self._send_ws('pong')
                else:
                    self._process_websocket_message(response)

            except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                logging.error('connection issue, resetting ws: %s' % e)
                logging.error('last response: %s' % response)
                self._ready_check.ws_connected = False
                self._ws = None

            except Exception as e:
                logging.error('encountered issue, resetting ws: %s' % e)
                logging.error('last response: %s' % response)
                self._ready_check.ws_connected = False
                self._ws = None

    def _process_websocket_message(self, message: str):
        # convert JSON string to data dictionary
        data = json.loads(message)

        data_type = data['type']

        if 'connected' == data_type:
            logging.info(message)
            return

        if 'error' == data_type:
            # {"type":"error","message":"Invalid message: could not parse","connection_id":"decf6ea9-5531-4a3a-aae7-f1580bfbd003","message_id":416}
            logging.error('encountered error message: %s' % message)
            return

        channel = data['channel']

        if 'v3_accounts' == channel:
            logging.info(message)
            contents = data['contents']

            if 'orders' in contents and contents['orders']:
                order_events = process_orders_ws(contents['orders'], self._open_orders)

                for order_event in order_events:
                    if order_event and self._id_generator.match(order_event.client_id):
                        if self._execution_callback:
                            # callback if this order event is originated from this connection
                            self._execution_callback(order_event)
                    else:
                        logging.info("Received execution that is not originated from this connection")

            if 'positions' in contents and contents['positions']:
                process_positions_ws(contents['positions'], self._positions)

            if 'fills' in contents and contents['fills']:
                pass

            if not self._ready_check.account_stream_ready:
                logging.info('Websocket account stream ready')
                self._ready_check.account_stream_ready = True

        elif 'v3_orderbook' == channel:
            # logging.info('book -> %s' % message)

            market = data['id']
            processor = self._orderbook_processors.get(market)
            processor.handle(data)
            updated_order_book = processor.get_orderbook()
            self._orderbooks[market] = updated_order_book

            if data_type == 'subscribed':
                """ we have received initial snapshot """
                logging.info('Websocket depth snapshot: {}'.format(message))
                # check if we have snapshot for all symbols
                all_depth_ready = True
                for symbol, processor in self._orderbook_processors.items():
                    if not processor.ready():
                        all_depth_ready = False
                        break

                if all_depth_ready:
                    logging.info('Websocket depth stream ready')
                    self._ready_check.depth_stream_ready = True
                else:
                    logging.info('Websocket depth stream not ready yet')

            if self._depth_callback:
                self._depth_callback(market, updated_order_book)

    """ ----------------------------------- """
    """             REST API                """
    """ ----------------------------------- """

    def _get_static(self):
        logging.info('REST - Requesting static data')
        response = self._client_public.get_markets()
        markets = response.data.get('markets')
        for symbol, static_data in markets.items():
            instrument_static = InstrumentDetails(contract_name=symbol,
                                                  tick_size=float(static_data.get('tickSize')),
                                                  quantity_size=float(static_data.get('stepSize')))
            self._instrument_static[symbol] = instrument_static

    def _get_account(self):
        logging.info('REST - Requesting account info')
        response = self._client_private.get_account()
        data = response.data
        self._position_id = data['account']['positionId']

    def _get_orders(self):
        logging.info('REST - Requesting open orders')
        response = self._client_private.get_orders()
        all_orders = response.data
        self._open_orders = process_orders(all_orders)

    def _get_positions(self):
        logging.info('REST - Requesting positions')
        response = self._client_private.get_positions(status=POSITION_STATUS_OPEN)
        all_positions = response.data
        logging.info(all_positions)
        self._positions = process_positions(all_positions)


    #############################################
    ##               Interface                 ##
    #############################################

    def not_ready(self) -> bool:
        return self._ready_check is not None and self._ready_check.not_ready()

    def get_ticker(self, contract_name: str) -> OrderBook:
        """ To get latest orderbook """
        return self._orderbooks.get(contract_name)

    def register_depth_callback(self, callback):
        """ a depth callback function takes two argument: (contract_name:str, book: OrderBook) """
        assert_param_counts(callback, 2)
        self._depth_callback = callback

    def register_execution_callback(self, callback):
        """ an execution callback function takes one argument, an order event: (event: OrderEvent) """
        assert_param_counts(callback, 1)
        self._execution_callback = callback

    def get_delta(self, contract_name: str) -> float:
        """ To get position from position manager """
        if contract_name in self._positions:
            return self._positions.get(contract_name)
        else:
            return 0

    def get_orders(self, contract_name: str) -> []:
        """ To get open orders snapshot from OMS """
        """ Return a list of Order object """
        orders_dict = self._open_orders.get(contract_name)

        if not orders_dict:
            return []
        else:
            return orders_dict.values()

    def place_order(self, nos: NewOrderSingle) -> str:
        """ Place an order. Return client order id """
        client_id = self._id_generator.next()
        order_type = None
        time_in_force = None
        expiration_epoch_seconds = None

        if nos.type is OrderType.Limit:
            order_type = ORDER_TYPE_LIMIT
            time_in_force = TIME_IN_FORCE_GTT
            # to expire one hour from now
            expiration_epoch = datetime.utcnow() + timedelta(hours=1)

        elif nos.type is OrderType.IOC:
            order_type = ORDER_TYPE_LIMIT
            time_in_force = TIME_IN_FORCE_IOC
            # minimum expiration time is 1 minute
            expiration_epoch = datetime.utcnow() + timedelta(minutes=5)
        else:
            raise Exception("Unsupported order type")

        size = str(to_nearest(nos.quantity, self._instrument_static.get(nos.symbol).qty_increment))
        price = str(nos.price)
        side = ORDER_SIDE_BUY if nos.side == Side.Buy else ORDER_SIDE_SELL

        expiration_iso = expiration_epoch.strftime('%Y-%m-%dT%H:%M:%S.%f',)[:-3] + 'Z'

        placed_order = self._client_private.create_order(
            position_id=self._position_id,
            market=nos.symbol,
            side=side,
            order_type=order_type,
            post_only=nos.post_only,
            size=size,
            price=price,
            limit_fee='0.001',
            expiration=expiration_iso,
            time_in_force=time_in_force,
            client_id=client_id
        )
        logging.info(placed_order)

        return client_id

    def get_tick_size(self, contract_name: str):
        if contract_name in self._instrument_static:
            instrument_static = self._instrument_static.get(contract_name)
            return instrument_static.tick_size
        else:
            return None

    def get_quantity_size(self, contract_name: str):
        if contract_name in self._instrument_static:
            instrument_static = self._instrument_static.get(contract_name)
            return instrument_static.qty_increment
        else:
            return 0


class OrderBookProcessor:
    """
        The price updates are not guaranteed to be sent in order. So it is possible to receive an older price update
        later. For this reason, the offset is included in the message, to help order.
        The offset increases monotonically, and increasing values of offsets indicate more recent values.

        To keep a valid order book, you should store the offset for each price level independently.
        A given price level should be updated if and only if an update for the price level is received with a
        higher offset than what you have stored. To get a per-price level offset in the initial response,
        you can set includeOffsets to true when subscribing.
    """
    def __init__(self, symbol: str, depth=5):
        self._symbol = symbol
        self._depth = depth

        # a map that contain bids and asks sides, then each side is a map of price -> (offset, quantity)
        self._orderbooks: DefaultDict[str, DefaultDict[float, PriceLevel]] = defaultdict(lambda: defaultdict(PriceLevel))
        self._timestamp = 0

        # latest order book
        self._clean_order_book = None

    def handle(self, message: dict) -> {}:
        """ Handle update, and return a signal (a map) if there is a cross """
        market = message['id']
        if market != self._symbol:
            raise ValueError("Received message for market {} but this processor is for {}".format(market, self._symbol))

        data = message['contents']

        signal = {}
        if message['type'] == 'subscribed':
            """ The initial response will contain the state of the order book """
            self._reset()
            self._handle_snapshot(data)
        else:
            signal = self._handle_update(data)

        self._timestamp = time.time_ns()

        return signal

    def _handle_snapshot(self, data):
        for side in {'bids', 'asks'}:
            book = self._orderbooks[side]
            for update_layer in data[side]:
                offset = int(update_layer['offset'])
                price = float(update_layer['price'])
                size = float(update_layer['size'])
                if size:
                    book[price] = PriceLevel(price, offset, size)

    def _handle_update(self, data):
        """ Handle update and return a signal if crossed (and remove the opposite side of update that crossed)
            A signal is a map that shows current TOB, and the update side that has caused a crossed
            {'wrong': (3809.7, 3809.6), 'wrong_side': 'bid'}
        """

        # "contents":{"offset":"1408380048","bids":[],"asks":[["48644","0.2056"],["48645","11.7164"]]}}
        update_offset = int(data['offset'])

        # apply update
        for side in {'bids', 'asks'}:
            book = self._orderbooks[side]
            for price, size in data[side]:
                price = float(price)
                size = float(size)
                if price not in book:
                    # new
                    book[price] = PriceLevel(price, update_offset, size)
                else:
                    previous_offset = book[price].get_offset()
                    if update_offset > previous_offset:
                        book[price].update(update_offset, size)
                    else:
                        logging.info(
                            "Skipping price update -> side={}, existing offset={}, update offset={}, price={}, size={}".format(
                                side, previous_offset, update_offset, price, size))
                        continue

    def get_best_bid(self):
        if self._orderbooks['bids']:
            return max(price for price, level in list(self._orderbooks['bids'].items()) if level.get_size())
        return None

    def get_sorted_bids(self):
        sorted_bids = sorted(
            [(price, level) for price, level in list(self._orderbooks['bids'].items()) if level.get_size()],
            key=itemgetter(0),
            reverse=True)
        return [p for (p, s) in sorted_bids]

    def get_sorted_asks(self):
        sorted_asks = sorted(
            [(price, level) for price, level in list(self._orderbooks['asks'].items()) if level.get_size()],
            key=itemgetter(0),
            reverse=False)
        return [p for (p, s) in sorted_asks]

    def get_best_ask(self):
        if self._orderbooks['asks']:
            return min(price for price, level in list(self._orderbooks['asks'].items()) if level.get_size())
        return None

    def get_orderbook(self) -> OrderBook:
        if self._timestamp == 0:
            return 0

        sorted_orderbooks = {side: sorted(
            [(price, level) for price, level in list(self._orderbooks[side].items()) if level.get_size()],
            key=itemgetter(0),
            reverse=(True if side == 'bids' else False)
        )
        for side in {'bids', 'asks'}}

        return OrderBook(timestamp=self._timestamp,
                         bids=[Tier(price=p, size=s.get_size(), quote_id=s.get_offset()) for (p, s) in sorted_orderbooks['bids'][:self._depth]],
                         asks=[Tier(price=p, size=s.get_size(), quote_id=s.get_offset()) for (p, s) in sorted_orderbooks['asks'][:self._depth]])

    def _reset(self) -> None:
        if 'bids' in self._orderbooks:
            del self._orderbooks['bids']

        if 'asks' in self._orderbooks:
            del self._orderbooks['asks']

        self._timestamp = 0

    def ready(self) -> bool:
        return self._timestamp > 0


class PriceLevel:
    def __init__(self, price: float, offset: int, size: float):
        self._price = price
        self._offset = offset
        self._size = size

    def update(self, offset, size):
        self._offset = offset
        self._size = size

    def zero(self, offset):
        self._offset = offset
        self._size = 0

    def get_size(self):
        return self._size

    def get_offset(self):
        return self._offset


def process_orders(message: dict) -> dict:
    # {"orders": [{"id": "296b2791d908f6867ce6555630d33656a284d48192dbb20fdab57db92aed9f8", "clientId": "4785304725173323", "accountId": "d82d13a7-473d-59c7-bcfc-031ed100d62b", "market": "BTC-USD", "side": "BUY", "price": "30000", "triggerPrice": None, "trailingPercent": None, "size": "0.001", "remainingSize": "0.001", "type": "LIMIT", "createdAt": "2021-09-18T14:06:25.111Z", "unfillableAt": None, "expiresAt": "2021-10-16T14:06:21.498Z", "status": "OPEN", "timeInForce": "GTT", "postOnly": False, "cancelReason": None}]}
    store = {}

    if not message['orders']:
        return store

    for data in message['orders']:
        status = data.get('status')
        if 'OPEN' == status:
            order = parse_order(data)

            if order.symbol not in store:
                store[order.symbol] = {}

            store[order.symbol][order.order_id] = order

    return store


def parse_order(data: dict) -> Order:
    contract_name = data.get('market')
    order_id = str(data.get('id'))
    qty = float(data.get('remainingSize'))
    side = Side.Sell if data.get('side') == "SELL" else Side.Buy
    timestamp = data.get('createdAt')
    order_type = data.get('type').upper()
    if 'price' in data:
        price = float(data.get('price'))
    else:
        price = None

    order = Order(symbol=contract_name,
                  price=price,
                  side=side,
                  order_id=order_id,
                  leaves_qty=qty,
                  timestamp=timestamp,
                  order_type=order_type)

    return order


def process_orders_ws(orders: dict, store: dict) -> [OrderEvent]:
    # "orders":[{"id":"296b2791d908f6867ce6555630d33656a284d48192dbb20fdab57db92aed9f8","clientId":"4785304725173323","market":"BTC-USD","accountId":"d82d13a7-473d-59c7-bcfc-031ed100d62b","side":"BUY","size":"0.001","remainingSize":"0.001","limitFee":"0.001","price":"30000","triggerPrice":null,"trailingPercent":null,"type":"LIMIT","status":"CANCELED","signature":"0529d804882c5db7fbfb1884d19d8641d67f793d7ffb5eb9627f961042dd76a3035ff8bd78d0f0c16368c83649e8715c38dd3852f8eff854cc67ce701ffbc270","timeInForce":"GTT","postOnly":false,"cancelReason":"USER_CANCELED","expiresAt":"2021-10-16T14:06:21.498Z","unfillableAt":null,"updatedAt":"2021-09-18T14:06:25.111Z","createdAt":"2021-09-18T14:06:25.111Z"}]

    if not orders:
        return

    order_events = []
    for data in orders:
        # PENDING, OPEN, FILLED, CANCELED, UNTRIGGERED
        status = data.get('status')
        client_id = data.get('clientId')
        order = parse_order(data)

        if 'OPEN' == status:
            # insert to store
            if order.symbol not in store:
                store[order.symbol] = {}

            store[order.symbol][order.order_id] = order

            order_events.append(OrderEvent(contract_name=order.symbol, order_id=order.order_id, status=OrderStatus.OPEN, client_id=client_id))

        elif 'FILLED' == status:
            # remove from store
            try:
                del store[order.symbol][order.order_id]
            except KeyError:
                # ok
                pass
            order_events.append(OrderEvent(contract_name=order.symbol, order_id=order.order_id, status=OrderStatus.MATCHED, client_id=client_id))

        elif 'CANCELED' == status:
            # remove from store
            try:
                del store[order.symbol][order.order_id]
            except KeyError:
                # ok
                pass
            cancel_reason = data.get('cancelReason')
            order_events.append(OrderEvent(contract_name=order.symbol, order_id=order.order_id, status=OrderStatus.CANCELED, canceled_reason=cancel_reason, client_id=client_id))

    return order_events


def process_positions(message: dict) -> dict:
    # {"positions": [{"market": "BTC-USD", "status": "OPEN", "side": "LONG", "size": "0.001", "maxSize": "0.001", "entryPrice": "48538.000000", "exitPrice": "0.000000", "unrealizedPnl": "0.003730", "realizedPnl": "0.000000", "createdAt": "2021-09-18T15:37:50.407Z", "closedAt": null, "sumOpen": "0.001", "sumClose": "0", "netFunding": "0"}]}
    if not message['positions']:
        return {}

    store = {}
    for data in message['positions']:
        if 'OPEN' == data['status']:
            symbol = data['market']
            position = data['size']
            store[symbol] = float(position)

    return store


def process_positions_ws(positions: dict, store: dict):
    if not positions:
        return

    for data in positions:
        symbol = data['market']
        position = data['size']
        store[symbol] = float(position)
