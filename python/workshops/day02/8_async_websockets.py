"""
Websockets is a Python library that support asyncio framework.

Take a look at the FTX api below, and learn to establish a connection a subscribe to order book data.
Reference: https://docs.ftx.com/?python#websocket-api

"""
import websockets
import asyncio
import json

# TODO get the URL from the API documentation
URL = ''

REQUEST_ORDER_BOOK = \
    {
        "channel": "",
        "market": "",
        "op": ""
    }


# an async method to connect to WebSocket
async def subscribe():
    async with websockets.connect(URL) as ws:
        await ws.send(json.dumps(REQUEST_ORDER_BOOK))
        while ws.open:
            resp = await ws.recv()
            print(resp)


# TODO run the subscription
