"""
To run multiple coroutines concurrently, wrap the coroutines in a task and await on them to finish.

"""
import sys
import logging
import asyncio


async def cut_ingredients():
    logging.info("Cutting ingredients...")
    await asyncio.sleep(2)
    logging.info("Finished cutting ingredients")


async def cook_food():
    logging.info("Cooking food...")
    await asyncio.sleep(5)
    logging.info("Finished cooking food")


async def prepare_dessert():
    logging.info("Preparing dessert...")
    await asyncio.sleep(10)
    logging.info("Finished preparing dessert")


async def cook():
    logging.info("Start cooking...")

    # a task signal to asyncio to run the method as soon as it can
    task_1 = asyncio.create_task(cut_ingredients())
    task_2 = asyncio.create_task(cook_food())
    task_3 = asyncio.create_task(prepare_dessert())

    # await for tasks to complete
    await task_1
    await task_2
    await task_3

    logging.info("Finished cooking")

if __name__ == '__main__':
    # logging settings
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    handler.setFormatter(logFormatter)
    root.addHandler(handler)

    # run the async function by main thread
    asyncio.run(cook())
