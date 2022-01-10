import json

from dydx3 import Client
from dydx3.constants import API_HOST_MAINNET
from dydx3.constants import NETWORK_ID_MAINNET
from web3 import Web3
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

# Query a private endpoint.
reward_response = client.private.get_trading_rewards()
print(json.dumps(reward_response.data))