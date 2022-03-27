"""
We will learn how to process market data messages from orderbook channel to create our local snapshot of the book.

As documented per the following API link, there are two actions to take note:
    1. action = partial (initial snapshot)
    2. action = update (incremental change)

https://docs.ftx.com/#public-channels

"""
import json
from lib.interface import OrderBook, Tier


# TODO from previous exercise of 8_async_websockets_ans, get the first and subsequent partial and update messages
message_partial = ''

message_update = ''


# TODO Create a helper class to process order book messages
class OrderBookProcessor:
    # TODO
    def __init__(self, symbol: str, depth=5):
        pass

    # TODO process the messages and store the prices in two maps (bids and asks)
    def handle(self, message: {}):
        pass

    # TODO sort the maps and return an orderbook object
    def get_orderbook(self) -> OrderBook:
        pass


# A driver class to demonstrate the usage of the order book processor
if __name__ == '__main__':
    processor = OrderBookProcessor(symbol='BTC-PERP')

    # pass
    processor.handle(json.dump(message_partial))
    processor.handle(json.dump(message_update))

    # get and print the order book
    order_book = processor.get_orderbook()
    print(order_book)
