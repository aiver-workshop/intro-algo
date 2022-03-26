"""
An order book is often modelled with a bids and asks sides, each side being an array of (price, quantity, identifier)

Reference: https://realpython.com/python3-object-oriented-programming/

"""
from datetime import datetime


# create a class named Tier to represent a price level with information of price, quantity, identifier in the order book
# define __str__(self) to print the object as {price, quantity} e.g. {100.20, 10}
class Tier:
    # TODO
    pass


# create a class named OrderBook to hold bids and asks, as an array of Tiers
# add a timestamp variable to store received time
# define def __str__(self) to print both sides
class OrderBook:
    # TODO
    pass


# construct the order book as follows
bids = [Tier(100, 2, 'b0001'), Tier(99, 3, 'b0002'), Tier(98, 4, 'b0003')]
asks = [Tier(101, 2, 'a0001'), Tier(102, 3, 'a0002'), Tier(103, 4, 'a0003')]
order_book = OrderBook(datetime.now(), bids=bids, asks=asks)

# print the order book
print(order_book)

# compute bid/ask spread
# TODO

