import unittest
import json
import gateways.ftx.ftx as ftx
from lib.interface import OrderBook, Tier, Order, Side, InstrumentDetails, NewOrderSingle, OrderType


class TestFtx(unittest.TestCase):
    def test_OrderBookProcessor(self):
        processor = ftx.OrderBookProcessor('BTC-PERP')

        message = '{"channel": "orderbook", "market": "BTC-PERP", "type": "partial", "data": {"time": 1630851340.6570554, "checksum": 3975705594, "bids": [[50492.0, 0.8454], [50491.0, 0.9953], [50490.0, 2.8681], [50489.0, 0.2663], [50488.0, 14.2327], [50487.0, 0.1397], [50483.0, 0.1917], [50482.0, 0.04], [50480.0, 0.6244], [50479.0, 2.5], [50476.0, 3.3234], [50475.0, 3.005], [50474.0, 2.1355], [50473.0, 10.5411], [50472.0, 3.7922], [50471.0, 0.7619], [50470.0, 6.2039], [50469.0, 5.4289], [50468.0, 3.068], [50467.0, 4.8818], [50466.0, 0.9903], [50465.0, 1.6893], [50464.0, 0.8642], [50463.0, 11.9904], [50461.0, 0.6889], [50460.0, 0.8366], [50459.0, 4.9592], [50458.0, 5.0914], [50456.0, 0.7646], [50455.0, 4.7132], [50454.0, 0.1642], [50452.0, 0.1692], [50451.0, 0.01], [50450.0, 1.395], [50449.0, 0.712], [50448.0, 2.2755], [50447.0, 7.0592], [50446.0, 0.4608], [50445.0, 0.01], [50441.0, 0.081], [50440.0, 2.4925], [50439.0, 0.01], [50438.0, 1.3737], [50437.0, 3.1832], [50436.0, 0.1901], [50435.0, 0.1544], [50434.0, 16.6701], [50433.0, 4.329], [50432.0, 0.007], [50431.0, 0.427], [50430.0, 0.1916], [50429.0, 5.4328], [50428.0, 1.3141], [50427.0, 0.1935], [50426.0, 2.7381], [50425.0, 1.088], [50424.0, 0.132], [50420.0, 1.6505], [50419.0, 0.2067], [50418.0, 0.443], [50417.0, 0.0456], [50416.0, 0.3925], [50413.0, 0.0112], [50412.0, 0.219], [50411.0, 0.8467], [50410.0, 0.0594], [50409.0, 2.9312], [50408.0, 0.06], [50407.0, 0.5035], [50406.0, 8.1521], [50405.0, 2.5809], [50404.0, 1.0], [50403.0, 0.0771], [50402.0, 0.05], [50401.0, 2.0019], [50400.0, 1.0023], [50399.0, 0.0616], [50398.0, 8.317], [50397.0, 0.3729], [50396.0, 1.4805], [50395.0, 3.8471], [50394.0, 1.4953], [50393.0, 0.0198], [50392.0, 0.2947], [50391.0, 0.0992], [50390.0, 2.148], [50389.0, 2.9902], [50388.0, 0.0698], [50387.0, 2.9078], [50386.0, 9.6613], [50385.0, 6.777], [50384.0, 0.0635], [50383.0, 18.9997], [50382.0, 0.6193], [50381.0, 2.498], [50380.0, 51.9276], [50379.0, 0.016], [50378.0, 0.6025], [50376.0, 0.2423], [50375.0, 0.0298]], "asks": [[50493.0, 0.3965], [50494.0, 0.1226], [50495.0, 1.1669], [50496.0, 0.2914], [50497.0, 0.04], [50498.0, 0.05], [50499.0, 0.2077], [50500.0, 78.8888], [50501.0, 0.01], [50502.0, 0.001], [50503.0, 0.4551], [50504.0, 0.0002], [50505.0, 0.338], [50506.0, 9.613], [50507.0, 3.6605], [50508.0, 3.9933], [50509.0, 1.1588], [50510.0, 1.6636], [50511.0, 1.5979], [50512.0, 14.8138], [50513.0, 0.5578], [50514.0, 3.1109], [50515.0, 0.9722], [50516.0, 0.064], [50517.0, 0.989], [50518.0, 0.1], [50519.0, 0.1763], [50520.0, 1.3286], [50521.0, 0.028], [50522.0, 0.4493], [50523.0, 2.5214], [50524.0, 3.1898], [50525.0, 3.1379], [50526.0, 1.3874], [50527.0, 3.7808], [50528.0, 2.352], [50529.0, 0.1112], [50530.0, 0.0525], [50531.0, 0.1974], [50532.0, 1.4127], [50533.0, 3.5336], [50534.0, 0.2862], [50535.0, 0.0111], [50536.0, 27.9072], [50537.0, 1.4121], [50538.0, 5.2996], [50539.0, 0.8193], [50540.0, 0.0199], [50541.0, 3.4636], [50542.0, 4.7419], [50543.0, 0.0638], [50544.0, 1.0375], [50545.0, 0.0811], [50546.0, 1.2032], [50547.0, 9.7002], [50548.0, 0.9505], [50549.0, 3.3195], [50550.0, 27.7852], [50551.0, 0.3346], [50552.0, 0.0105], [50553.0, 0.0673], [50554.0, 11.0872], [50555.0, 1.015], [50556.0, 0.0385], [50557.0, 0.0457], [50558.0, 2.2542], [50559.0, 0.2807], [50560.0, 0.0134], [50561.0, 0.0765], [50562.0, 0.1452], [50563.0, 7.3371], [50564.0, 0.0079], [50565.0, 0.0337], [50566.0, 0.0023], [50567.0, 0.2006], [50569.0, 0.0001], [50570.0, 4.9903], [50571.0, 0.7769], [50572.0, 3.2975], [50574.0, 0.0337], [50575.0, 0.079], [50576.0, 0.01], [50577.0, 7.8627], [50579.0, 15.7567], [50580.0, 3.4208], [50581.0, 10.0101], [50582.0, 0.0649], [50583.0, 50.7268], [50584.0, 11.6489], [50585.0, 0.0797], [50586.0, 0.7], [50588.0, 0.9131], [50589.0, 0.7748], [50590.0, 1.0261], [50591.0, 0.0616], [50592.0, 11.3727], [50593.0, 0.031], [50595.0, 0.0047], [50597.0, 1.8838], [50598.0, 18.0634]], "action": "partial"}}'
        processor.handle(json.loads(message))

        order_book = processor.get_orderbook()
        self.assertEqual(5, len(order_book.bids))
        self.assertEqual(5, len(order_book.asks))

        self.assertEqual(50492.0, order_book.bids[0].price)
        self.assertEqual(0.8454, order_book.bids[0].size)
        self.assertEqual(50491.0, order_book.bids[1].price)
        self.assertEqual(0.9953, order_book.bids[1].size)
        self.assertEqual(50490.0, order_book.bids[2].price)
        self.assertEqual(2.8681, order_book.bids[2].size)
        self.assertEqual(50489.0, order_book.bids[3].price)
        self.assertEqual(0.2663, order_book.bids[3].size)
        self.assertEqual(50488.0, order_book.bids[4].price)
        self.assertEqual(14.2327, order_book.bids[4].size)

        self.assertEqual(50493.0, order_book.asks[0].price)
        self.assertEqual(0.3965, order_book.asks[0].size)
        self.assertEqual(50494.0, order_book.asks[1].price)
        self.assertEqual(0.1226, order_book.asks[1].size)
        self.assertEqual(50495.0, order_book.asks[2].price)
        self.assertEqual(1.1669, order_book.asks[2].size)
        self.assertEqual(50496.0, order_book.asks[3].price)
        self.assertEqual(0.2914, order_book.asks[3].size)
        self.assertEqual(50497.0, order_book.asks[4].price)
        self.assertEqual(0.04, order_book.asks[4].size)

        message = '{"channel": "orderbook", "market": "BTC-PERP", "type": "update", "data": {"time": 1630851340.7094188, "checksum": 645000214, "bids": [[50492.0, 3.3554], [50491.0, 1.2548], [50489.0, 0.0259], [50486.0, 0.0991], [50483.0, 0.5879], [50479.0, 0.0], [50477.0, 0.25], [50470.0, 7.1769], [50468.0, 3.0268], [50465.0, 1.6993], [50463.0, 12.5014], [50426.0, 28.0923], [50396.0, 0.1901], [50375.0, 0.0]], "asks": [[50494.0, 0.0956], [50509.0, 1.1648], [50510.0, 1.6736], [50516.0, 0.1571], [50522.0, 1.5493], [50523.0, 2.7029], [50540.0, 0.0299], [50593.0, 0.061]], "action": "update"}}'
        processor.handle(json.loads(message))

        order_book = processor.get_orderbook()
        self.assertEqual(5, len(order_book.bids))
        self.assertEqual(5, len(order_book.asks))

        self.assertEqual(50492.0, order_book.bids[0].price)
        self.assertEqual(3.3554, order_book.bids[0].size)
        self.assertEqual(50491.0, order_book.bids[1].price)
        self.assertEqual(1.2548, order_book.bids[1].size)
        # this layer has no update, remain
        self.assertEqual(50490.0, order_book.bids[2].price)
        self.assertEqual(2.8681, order_book.bids[2].size)
        self.assertEqual(50489.0, order_book.bids[3].price)
        self.assertEqual(0.0259, order_book.bids[3].size)
        # this layer has no update, remain
        self.assertEqual(50488.0, order_book.bids[4].price)
        self.assertEqual(14.2327, order_book.bids[4].size)

        # no change in first layer
        self.assertEqual(50493.0, order_book.asks[0].price)
        self.assertEqual(0.3965, order_book.asks[0].size)
        self.assertEqual(50494.0, order_book.asks[1].price)
        self.assertEqual(0.0956, order_book.asks[1].size)
        self.assertEqual(50495.0, order_book.asks[2].price)
        self.assertEqual(1.1669, order_book.asks[2].size)
        self.assertEqual(50496.0, order_book.asks[3].price)
        self.assertEqual(0.2914, order_book.asks[3].size)
        self.assertEqual(50497.0, order_book.asks[4].price)
        self.assertEqual(0.04, order_book.asks[4].size)


    def test_OrderBookProcessor_delete(self):
        processor = ftx.OrderBookProcessor('BTC-PERP')

        message = '{"channel": "orderbook", "market": "BTC-PERP", "type": "partial", "data": {"time": 1630851340.6570554, "checksum": 3975705594, "bids": [[100, 0.01], [100.1, 0.02], [100.2, 0.03]], "asks": [[200.3, 0.08], [200.2, 0.07], [200.1, 0.06]], "action": "partial"}}'
        processor.handle(json.loads(message))

        order_book = processor.get_orderbook()
        self.assertEqual(3, len(order_book.bids))
        self.assertEqual(3, len(order_book.asks))

        self.assertEqual(100.2, order_book.bids[0].price)
        self.assertEqual(0.03, order_book.bids[0].size)
        self.assertEqual(100.1, order_book.bids[1].price)
        self.assertEqual(0.02, order_book.bids[1].size)
        self.assertEqual(100, order_book.bids[2].price)
        self.assertEqual(0.01, order_book.bids[2].size)

        self.assertEqual(200.1, order_book.asks[0].price)
        self.assertEqual(0.06, order_book.asks[0].size)
        self.assertEqual(200.2, order_book.asks[1].price)
        self.assertEqual(0.07, order_book.asks[1].size)
        self.assertEqual(200.3, order_book.asks[2].price)
        self.assertEqual(0.08, order_book.asks[2].size)

        # delete bids
        message = '{"channel": "orderbook", "market": "BTC-PERP", "type": "update", "data": {"time": 1630851340.7094188, "checksum": 645000214, "bids": [[100, 0.00], [100.1, 0], [100.2, 0.0]], "asks": [], "action": "update"}}'
        processor.handle(json.loads(message))

        order_book = processor.get_orderbook()
        self.assertEqual(0, len(order_book.bids))
        self.assertEqual(3, len(order_book.asks))

        self.assertEqual(200.1, order_book.asks[0].price)
        self.assertEqual(0.06, order_book.asks[0].size)
        self.assertEqual(200.2, order_book.asks[1].price)
        self.assertEqual(0.07, order_book.asks[1].size)
        self.assertEqual(200.3, order_book.asks[2].price)
        self.assertEqual(0.08, order_book.asks[2].size)

        # delete asks
        message = '{"channel": "orderbook", "market": "BTC-PERP", "type": "update", "data": {"time": 1630851340.7094188, "checksum": 645000214, "bids": [], "asks": [[200.1, 0.0]], "action": "update"}}'
        processor.handle(json.loads(message))

        order_book = processor.get_orderbook()
        self.assertEqual(0, len(order_book.bids))
        self.assertEqual(2, len(order_book.asks))

        self.assertEqual(200.2, order_book.asks[0].price)
        self.assertEqual(0.07, order_book.asks[0].size)
        self.assertEqual(200.3, order_book.asks[1].price)
        self.assertEqual(0.08, order_book.asks[1].size)

    def test_positions(self):
        message = '{"success": "True", "result": []}'
        store = ftx.process_position(json.loads(message))

        # should be empty
        self.assertFalse(store)

        # long
        message = '{"success": "True", "result": [{"future": "BTC-PERP", "size": 0.0001, "side": "buy", "netSize": 0.0001, "longOrderSize": 0.0, "shortOrderSize": 0.0, "cost": 4.7122, "entryPrice": 47122.0, "unrealizedPnl": 0.0, "realizedPnl": 0.0123, "initialMarginRequirement": 1.0, "maintenanceMarginRequirement": 0.03, "openSize": 0.0001, "collateralUsed": 4.7122, "estimatedLiquidationPrice": 0.0}]}'
        store = ftx.process_position(json.loads(message))
        self.assertEqual(0.0001, store.get("BTC-PERP"))

        # short
        message = '{"success": "True", "result": [{"future": "BTC-PERP", "size": 0.0001, "side": "sell", "netSize": -0.0001, "longOrderSize": 0.0, "shortOrderSize": 0.0, "cost": -4.7055, "entryPrice": 47055.0, "unrealizedPnl": 0.0, "realizedPnl": -0.0139, "initialMarginRequirement": 1.0, "maintenanceMarginRequirement": 0.03, "openSize": 0.0001, "collateralUsed": 4.7055, "estimatedLiquidationPrice": 1045410.64219}]}'
        store = ftx.process_position(json.loads(message))
        self.assertEqual(-0.0001, store.get("BTC-PERP"))

    def test_process_wallet_balances(self):
        message = '{"success": "True", "result": [{"coin": "ETH", "total": 0.00099981, "free": 0.00099981, "availableWithoutBorrow": 0.00099981, "usdValue": 3.6293909786081513, "spotBorrow": 0.0}, {"coin": "BTC", "total": 0.00012779, "free": 0.00012779, "availableWithoutBorrow": 0.00012779, "usdValue": 6.154081081476318, "spotBorrow": 0.0}, {"coin": "USD", "total": 90.49253176, "free": 90.49253176, "availableWithoutBorrow": 90.49253176, "usdValue": 90.4925317685, "spotBorrow": 0.0}, {"coin": "USDT", "total": 0.0, "free": 0.0, "availableWithoutBorrow": 0.0, "usdValue": 0.0, "spotBorrow": 0.0}]}'
        store = ftx.process_wallet_balances(json.loads(message))
        self.assertEqual(0.00012779, store.get("BTC"))
        self.assertEqual(0.00099981, store.get("ETH"))
        self.assertEqual(90.49253176, store.get("USD"))


    def test_process_fills(self):
        message = '{"channel": "fills", "type": "update", "data": {"id": 3692005673, "market": "BTC-PERP", "future": "BTC-PERP", "baseCurrency": null, "quoteCurrency": null, "type": "order", "side": "sell", "price": 47052.0, "size": 0.0001, "orderId": 77913105521, "time": "2021-09-09T14:10:25.646508+00:00", "tradeId": 1832691741, "feeRate": 0.000665, "fee": 0.003128958, "feeCurrency": "USD", "liquidity": "taker"}}'
        store = {}
        ftx.process_fills(json.loads(message), store)
        self.assertEqual(-0.0001, store.get('BTC-PERP'))

        ftx.process_fills(json.loads(message), store)
        self.assertEqual(-0.0002, store.get('BTC-PERP'))

        # https://stackoverflow.com/questions/24914298/why-0-000610000010-is-10
        # 0.0006 and 0.0003 are not representable in a machine double precisely
        ftx.process_fills(json.loads(message), store)
        self.assertEqual(-0.00030000000000000003, store.get('BTC-PERP'))

    def test_process_fills_spot(self):
        message = '{"channel": "fills", "type": "update", "data": {"id": 3821365218, "market": "BTC/USD", "future": null, "baseCurrency": "BTC", "quoteCurrency": "USD", "type": "order", "side": "buy", "price": 48022.0, "size": 0.0004, "orderId": 79884212404, "time": "2021-09-16T15:57:58.186132+00:00", "tradeId": 1896884218, "feeRate": 0.000665, "fee": 0.012773852, "feeCurrency": "USD", "liquidity": "taker"}}'
        store = {}
        ftx.process_fills(json.loads(message), store)
        self.assertEqual(0.0004, store.get('BTC'))


    def test_process_orders_closed_filled(self):
        message = '{"channel": "orders", "type": "update", "data": {"id": 77929828233, "clientId": null, "market": "BTC-PERP", "type": "market", "side": "buy", "price": null, "size": 0.0001, "status": "closed", "filledSize": 0.0001, "remainingSize": 0.0, "reduceOnly": false, "liquidation": false, "avgFillPrice": 46880.0, "postOnly": false, "ioc": true, "createdAt": "2021-09-09T15:26:59.160469+00:00"}}'
        store = {}
        order_event = ftx.process_orders_ws(json.loads(message), store)
        self.assertFalse('BTC-PERP' in store)
        self.assertEqual(ftx.OrderStatus.MATCHED, order_event.status)


    def test_process_orders_closed_unfilled(self):
        message = '{"channel": "orders", "type": "update", "data": {"id": 77932638250, "clientId": null, "market": "BTC-PERP", "type": "limit", "side": "buy", "price": 30000.0, "size": 0.0001, "status": "closed", "filledSize": 0.0, "remainingSize": 0.0, "reduceOnly": false, "liquidation": false, "avgFillPrice": null, "postOnly": false, "ioc": true, "createdAt": "2021-09-09T15:40:08.938301+00:00"}}'
        store = {}
        order_event = ftx.process_orders_ws(json.loads(message), store)
        self.assertFalse('BTC-PERP' in store)
        self.assertEqual(ftx.OrderStatus.CANCELED, order_event.status)

    def test_order_market(self):
        client_id = 'ftx-123'
        instrument_static = ftx.InstrumentDetails('BTC-PERP', tick_size=1.0, quantity_size=0.0001)
        order = NewOrderSingle('BTC-PERP', Side.Buy, 0.001, OrderType.Market)
        request = ftx.get_place_order_message(order, instrument_static, client_id)

        expectation = \
            {
                "market": "BTC-PERP",
                "side": "buy",
                "price": None,
                "type": "market",
                "size": 0.001,
                "ioc": False,
                "postOnly": False,
                "clientId": client_id
            }
        self.assertEqual(json.dumps(expectation), json.dumps(request))

    def test_order_market_post(self):
        client_id = 'ftx-123'
        instrument_static = InstrumentDetails('BTC-PERP', tick_size=1.0, quantity_size=0.0001)
        order = NewOrderSingle('BTC-PERP', Side.Buy, 0.001, OrderType.Market, post_only=True)
        request = ftx.get_place_order_message(order, instrument_static, client_id)

        expectation = \
            {
                "market": "BTC-PERP",
                "side": "buy",
                "price": None,
                "type": "market",
                "size": 0.001,
                "ioc": False,
                "postOnly": True,
                "clientId": client_id
            }
        self.assertEqual(json.dumps(expectation), json.dumps(request))

    def test_order_limit(self):
        client_id = 'ftx-123'
        instrument_static = InstrumentDetails('BTC-PERP', tick_size=1.0, quantity_size=0.0001)
        order = NewOrderSingle('BTC-PERP', Side.Sell, 0.001, OrderType.Limit, price=30000)
        request = ftx.get_place_order_message(order, instrument_static, client_id)

        expectation = \
            {
                "market": "BTC-PERP",
                "side": "sell",
                "price": 30000,
                "type": "limit",
                "size": 0.001,
                "ioc": False,
                "postOnly": False,
                "clientId": client_id
            }
        self.assertEqual(json.dumps(expectation), json.dumps(request))

    def test_order_ioc(self):
        client_id = 'ftx-123'
        instrument_static = InstrumentDetails('BTC-PERP', tick_size=1.0, quantity_size=0.0001)
        order = NewOrderSingle('BTC-PERP', Side.Buy, 0.001, OrderType.IOC, price=30000)
        request = ftx.get_place_order_message(order, instrument_static, client_id)

        expectation = \
            {
                "market": "BTC-PERP",
                "side": "buy",
                "price": 30000,
                "type": "limit",
                "size": 0.001,
                "ioc": True,
                "postOnly": False,
                "clientId": client_id
            }
        self.assertEqual(json.dumps(expectation), json.dumps(request))



    def test_ready_check(self):
        flag = ftx.ReadyCheck()
        self.assertFalse(flag.streams_ready())
        self.assertTrue(flag.not_ready())

        flag.snapshot_ready = True
        self.assertFalse(flag.streams_ready())
        self.assertTrue(flag.not_ready())

        flag.ws_connected = True
        self.assertFalse(flag.streams_ready())
        self.assertTrue(flag.not_ready())

        flag.orders_stream_ready = True
        self.assertFalse(flag.streams_ready())
        self.assertTrue(flag.not_ready())

        flag.depth_stream_ready = True
        self.assertFalse(flag.streams_ready())
        self.assertTrue(flag.not_ready())

        # all ready
        flag.position_stream_ready = True
        self.assertTrue(flag.streams_ready())
        self.assertFalse(flag.not_ready())

        # has circuit break
        flag.circuit_break = True
        self.assertTrue(flag.not_ready())

        # circuit break removed
        flag.circuit_break = False
        self.assertFalse(flag.not_ready())

        # lost hearbeat
        flag.lost_heartbeat = True
        self.assertTrue(flag.not_ready())

    def test_ready_check_snapshot(self):
        flag = ftx.ReadyCheck()
        flag.ws_connected = True
        flag.orders_stream_ready = True
        flag.depth_stream_ready = True
        flag.position_stream_ready = True
        self.assertTrue(flag.not_ready())

        # fully ready when snapshot also ready
        flag.snapshot_ready = True
        self.assertFalse(flag.not_ready())


    def test_process_orders_new(self):
        message = '{"channel": "orders", "type": "update", "data": {"id": 77921137820, "clientId": "abc", "market": "BTC-PERP", "type": "limit", "side": "buy", "price": 30000.0, "size": 0.0001, "status": "new", "filledSize": 0.0, "remainingSize": 0.0001, "reduceOnly": "false", "liquidation": "false", "avgFillPrice": null, "postOnly": false, "ioc": false, "createdAt": "2021-09-09T14:47:17.792437+00:00"}}'
        store = {}
        order_event = ftx.process_orders_ws(json.loads(message), store)
        self.assertEqual(ftx.OrderStatus.OPEN, order_event.status)
        self.assertEqual("abc", order_event.client_id)

        orders = store.get("BTC-PERP")
        self.assertEqual(1, len(orders))
        order = orders['77921137820']
        self.assertEqual("77921137820", order.orderID)
        self.assertEqual("BTC-PERP", order.symbol)
        self.assertEqual(Side.Buy, order.side)
        self.assertEqual(0.0001, order.leavesQty)
        self.assertEqual(30000, order.price)
        self.assertEqual("LIMIT", order.type)

    def test_is_spot(self):
        self.assertTrue(ftx.is_spot('BTC/USD'))
        self.assertTrue(ftx.is_spot('ETH/USD'))

        self.assertFalse(ftx.is_spot('BTC-PERP'))

