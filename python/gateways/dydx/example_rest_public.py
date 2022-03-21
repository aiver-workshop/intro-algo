from dydx3 import Client
from web3 import Web3

#
# Access public API endpoints.
#
public_client = Client(
    host='https://api.dydx.exchange',
)

# Query market static data
response = public_client.public.get_markets()
print(response.data.get('markets'))

# Query order book snapshot
response = public_client.public.get_orderbook('BTC-USD')
print(response.data)


