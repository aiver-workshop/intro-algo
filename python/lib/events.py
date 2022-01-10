from enum import Enum


class OrderStatus(Enum):
    OPEN = 0
    CANCELED = 1
    MODIFIED = 2
    MATCHED = 3


class OrderEvent:
    def __init__(self, contract_name: str, order_id: str, status: OrderStatus, canceled_reason=None, client_id=None):
        self.contract_name = contract_name
        self.order_id = order_id
        self.client_id = client_id
        self.status = status
        self.canceled_reason = canceled_reason

        # the following fields will be populated if matched
        self.fill_time = None
        self.fill_price = None
        self.fill_quantity = None
        self.side = None
        self.fill_id = None
        self.fill_type = None

    def __str__(self):
        return "Order events [contract={}, order_id={}, status={}, canceled_reason={}]".format(self.contract_name, self.order_id, self.status, self.canceled_reason)

    def __repr__(self):
        return str(self)