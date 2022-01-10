from dydx3 import Client
from web3 import Web3

#
# Access public API endpoints.
#
public_client = Client(
    host='https://api.dydx.exchange',
)

response = public_client.public.get_markets()
print(response.data)

response = public_client.public.get_orderbook('BTC-USD')
print(response.data)


