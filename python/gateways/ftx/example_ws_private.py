import websockets
import asyncio
import time
import hmac
import json
import os
from dotenv import load_dotenv

# read key and secret from environment variable file
dotenv_path = 'c:/vault/.ftx_keys'
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

# prepare signature
ts = int(time.time() * 1000)
signature_payload = f'{ts}websocket_login'.encode()
signature = hmac.new(API_SECRET.encode(), signature_payload, 'sha256').hexdigest()

# prepare login message
msg_auth = \
{
  "op": "login",
  "args": {
           "key": API_KEY,
           "sign": signature,
           "time": ts
          }
}
print(msg_auth)


# an async method to connect to WebSocket
async def subscribe():
    async with websockets.connect('wss://ftx.com/ws/') as ws:
        await ws.send(json.dumps(msg_auth))
        while ws.open:
            resp = await ws.recv()
            print(resp)
            # if unsuccessful will receive a response of {"type": "error", "code": 400, "msg": "Invalid login credentials"}

asyncio.get_event_loop().run_until_complete(subscribe())