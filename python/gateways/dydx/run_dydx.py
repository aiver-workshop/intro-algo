from dydx import DydxManager
import logging
import sys
import time
import os
from dotenv import load_dotenv


# read key and secret from environment variable file
dotenv_path = 'c:/vault/.dydx_keys'
load_dotenv(dotenv_path=dotenv_path)
ETHEREUM_ADDRESS = os.getenv('ETHEREUM_ADDRESS')
L = os.getenv('L')
S = os.getenv('S')
K = os.getenv('K')
P = os.getenv('P')


if __name__ == '__main__':
    # logging stuff
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    handler.setFormatter(logFormatter)
    root.addHandler(handler)

    logging.info("main program starts")

    symbols = {'ETH-USD'}
    dydx = DydxManager(symbol=symbols,
                       ethereum_address=ETHEREUM_ADDRESS,
                       stark_private_key=L, api_s=S,
                       api_k=K,
                       api_p=P,
                       web3_http_provider_url='https://mainnet.infura.io/v3/9a7bac104fd14b5e936862563224f8be')
    dydx.connect()

    # loop till ready
    while True:
        if dydx.not_ready():
            logging.info("Not ready to trade")
            time.sleep(1)
        else:
            break

    while True:
        if dydx.not_ready():
            logging.info("Not ready to trade")
        else:
            logging.info('Depth (ETH): %s' % dydx.get_ticker('ETH-USD'))
            logging.info('Positions (ETH): %s' % dydx.get_delta('ETH-USD'))
            logging.info('Open Orders: %s' % dydx.get_orders('ETH-USD'))

        time.sleep(1)
