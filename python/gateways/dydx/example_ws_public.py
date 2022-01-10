import asyncio
import json
import websockets


async def main():
    req = {
        'type': 'subscribe',
        'channel': 'v3_orderbook',
        'id': 'BTC-USD',
        'includeOffsets': True
    }

    # Note: This doesn't work with Python 3.9.
    async with websockets.connect('wss://api.dydx.exchange/v3/ws') as websocket:

        await websocket.send(json.dumps(req))
        print(f'> {req}')

        while True:
            res = await websocket.recv()
            print(f'< {res}')

asyncio.get_event_loop().run_until_complete(main())