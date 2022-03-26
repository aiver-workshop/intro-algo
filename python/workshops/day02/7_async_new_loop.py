"""
By default, asyncio.run() executes the coroutines in the current main thread.

We are going to create a new thread to runs the coroutines.

"""
import logging
import random
import sys
import asyncio
import time
from threading import Thread


def start():
    loop_thread = Thread(target=run_async_task, daemon=True, name='Async Thread')
    loop_thread.start()


def run_async_task():
    # create a new event loop to run task by the calling thread
    loop = asyncio.new_event_loop()

    # create task and add it to the event loop
    loop.create_task(print_forever())

    # run the event loop until stop() is called
    loop.run_forever()


# TODO define a coroutine that continuously print a random number once a second in a while loop
async def print_forever():
    pass

if __name__ == '__main__':
    # logging settings
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    handler.setFormatter(logFormatter)
    root.addHandler(handler)

    # start the background task
    start()
    while True:
        time.sleep(5)
        logging.info('sanity check')

