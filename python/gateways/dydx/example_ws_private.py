from dydx3 import Client
from dydx3.constants import API_HOST_MAINNET
from dydx3.constants import NETWORK_ID_MAINNET
from web3 import Web3
from dydx3.helpers.request_helpers import generate_now_iso
import asyncio
import json
import websockets
import os
from dotenv import load_dotenv


# read key and secret from environment variable file
dotenv_path = 'c:/vault/.eth_keys'
load_dotenv(dotenv_path=dotenv_path)
ETHEREUM_ADDRESS = os.getenv('PUBLIC_KEY')
ETHEREUM_PRIVATE_KEY = os.getenv('PRIVATE_KEY')

# We use a node service by Infura (https://infura.io/) to access the Ethereum chain.
# Start by creating an account; dashboard -> Ethereum -> create project
WEB_PROVIDER_URL = 'https://mainnet.infura.io/v3/9a7bac104fd14b5e936862563224f8be'

client = Client(
    network_id=NETWORK_ID_MAINNET,
    host=API_HOST_MAINNET,
    default_ethereum_address=ETHEREUM_ADDRESS,
    eth_private_key=ETHEREUM_PRIVATE_KEY,
    web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
)

# Set STARK key.
stark_private_key = client.onboarding.derive_stark_key()
client.stark_private_key = stark_private_key

now_iso_string = generate_now_iso()
signature = client.private.sign(
    request_path='/ws/accounts',
    method='GET',
    iso_timestamp=now_iso_string,
    data={},
)

req = {
    'type': 'subscribe',
    'channel': 'v3_accounts',
    'accountNumber': '0',
    'apiKey': client.api_key_credentials['key'],
    'passphrase': client.api_key_credentials['passphrase'],
    'timestamp': now_iso_string,
    'signature': signature,
}


async def main():
    # Note: This doesn't work with Python 3.9.
    async with websockets.connect('wss://api.dydx.exchange/v3/ws') as websocket:

        await websocket.send(json.dumps(req))
        print(f'> {req}')

        while True:
            res = await websocket.recv()
            print(f'< {res}')

asyncio.get_event_loop().run_until_complete(main())