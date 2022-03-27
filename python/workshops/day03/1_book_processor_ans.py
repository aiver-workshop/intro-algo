import json
from lib.interface import OrderBook, Tier
from collections import defaultdict
from typing import DefaultDict


message_partial = '{"channel": "orderbook", "market": "BTC-PERP", "type": "partial", "data": {"time": 1648382275.1076198, "checksum": 3286356399, "bids": [[44576.0, 6.6639], [44575.0, 1.5101], [44574.0, 0.458], [44573.0, 0.1224], [44571.0, 0.3889], [44570.0, 4.701], [44569.0, 1.0743], [44568.0, 0.1552], [44567.0, 4.383], [44566.0, 3.9471], [44565.0, 5.1978], [44564.0, 5.3502], [44563.0, 7.6548], [44562.0, 1.3408], [44561.0, 1.1889], [44560.0, 4.9346], [44559.0, 1.482], [44558.0, 0.797], [44557.0, 0.4059], [44556.0, 0.0102], [44555.0, 18.4502], [44554.0, 1.4907], [44553.0, 6.1632], [44552.0, 3.7276], [44550.0, 0.0715], [44549.0, 1.4021], [44548.0, 9.0308], [44547.0, 11.4931], [44546.0, 2.3081], [44545.0, 1.2403], [44544.0, 1.2312], [44543.0, 3.0192], [44542.0, 18.9078], [44541.0, 9.5435], [44540.0, 3.9879], [44539.0, 2.9329], [44538.0, 7.8009], [44537.0, 18.5559], [44536.0, 13.8252], [44535.0, 0.1515], [44533.0, 0.3068], [44532.0, 0.0088], [44531.0, 18.5739], [44530.0, 9.0396], [44529.0, 0.4894], [44528.0, 10.4866], [44527.0, 1.7422], [44526.0, 6.342], [44525.0, 3.8395], [44524.0, 6.9216], [44523.0, 0.3343], [44522.0, 13.6518], [44521.0, 8.5023], [44520.0, 0.2344], [44519.0, 18.3164], [44518.0, 0.2294], [44517.0, 2.1954], [44516.0, 1.025], [44515.0, 0.3019], [44514.0, 0.2146], [44513.0, 21.5935], [44512.0, 0.0251], [44511.0, 0.2028], [44510.0, 0.2237], [44509.0, 0.1814], [44508.0, 3.2272], [44507.0, 2.0961], [44506.0, 0.1759], [44505.0, 1.1881], [44504.0, 4.5383], [44503.0, 0.2697], [44502.0, 0.3368], [44501.0, 0.0074], [44500.0, 3.7231], [44499.0, 0.66], [44498.0, 9.8771], [44497.0, 0.0159], [44496.0, 0.0194], [44495.0, 0.0495], [44494.0, 0.4877], [44493.0, 0.0002], [44492.0, 16.5406], [44491.0, 0.001], [44490.0, 2.8453], [44489.0, 0.0738], [44488.0, 8.9183], [44487.0, 0.5783], [44485.0, 0.018], [44484.0, 0.04], [44483.0, 0.2478], [44482.0, 0.273], [44481.0, 0.4815], [44480.0, 0.3164], [44479.0, 9.9453], [44478.0, 0.0123], [44477.0, 5.0088], [44476.0, 9.2027], [44475.0, 0.112], [44474.0, 0.4528], [44473.0, 0.2645]], "asks": [[44577.0, 1.9096], [44579.0, 0.2833], [44580.0, 0.5], [44581.0, 0.58], [44582.0, 0.15], [44583.0, 3.9696], [44584.0, 4.6955], [44585.0, 1.7754], [44586.0, 6.6103], [44587.0, 3.6312], [44588.0, 1.8795], [44590.0, 0.4733], [44591.0, 0.5843], [44592.0, 0.9078], [44593.0, 3.8579], [44594.0, 5.3613], [44595.0, 0.4603], [44596.0, 4.7939], [44597.0, 6.5803], [44598.0, 9.843], [44599.0, 9.1117], [44600.0, 1.2456], [44601.0, 0.5032], [44602.0, 0.504], [44603.0, 5.6777], [44604.0, 12.3896], [44605.0, 0.6411], [44606.0, 16.2399], [44607.0, 14.3524], [44608.0, 0.6081], [44609.0, 1.0389], [44610.0, 0.1343], [44611.0, 1.5269], [44612.0, 0.3265], [44613.0, 0.0469], [44614.0, 2.1337], [44616.0, 0.0117], [44617.0, 0.1068], [44618.0, 0.538], [44619.0, 0.3276], [44620.0, 17.6085], [44621.0, 3.2146], [44622.0, 21.4696], [44623.0, 5.9854], [44624.0, 0.269], [44625.0, 0.2181], [44626.0, 0.1623], [44627.0, 0.0067], [44628.0, 7.3194], [44629.0, 3.3982], [44630.0, 2.0868], [44631.0, 0.0469], [44632.0, 0.5612], [44633.0, 10.8415], [44634.0, 0.075], [44635.0, 5.4723], [44636.0, 14.0447], [44637.0, 7.7654], [44638.0, 0.2544], [44639.0, 1.3979], [44640.0, 1.2062], [44641.0, 1.047], [44643.0, 6.8309], [44644.0, 0.01], [44646.0, 0.2747], [44647.0, 0.0068], [44649.0, 0.0089], [44650.0, 2.1325], [44651.0, 0.5087], [44654.0, 0.05], [44656.0, 2.9881], [44657.0, 2.8242], [44659.0, 0.1827], [44660.0, 2.3772], [44661.0, 0.279], [44663.0, 1.2831], [44664.0, 6.0771], [44665.0, 0.0022], [44666.0, 14.8856], [44667.0, 0.5608], [44669.0, 0.0068], [44671.0, 0.0068], [44672.0, 0.0044], [44673.0, 1.5184], [44674.0, 21.267], [44675.0, 0.0054], [44676.0, 0.2687], [44678.0, 0.8466], [44680.0, 0.2876], [44682.0, 8.339], [44683.0, 0.0034], [44684.0, 0.0865], [44685.0, 16.5858], [44686.0, 0.28], [44687.0, 0.005], [44688.0, 0.236], [44689.0, 0.0068], [44690.0, 3.9915], [44692.0, 0.0023], [44693.0, 0.4802]], "action": "partial"}}'

message_update = '{"channel": "orderbook", "market": "BTC-PERP", "type": "update", "data": {"time": 1648382275.1340098, "checksum": 2034798929, "bids": [], "asks": [[44592.0, 2.1428], [44593.0, 0.0117]], "action": "update"}}'


# Create a helper class to process order book messages
class OrderBookProcessor:
    def __init__(self, symbol: str, depth=5):
        self._symbol = symbol
        self._depth = depth

        # a map that contain bids and asks sides
        self._bids : DefaultDict[float, float] = defaultdict()
        self._asks: DefaultDict[float, float] = defaultdict()
        self._timestamp = 0

    def handle(self, message: {}):
        market = message['market']
        if market != self._symbol:
            raise ValueError("Received message for market {} but this processor is for {}".format(market, self._symbol))

        data = message['data']

        if data['action'] == 'partial':
            self._reset()

        # process bids side
        for price, size in data['bids']:
            if size:
                self._bids[price] = size
            else:
                del self._bids[price]

        # process asks side
        for price, size in data['asks']:
            if size:
                self._asks[price] = size
            else:
                del self._asks[price]

        self._timestamp = data['time']

    def get_orderbook(self) -> OrderBook:
        if self._timestamp == 0:
            return 0

        # sort bids in descending order (largest first), only if quantity > 0
        sorted_bids = sorted([(price, quantity) for price, quantity in list(self._bids.items()) if quantity], reverse=True)

        # sort asks in ascending order (smallest first), only if quantity > 0
        sorted_asks = sorted([(price, quantity) for price, quantity in list(self._asks.items()) if quantity])

        return OrderBook(timestamp=self._timestamp,
                         bids=[Tier(price=p, size=s) for (p, s) in sorted_bids[:self._depth]],
                         asks=[Tier(price=p, size=s) for (p, s) in sorted_asks[:self._depth]])

    def _reset(self) -> None:
        self._bids: DefaultDict[float, float] = defaultdict()
        self._asks: DefaultDict[float, float] = defaultdict()
        self._timestamp = 0


# A driver class to demonstrate the usage of the order book processor
if __name__ == '__main__':
    processor = OrderBookProcessor(symbol='BTC-PERP')

    # pass
    processor.handle(json.loads(message_partial))
    processor.handle(json.loads(message_update))

    # get and print the order book
    order_book = processor.get_orderbook()
    print(order_book)
