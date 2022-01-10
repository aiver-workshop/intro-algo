from datetime import datetime
import uuid


class OrderIdGenerator:
    def __init__(self, prefix: str):
        random_id = uuid.uuid4()
        date_str = datetime.now().strftime("%Y%m%d")
        self._prefix = prefix + "-" + date_str + "-" + str(random_id)[0:8] + "-"
        self._counter = 0

    def get_prefix(self) -> str:
        return self._prefix

    def next(self) -> str:
        self._counter += 1
        return self._prefix + str(self._counter)

    def match(self, client_id: str) -> bool:
        return client_id.startswith(self._prefix)



