import websockets
import asyncio
import json

URL = 'wss://ftx.com/ws/'

REQUEST_ORDER_BOOK = \
    {
        "channel": "orderbook",
        "market": "BTC-PERP",
        "op": "subscribe"
    }


# an async method to connect to WebSocket
async def subscribe():
    async with websockets.connect(URL) as ws:
        await ws.send(json.dumps(REQUEST_ORDER_BOOK))
        while ws.open:
            resp = await ws.recv()
            print(resp)


# run the subscription
asyncio.run(subscribe())
