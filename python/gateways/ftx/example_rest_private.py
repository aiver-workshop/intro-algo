import time
import hmac
from requests import Request, Session
import os
from dotenv import load_dotenv

# read key and secret from environment variable file
dotenv_path = 'c:/vault/.ftx_keys'
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

# REST point to get wallet balances
URL = 'https://ftx.com/api'
method = '/wallet/balances'

# prepare request
request = Request('GET', URL + method)
ts = int(time.time() * 1000)
prepared = request.prepare()
signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
signature = hmac.new(API_SECRET.encode(), signature_payload, 'sha256').hexdigest()
request.headers['FTX-KEY'] = API_KEY
request.headers['FTX-SIGN'] = signature
request.headers['FTX-TS'] = str(ts)

print(request)

# send request
session = Session()
response = session.send(request.prepare())
print(response.json())

# {'success': True, 'result': [{'coin': 'ETH', 'total': 0.00099981, 'free': 0.00099981, 'availableWithoutBorrow': 0.00099981, 'usdValue': 3.1644515040858154, 'spotBorrow': 0.0}, {'coin': 'BTC', 'total': 0.00032779, 'free': 0.00032779, 'availableWithoutBorrow': 0.00032779, 'usdValue': 13.475079013720213, 'spotBorrow': 0.0}, {'coin': 'USD', 'total': 81.42693283, 'free': 81.42693283, 'availableWithoutBorrow': 81.42693283, 'usdValue': 81.4269328305, 'spotBorrow': 0.0}, {'coin': 'USDT', 'total': 0.0, 'free': 0.0, 'availableWithoutBorrow': 0.0, 'usdValue': 0.0, 'spotBorrow': 0.0}]}






