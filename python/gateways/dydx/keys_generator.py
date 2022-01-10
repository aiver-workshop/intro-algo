from dydx3 import Client
from dydx3.constants import API_HOST_MAINNET
from dydx3.constants import NETWORK_ID_MAINNET
from web3 import Web3
import os
from dotenv import load_dotenv

WEB_PROVIDER_URL = 'https://mainnet.infura.io/v3/9a7bac104fd14b5e936862563224f8be'


def generate_l2_key(eth_address: str, eth_private_key: str) -> str:
    client = Client(
        network_id=NETWORK_ID_MAINNET,
        host=API_HOST_MAINNET,
        default_ethereum_address=eth_address,
        eth_private_key=eth_private_key,
        web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
    )

    return client.onboarding.derive_stark_key()


def generate_api_key(eth_address: str, eth_private_key: str) -> str:
    client = Client(
        network_id=NETWORK_ID_MAINNET,
        host=API_HOST_MAINNET,
        default_ethereum_address=eth_address,
        eth_private_key=eth_private_key,
        web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
    )

    return client.onboarding.recover_default_api_key_credentials(eth_address)


if __name__ == '__main__':
    # read key and secret from environment variable file
    dotenv_path = 'c:/vault/.eth_keys'
    load_dotenv(dotenv_path=dotenv_path)
    eth_public_address = os.getenv('PUBLIC_KEY')
    eth_private_key = os.getenv('PRIVATE_KEY')

    stark_private_key = generate_l2_key(eth_public_address, eth_private_key)
    print(stark_private_key)

    api_key = generate_api_key(eth_public_address, eth_private_key)
    print(api_key)
