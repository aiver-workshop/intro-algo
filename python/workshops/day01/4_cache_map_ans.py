"""
Use a dictionary to store bids and asks price/size of an order book. Sort to get top-of-book prices.

Understand the difference between sort() and sorted()

"""
from collections import defaultdict
from typing import DefaultDict

bids: DefaultDict[float, float] = defaultdict()
asks: DefaultDict[float, float] = defaultdict()

# add the following price/size to bids side: (12.5, 5), (15.2, 4), (11.8, 3)
bids[12.5] = 5
bids[15.2] = 4
bids[11.8] = 3

# add the following price/size to asks side: (24.7, 6), (21.5, 4), (22.1, 1)
asks[24.7] = 6
asks[21.5] = 4
asks[22.1] = 1

# use sorted() to sort bids in descending order to print best price (15.2)
sorted_bids = sorted(bids, reverse=True)
print(sorted_bids[0])

# use sorted() to sort asks in ascending order to print best price (21.5)
sorted_asks = sorted(asks)
print(sorted_asks[0])


