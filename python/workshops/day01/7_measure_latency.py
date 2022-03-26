"""
Create a class to measure the average time lapsed between mark() calls
This is useful to measure how frequent is the price update (i.e. we call mark() method on every price update)

"""
import time
import random


class LatencyMetric:
    def __init__(self):
        # TODO create variable to keep track of sum, count, max
        self._last_received_timestamp = time.time_ns()
        pass

    def mark(self):
        # TODO calculate time lapsed between now and last updated time, in nanoseconds
        pass

    def get_max(self) -> int:
        # TODO get max period
        pass

    def get_mean(self) -> int:
        # TODO get mean in milliseconds
        pass


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