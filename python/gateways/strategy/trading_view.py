import logging
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import collections
import time


class SpreadSignalGraph:
    """A stock trading visualization using matplotlib made to render """
    def __init__(self, width=200, spread_abs_max=10):
        # collections to hold data
        self._ask_spreads = collections.deque(np.zeros(width))
        self._bid_spreads = collections.deque(np.zeros(width))
        self._signals = collections.deque(np.zeros(width))

        self._reference_bid = None
        self._reference_ask = None
        self._target_bid = None
        self._target_ask = None

        self._spread_abs_max = spread_abs_max

        # define and adjust figure
        self._fig = plt.figure(facecolor='#121416')
        gs = self._fig.add_gridspec(6, 12)

        self._spreads_ax = self._fig.add_subplot(gs[0:3, 0:12])
        self._signals_ax = self._fig.add_subplot(gs[4:6, 0:12])

        plt.ion()
        plt.show()

    def _figure_design(self, ax, ymin=-1, ymax=1):
        ax.set_facecolor('#091217')
        ax.tick_params(axis='both', labelsize=10, colors='white')
        ax.ticklabel_format(useOffset=False)
        ax.spines['bottom'].set_color('#808080')
        ax.spines['top'].set_color('#808080')
        ax.spines['left'].set_color('#808080')
        ax.spines['right'].set_color('#808080')

        leg = ax.legend(loc='upper left', facecolor='#121416', fontsize=8)
        for text in leg.get_texts():
            plt.setp(text, color='w')

        ax.set_ylim(ymin=ymin, ymax=ymax)

        # a horizon line at y=0 axis
        ax.axhline(y=0, linewidth=0.5, color='#808080')

    def add_data(self,
                 ask_spread: float,
                 bid_spread: float,
                 signal: int,
                 reference_bid=0,
                 reference_ask=0,
                 target_bid=0,
                 target_ask=0):

        # append data
        self._ask_spreads.popleft()
        self._ask_spreads.append(ask_spread)

        self._bid_spreads.popleft()
        self._bid_spreads.append(bid_spread)

        self._signals.popleft()
        self._signals.append(signal)

        # order book data
        self._reference_bid = reference_bid
        self._reference_ask = reference_ask
        self._target_bid = target_bid
        self._target_ask = target_ask

    def render(self):
        # clear axis
        self._spreads_ax.cla()
        self._signals_ax.cla()

        self._spreads_ax.plot(self._ask_spreads, color='#85bf4b', label='Ask spreads:' + format_float(self._ask_spreads[-1]))
        self._spreads_ax.plot(self._bid_spreads, color='#ED2939', label='Bid spreads:' + format_float(self._bid_spreads[-1]))
        self._figure_design(self._spreads_ax, ymin=-self._spread_abs_max, ymax=self._spread_abs_max)
        self._spreads_ax.set_title(self._get_spread_title(), loc='left', fontsize=12, color='grey')

        self._signals_ax.plot(self._signals, color='orange', label='Signals')
        self._figure_design(self._signals_ax, ymin=-2, ymax=2)

        plt.draw()
        plt.show()
        plt.pause(0.01)

    def _get_spread_title(self):
        return 'RASK:{} TBID:{} - RBID:{} TASK:{}'.format(format_float(self._reference_ask),
                                                          format_float(self._target_bid),
                                                          format_float(self._reference_bid),
                                                          format_float(self._target_ask))


def format_float(value: float) -> str:
    if value:
        return '%1.1f' % value
    else:
        return '-'


if __name__ == '__main__':
    graph = SpreadSignalGraph(300)
    while True:
        random_spread = round(random.uniform(-1, 1) * 10, 2)
        random_signal = random.randint(-1, 1)
        graph.add_data(ask_spread=random_spread, bid_spread=random_spread-2, signal=random_signal)
        graph.render()
        time.sleep(0.1)