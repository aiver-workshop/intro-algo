"""
Create a class to measure the average time lapsed between mark() calls
This is useful to measure how frequent is the price update (i.e. we call mark() method on every price update)

"""
import time
import random


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


# A simple driver class to demonstrate the usage
if __name__ == '__main__':
    metric = LatencyMetric()

    while True:
        # a random time between 0.9 and 1.1 seconds
        random_duration = float(random.randint(90, 110)) / 100.0
        time.sleep(random_duration)
        metric.mark()

        # we expect to print an average time of ~1 second
        print('Average: {}, max: {}'.format(metric.get_mean(), metric.get_max()))

