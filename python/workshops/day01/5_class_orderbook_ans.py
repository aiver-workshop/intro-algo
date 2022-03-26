"""
An order book is often modelled with a bids and asks sides, each side being an array of (price, quantity, identifier)

Reference: https://realpython.com/python3-object-oriented-programming/

"""
from datetime import datetime


# Tier represents a price level with information of price, quantity, identifier in the order book
class Tier:
    def __init__(self, price: float, size: float, quote_id: str = None):
        self.price = price
        self.size = size
        self.quote_id = quote_id

    def __str__(self):
        return '{' + str(self.price) + ", " + str(self.size) + '}'


# OderBook class to hold bids and asks, as an array of Tiers
class OrderBook:
    def __init__(self, timestamp: float, bids: [Tier], asks: [Tier]):
        self.timestamp = timestamp
        self.bids = bids
        self.asks = asks

    def __str__(self):
        string = 'Bids:'
        for tier in self.bids[:4]:
            string += str(tier) + " "

        string = string + ' Asks:'
        for tier in self.asks[:4]:
            string += str(tier) + " "

        return string


# construct the order book as follows
bids = [Tier(100, 2, 'b0001'), Tier(99, 3, 'b0002'), Tier(98, 4, 'b0003')]
asks = [Tier(101, 2, 'a0001'), Tier(102, 3, 'a0002'), Tier(103, 4, 'a0003')]
order_book = OrderBook(datetime.now(), bids=bids, asks=asks)

# print the order book
print(order_book)

# compute bid/ask spread
spread = order_book.asks[0].price - order_book.bids[0].price
print(spread)
