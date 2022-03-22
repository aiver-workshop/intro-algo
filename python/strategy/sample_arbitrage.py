import asyncio

from lib.interface import OrderBook
from gateways.ftx.ftx import FtxManager
from gateways.dydx.dydx import DydxManager
from lib.events import OrderEvent
from trading_view import SpreadSignalGraph
import logging
import sys
import time
import os
from dotenv import load_dotenv


class ArbitrageStrategy:
    def __init__(self,
                 reference_symbol: str,
                 target_symbol: str,
                 signal_distance: float,
                 reversal_distance: float,
                 spread_graph: SpreadSignalGraph = None):

        self._reference_symbol = reference_symbol
        self._reference_book = None

        self._target_symbol = target_symbol
        self._target_book = None

        self._last_signal = 0

        # signal is generated when |spread| >= signal_distance
        self._signal_distance = signal_distance

        # signal is reverted back to zero when |spread| <= reversal_distance
        self._reversal_distance = reversal_distance

        # graph
        self._graph = spread_graph

    def on_reference_book(self, contract_name: str, book: OrderBook):
        if not tob_crossed(book):
            self._reference_book = book
            self._on_book_event()

    def on_target_book(self, contract_name: str, book: OrderBook):
        if not tob_crossed(book):
            self._target_book = book
            self._on_book_event()

    def on_reference_execution(self, order_event: OrderEvent):
        logging.info('Reference execution callback: {}'.format(order_event))

    def on_target_execution(self, order_event: OrderEvent):
        logging.info('Reference execution callback: {}'.format(order_event))

    def _on_book_event(self):
        """ assume no crossing for each book, then only only side will cross """
        if self._reference_book and self._target_book:
            _ask_spread = self._reference_book.asks[0].price - self._target_book.bids[0].price
            _bid_spread = self._reference_book.bids[0].price - self._target_book.asks[0].price

            _signal = self._last_signal

            if _ask_spread <= -self._signal_distance:
                _signal = 1     # buy, sell to capture spread
            elif _bid_spread >= self._signal_distance:
                _signal = -1    # sell, buy to capture spread
            elif abs(_bid_spread) <= self._reversal_distance or abs(_ask_spread) <= self._reversal_distance:
                _signal = 0  # exit

            self._on_signal(signal=_signal, a_spread=_ask_spread, b_spread=_bid_spread)

    def _on_signal(self, signal: int, a_spread: float, b_spread: float):
        if self._graph:
            self._graph.add_data(ask_spread=a_spread,
                                 bid_spread=b_spread,
                                 signal=signal,
                                 reference_bid=self._reference_book.bids[0].price,
                                 reference_ask=self._reference_book.asks[0].price,
                                 target_bid=self._target_book.bids[0].price,
                                 target_ask=self._target_book.asks[0].price)

        self._last_signal = signal


def calculate_mid(book: OrderBook) -> float:
    return 0.5 * (book.asks[0].price + book.bids[0].price)


def tob_crossed(book: OrderBook) -> bool:
    return book.asks[0].price <= book.bids[0].price


def start_ftx(contract: str, read_only=True) -> FtxManager:
    if read_only:
        _ftx = FtxManager(symbol={contract})
    else:
        dotenv_path = 'c:/vault/.ftx_keys'
        load_dotenv(dotenv_path=dotenv_path)
        _ftx = FtxManager(symbol={contract}, api_key=os.getenv('API_KEY'), api_secret=os.getenv('API_SECRET'))

    # connect
    _ftx.connect()
    logging.info("FTX started")
    return _ftx


def start_dydx(contract: str, read_only=True) -> DydxManager:
    if read_only:
        _dydx = DydxManager({contract}, web3_http_provider_url='https://mainnet.infura.io/v3/9a7bac104fd14b5e936862563224f8be')
    else:
        dotenv_path = 'c:/vault/.dydx_keys'
        load_dotenv(dotenv_path=dotenv_path)
        _dydx = DydxManager({contract},
                            os.getenv('ETHEREUM_ADDRESS'),
                            os.getenv('L'),
                            os.getenv('S'),
                            os.getenv('K'),
                            os.getenv('P'),
                            web3_http_provider_url='https://mainnet.infura.io/v3/9a7bac104fd14b5e936862563224f8be')

    # connect
    _dydx.connect()
    logging.info("DYDX started")
    return _dydx


async def render(spread_graph: SpreadSignalGraph):
    graph.render()
    await asyncio.sleep(0.1)


if __name__ == '__main__':
    # logging stuff
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    handler.setFormatter(logFormatter)
    root.addHandler(handler)

    # graph
    graph = SpreadSignalGraph(300, spread_abs_max=2)

    dydx_symbol = 'ETH-USD'
    ftx_symbol = 'ETH-PERP'

    # trading strategy
    strategy = ArbitrageStrategy(reference_symbol=ftx_symbol,
                                 target_symbol=dydx_symbol,
                                 signal_distance=1,
                                 reversal_distance=0.1,
                                 spread_graph=graph)

    dydx = start_dydx(dydx_symbol, read_only=True)
    dydx.register_depth_callback(strategy.on_target_book)
    dydx.register_execution_callback(strategy.on_target_execution)

    ftx = start_ftx(ftx_symbol, read_only=True)
    ftx.register_depth_callback(strategy.on_reference_book)
    ftx.register_execution_callback(strategy.on_reference_execution)

    loop = asyncio.new_event_loop()

    # loop till ready
    while True:
        if dydx.not_ready():
            logging.info("Dydx not ready to trade")
            time.sleep(1)
        if ftx.not_ready():
            logging.info("Ftx not ready to trade")
            time.sleep(1)
        else:
            asyncio.run(render(graph))