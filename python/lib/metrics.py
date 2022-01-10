import time


class LatencyMetric:
    def __init__(self):
        self._last_received_timestamp = time.time_ns()
        self._max_duration = 0
        self._sum = 0
        self._count = 0

    def mark(self):
        # calculate time lapsed
        ts = time.time_ns()
        duration = ts - self._last_received_timestamp
        self._last_received_timestamp = ts

        self._sum += duration
        self._count += 1

        if duration > self._max_duration:
            self._max_duration = duration

    def get_max(self) -> int:
        return self._max_duration

    def get_mean(self) -> int:
        """ get mean in milliseconds """
        return self._sum / self._count / 1000000

    def get_total_ns(self) -> int:
        return self._sum

    def get_total_ms(self) -> int:
        return self._sum / 1000000


class Timer:
    def __init__(self):
        self._sum = 0
        self._count = 0
        self._start = 0

    def start(self):
        self._start = time.time_ns()

    def finish(self):
        duration = time.time_ns() - self._start
        self._sum += duration
        self._count += 1

    def get_mean(self) -> int:
        """ get mean in milliseconds """
        return self._sum / self._count / 1000000