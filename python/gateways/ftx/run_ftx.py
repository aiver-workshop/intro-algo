from ftx import FtxManager
import time
import logging
import sys
import os
from dotenv import load_dotenv

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

    # read key and secret from environment variable file
    dotenv_path = 'c:/vault/.ftx_keys'
    load_dotenv(dotenv_path=dotenv_path)
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')

    contract = 'BTC-PERP'
    contracts = {contract}

    ftx = FtxManager(symbol=contracts, api_key=API_KEY, api_secret=API_SECRET)
    ftx.connect()

    while True:
        time.sleep(2)

        if ftx.not_ready():
            logging.info("Not ready to trade")
        else:
            logging.info('Depth: %s' % ftx.get_ticker(contract))
            logging.info('Positions: %s' % ftx.get_delta(contract))
            logging.info('Open Orders: %s' % ftx.get_orders(contract))