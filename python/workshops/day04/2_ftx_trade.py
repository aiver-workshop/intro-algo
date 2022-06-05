import os
from dotenv import load_dotenv
from gateways.ftx.ftx import FtxManager
from lib.interface import Side, NewOrderSingle, OrderType
import time

dotenv_path = 'c:/vault/.ftx_keys'
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

ftx = FtxManager(symbol={"BTC-PERP"}, api_key=API_KEY, api_secret=API_SECRET)

ftx.connect()

while True:
    if ftx.not_ready():
       print("Not ready to trade")
       time.sleep(1)
    else:
       break

# gateway is ready, raise an order
print("Sending a limit order...")
limit_order = NewOrderSingle('BTC-PERP', Side.Buy, 0.01, OrderType.Limit, price=24888)
ftx.place_order(limit_order)




