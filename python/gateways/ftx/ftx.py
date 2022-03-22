import websockets
import asyncio
import requests
from requests import Request, Session
import json
import time
import hmac
from threading import Thread
from lib.interface import OrderBook, Tier, Order, Side, NewOrderSingle, OrderType, InstrumentDetails
from lib.callback_utils import assert_param_counts
from lib.math_utils import to_nearest
from lib.events import OrderEvent, OrderStatus
from lib.identifier import OrderIdGenerator
import logging
from collections import defaultdict
from typing import DefaultDict
from operator import itemgetter


""" Class to maintain readiness check """
class ReadyCheck:
    def __init__(self):
        self.ws_connected = False
        self.snapshot_ready = False
        self.depth_stream_ready = False
        self.orders_stream_ready = False
        self.position_stream_ready = False
        self.circuit_break = False
        self.lost_heartbeat = False

    def streams_ready(self) -> bool:
        """ Return a boolean to indicate streams readiness (True = all ready) or not (False = one or more not ready) """
        return self.snapshot_ready & self.ws_connected & self.depth_stream_ready & self.orders_stream_ready & self.position_stream_ready

    def not_ready(self) -> bool:
        """ Return a boolean to indicate if algo should sleep (True = should not trade) or not (True = ok to trade) """
        return not self.streams_ready() or self.circuit_break or self.lost_heartbeat


URL_WS = 'wss://ftx.com/ws/'
URL_REST = 'https://ftx.com/api'


class FtxManager:
    def __init__(self, symbol: {str}, api_key=None, api_secret=None, name='FTX'):

        self._url = URL_WS
        self._rest_url = URL_REST

        # support string or set of string
        if isinstance(symbol, str):
            self._symbol = {symbol}
        elif isinstance(symbol, set):
            self._symbol = symbol
        else:
            raise ValueError('symbol must either be str or {str}')

        self._loop = asyncio.new_event_loop()
        self._conn = None
        self._ws = None
        self._api_key = api_key
        self._api_secret = api_secret
        self._nonce = 0
        self._signal_reconnect = False

        # static data
        self._instrument_static = {}

        # order book processor, one per symbol
        self._orderbook_processors = {}
        for sym in self._symbol:
            self._orderbook_processors[sym] = OrderBookProcessor(sym)
        self._orderbooks = {}

        # positions
        self._positions = {}

        # open orders
        self._open_orders = {}

        # this is a dedicated thread to run all async concurrent tasks
        self._loop_thread = Thread(target=self._run_async_tasks, daemon=True, name=name)

        # readiness and circuit breaker flag
        self._ready_check = ReadyCheck()

        # callbacks
        self._signal_callback = None
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

    def _has_keys(self) -> bool:
        return self._api_key and self._api_secret

    def _init_cache(self):
        # initialize data with REST APIs
        if self._has_keys():
            self._get_positions()
            self._get_wallet_balances()
            self._get_orders()

        self._ready_check.snapshot_ready = True

    async def _reconnect_ws(self):
        self._ready_check = ReadyCheck()

        # initialize cache
        self._init_cache()

        # ws connect and authenticate
        await self._connect_authenticate_ws()

        # subscribe to all channel
        await self._subscribe_all()

    async def _connect_authenticate_ws(self):
        logging.info('WS - Connect and authenticating')
        self._conn = websockets.connect(self._url)

        try:
            self._ws = await self._conn.__aenter__()

            if self._has_keys():
                # try authenticate
                ts = int(time.time() * 1000)
                signature_payload = f'{ts}websocket_login'.encode()
                signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
                msg_auth = \
                    {
                        "op": "login",
                        "args": {
                            "key": self._api_key,
                            "sign": signature,
                            "time": ts
                        }
                    }
                await self._send_ws(json.dumps(msg_auth))

            # connected
            self._ready_check.ws_connected = True

        except Exception as e:
            logging.error(e)

    async def _send_ws(self, request: str):
        logging.info(request)
        await self._ws.send(request)

    async def _subscribe_all(self):
        if not self._ws:
            logging.error("websocket disconnected, unable to subscribe")
            return

        logging.info('WS - Subscribing to depth')
        for sym in self._symbol:
            request_msg = \
                {
                    "op": "subscribe",
                    "channel": "orderbook",
                    "market": sym
                }
            await self._send_ws(json.dumps(request_msg))

        if self._has_keys():
            logging.info('WS - Subscribing to orders')
            await self._send_ws('{"op": "subscribe", "channel": "orders"}')

            logging.info('WS - Subscribing to fills')
            await self._send_ws('{"op": "subscribe", "channel": "fills"}')
        else:
            logging.info('WS - Not subscribing to orders and fills due to missing keys')
            self._ready_check.orders_stream_ready = True
            self._ready_check.position_stream_ready = True

    def stop(self):
        logging.info("stopping")
        self._loop.stop()
        self._ready_check = None

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
                self._process_websocket_message(response)

            except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                logging.error('connection issue, resetting ws: %s' % e)
                self._ready_check.ws_connected = False
                self._ws = None

            except Exception as e:
                logging.error('encountered issue, resetting ws: %s' % e)
                self._ready_check.ws_connected = False
                self._ws = None

    def _process_websocket_message(self, message: str):
        data = json.loads(message)

        if 'type' in data and data['type'] == 'subscribed':
            logging.info('Received subscription response: ' + message)
            # subscription successful response
            # {"type": "subscribed", "channel": "orderbook", "market": "BTC-PERP"}
            # {"type": "subscribed", "channel": "orders"}
            channel = data['channel']
            if channel == 'orders':
                logging.info('Websocket order stream ready')
                self._ready_check.orders_stream_ready = True
            elif channel == 'fills':
                logging.info('Websocket fill stream ready')
                self._ready_check.position_stream_ready = True

        elif 'channel' in data and data['channel'] == 'orderbook':
            market = data['market']
            processor = self._orderbook_processors.get(market)
            processor.handle(data)
            order_book = processor.get_orderbook()
            self._orderbooks[market] = order_book

            if self._depth_callback:
                self._depth_callback(market, order_book)

            if data['type'] == 'partial':
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

        elif 'channel' in data and data['channel'] == 'fills':
            logging.info(message)
            process_fills(data, self._positions)

        elif 'channel' in data and data['channel'] == 'orders':
            logging.info(message)
            order_event = process_orders_ws(data, self._open_orders)

            if order_event and self._id_generator.match(order_event.client_id):
                if self._execution_callback:
                    # callback if this order event is originated from this connection
                    self._execution_callback(order_event)
            else:
                logging.info("Received execution that is not originated from this connection")

        else:
            logging.info(message)


    """ ----------------------------------- """
    """             REST API                """
    """ ----------------------------------- """

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

    def _get_orders(self):
        logging.info('REST - Requesting open orders')
        data = self._private_request('/orders')
        logging.info(data)
        self._open_orders = process_orders(data)

    def _get_positions(self):
        logging.info('REST - Requesting positions')
        data = self._private_request('/positions')
        logging.info(data)
        self._positions = process_position(data)

    def _get_wallet_balances(self):
        logging.info('REST - Requesting wallet balances')
        data = self._private_request('/wallet/balances')
        logging.info(data)
        balances = process_wallet_balances(data)
        self._positions = {**self._positions, **balances}

    def _private_request(self, method: str) -> object:
        request = Request('GET', URL_REST + method)
        self._set_private_header(request)
        session = Session()
        response = session.send(request.prepare())
        return response.json()

    def _private_request_post(self, method: str, data: dict) -> object:
        request = Request('POST', URL_REST + method, json=data)
        self._set_private_header(request)
        session = Session()
        response = session.send(request.prepare())
        return response.json()

    def _set_private_header(self, request: Request):
        ts = int(time.time() * 1000)
        prepared = request.prepare()

        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body

        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)


    #############################################
    ##               Interface                 ##
    #############################################

    def not_ready(self) -> bool:
        return self._ready_check is not None and self._ready_check.not_ready()

    def get_ticker(self, contract_name: str) -> OrderBook:
        """ To get latest orderbook """
        return self._orderbooks.get(contract_name)

    def get_delta(self, symbol: str) -> float:
        """ To get position from position manager """
        """ return a float, which is # of lots for derivatives, and # of coin for spot """
        if is_spot(symbol):
            symbol = symbol.split('/')[0]

        if symbol in self._positions:
            return self._positions.get(symbol)
        else:
            return float('nan')

    def get_orders(self, contract_name: str) -> []:
        """ To get open orders snapshot from OMS """
        """ Return a list of Order object """
        orders_dict = self._open_orders.get(contract_name)

        if not orders_dict:
            return []
        else:
            return orders_dict.values()

    def place_order(self, nos) -> str:
        """ Place an order. Return client order id if successful """
        client_id = self._id_generator.next()
        instrument_static = self._instrument_static.get(nos.symbol)
        data = get_place_order_message(nos, instrument_static, client_id)
        logging.info('sending order: {}'.format(data))
        response = self._private_request_post('/orders', data)
        logging.info(response)

        # {'success': False, 'error': 'Account does not have enough margin for order.'}
        # {'success': True, 'result': {'id': 78441353101, 'clientId': None, 'market': 'BTC-PERP', 'type': 'limit', 'side': 'buy', 'price': 30000.0, 'size': 0.001, 'status': 'new', 'filledSize': 0.0, 'remainingSize': 0.001, 'reduceOnly': False, 'liquidation': None, 'avgFillPrice': None, 'postOnly': False, 'ioc': False, 'createdAt': '2021-09-11T08:56:17.378995+00:00', 'future': 'BTC-PERP'}}
        if response['success']:
            return client_id
        else:
            return None

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

    def register_signal_callback(self, callback):
        """ a signal callback function takes two arguments: (contract_name:str, data:{}) """
        assert_param_counts(callback, 2)
        self._signal_callback = callback

    def register_depth_callback(self, callback):
        """ a depth callback function takes two argument: (contract_name:str, book: OrderBook) """
        assert_param_counts(callback, 2)
        self._depth_callback = callback

    def register_execution_callback(self, callback):
        """ an execution callback function takes one argument, an order event: (event: OrderEvent) """
        assert_param_counts(callback, 1)
        self._execution_callback = callback


def process_position(message: dict) -> dict:
    #'{"success": "True", "result": [{"future": "BTC-PERP", "size": 0.0001, "side": "buy", "netSize": 0.0001, "longOrderSize": 0.0, "shortOrderSize": 0.0, "cost": 4.7122, "entryPrice": 47122.0, "unrealizedPnl": 0.0, "realizedPnl": 0.0123, "initialMarginRequirement": 1.0, "maintenanceMarginRequirement": 0.03, "openSize": 0.0001, "collateralUsed": 4.7122, "estimatedLiquidationPrice": 0.0}]}'
    if not message['result']:
        return

    store = {}
    for data in message['result']:
        symbol = data['future']
        position = data['netSize']
        store[symbol] = float(position)

    return store


def process_wallet_balances(message: dict) -> dict:
    #{'success': True, 'result': [{'coin': 'ETH', 'total': 0.00099981, 'free': 0.00099981, 'availableWithoutBorrow': 0.00099981, 'usdValue': 3.6293909786081513, 'spotBorrow': 0.0}, {'coin': 'BTC', 'total': 0.00012779, 'free': 0.00012779, 'availableWithoutBorrow': 0.00012779, 'usdValue': 6.154081081476318, 'spotBorrow': 0.0}, {'coin': 'USD', 'total': 90.49253176, 'free': 90.49253176, 'availableWithoutBorrow': 90.49253176, 'usdValue': 90.4925317685, 'spotBorrow': 0.0}, {'coin': 'USDT', 'total': 0.0, 'free': 0.0, 'availableWithoutBorrow': 0.0, 'usdValue': 0.0, 'spotBorrow': 0.0}]}
    if not message['result']:
        return

    store = {}
    for data in message['result']:
        symbol = data['coin']
        position = data['total']
        store[symbol] = float(position)

    return store


def process_fills(message: dict, store: dict):
    #{"channel": "fills", "type": "update", "data": {"id": 3692005673, "market": "BTC-PERP", "future": "BTC-PERP", "baseCurrency": null, "quoteCurrency": null, "type": "order", "side": "sell", "price": 47052.0, "size": 0.0001, "orderId": 77913105521, "time": "2021-09-09T14:10:25.646508+00:00", "tradeId": 1832691741, "feeRate": 0.000665, "fee": 0.003128958, "feeCurrency": "USD", "liquidity": "taker"}}
    if 'channel' in message and message['channel'] == 'fills':
        data = message.get('data')
        symbol = data.get('market')

        if is_spot(symbol):
            symbol = symbol.split('/')[0]

        size = data.get('size')
        sign = (-1 if data['side'] == 'sell' else 1)
        position = float(sign * size)

        if symbol in store:
            store[symbol] = store[symbol] + position
        else:
            store[symbol] = position


def process_orders(message: dict) -> dict:
    # {'success': True, 'result': [{'id': 77934326712, 'clientId': None, 'market': 'BTC-PERP', 'type': 'limit', 'side': 'buy', 'price': 30000.0, 'size': 0.0001, 'status': 'open', 'filledSize': 0.0, 'remainingSize': 0.0001, 'reduceOnly': False, 'liquidation': False, 'avgFillPrice': None, 'postOnly': False, 'ioc': False, 'createdAt': '2021-09-09T15:48:04.320464+00:00', 'future': 'BTC-PERP'}]}
    store = {}

    if not message['result']:
        return store

    for data in message['result']:
        contract_name = data.get('market')
        order_id = str(data.get('id'))
        qty = float(data.get('size'))
        side = Side.Sell if data.get('side') == "sell" else Side.Buy
        timestamp = data.get('createdAt')
        order_type = data.get('type').upper()
        if 'price' in data:
            price = float(data.get('price'))
        else:
            price = None

        order = Order(symbol=contract_name,
                      price=price,
                      side=side,
                      orderID=order_id,
                      leavesQty=qty,
                      timestamp=timestamp,
                      type=order_type)

        if contract_name not in store:
            store[contract_name] = {}

        store[contract_name][order_id] = order

    return store


def process_orders_ws(message: dict, store: dict) -> [OrderEvent]:
    # {"channel": "orders", "type": "update", "data": {"id": 77921137820, "clientId": null, "market": "BTC-PERP", "type": "limit", "side": "buy", "price": 30000.0, "size": 0.0001, "status": "new", "filledSize": 0.0, "remainingSize": 0.0001, "reduceOnly": false, "liquidation": false, "avgFillPrice": null, "postOnly": false, "ioc": false, "createdAt": "2021-09-09T14:47:17.792437+00:00"}}
    if 'channel' in message and message['channel'] == 'orders':
        data = message.get('data')
        contract_name = data.get('market')
        order_id = str(data.get('id'))
        client_id = data.get('clientId')
        qty = float(data.get('size'))

        side = Side.Sell if data.get('side') == "sell" else Side.Buy

        timestamp = data.get('createdAt')
        order_type = data.get('type').upper()
        status = data.get('status')

        order_event = None
        if status == 'new':
            # insert to cache
            if 'price' in data:
                price = float(data.get('price'))
            else:
                price = None

            order = Order(symbol=contract_name,
                          price=price,
                          side=side,
                          orderID=order_id,
                          leavesQty=qty,
                          timestamp=timestamp,
                          type=order_type)

            if contract_name not in store:
                store[contract_name] = {}

            store[contract_name][order_id] = order

            # create event object
            order_event = OrderEvent(contract_name=contract_name,
                                     order_id=order_id,
                                     status=OrderStatus.OPEN,
                                     client_id=client_id)

        elif status == 'closed':
            # remove from the cache
            try:
                del store[contract_name][order_id]
            except KeyError:
                # ok
                pass

            order_status = (OrderStatus.MATCHED if data['filledSize'] > 0 else OrderStatus.CANCELED)

            # create event object
            order_event = OrderEvent(contract_name=contract_name,
                                     order_id=order_id,
                                     status=order_status,
                                     canceled_reason="",
                                     client_id=client_id)

        return order_event


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
                         asks=[Tier(price=p, size=s) for (p, s) in sorted_orderbooks['asks'][:self._depth]],
                         sorted=True)

    def _reset(self) -> None:
        if 'bids' in self._orderbooks:
            del self._orderbooks['bids']

        if 'asks' in self._orderbooks:
            del self._orderbooks['asks']

        self._timestamp = 0

    def ready(self) -> bool:
        return self._timestamp > 0


def get_place_order_message(nos: NewOrderSingle, instrument_static: InstrumentDetails, client_id: str) -> dict:
    """ construct place order request and return a JSON string """

    order_type = None
    price = None
    ioc = False
    if nos.type is OrderType.Market:
        order_type = "market"
    elif nos.type is OrderType.Limit:
        order_type = "limit"
        price = nos.price
    elif nos.type is OrderType.IOC:
        order_type = "limit"
        price = nos.price
        ioc = True
    else:
        raise Exception("Unsupported order type")

    place_order = \
        {
            "market": nos.symbol,
            "side": "buy" if nos.side == Side.Buy else "sell",
            "price": price,
            "type": order_type,
            "size": to_nearest(nos.quantity, instrument_static.quantity_size),
            "ioc": ioc,
            "postOnly": nos.post_only,
            "clientId": client_id
        }

    return place_order


def is_spot(symbol: str) -> bool:
    return '/' in symbol


