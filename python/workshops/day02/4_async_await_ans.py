"""
In Python asyncio, we can await on coroutines and tasks.

Awaiting on coroutines to run the methods sequentially.
Awaiting on tasks to run the methods concurrently (next exercise)

"""
import asyncio


async def cut_ingredients():
    print("Cutting ingredients...")
    await asyncio.sleep(2)
    print("Finished cutting ingredients")


# TODO copy code from above and change the print
async def cook_food():
    print("Cooking food...")
    await asyncio.sleep(2)
    print("Finished cooking food")


# TODO copy code from above and change the print
async def prepare_dessert():
    print("Preparing dessert...")
    await asyncio.sleep(2)
    print("Finished preparing dessert")


async def cook():
    await cut_ingredients()
    await cook_food()
    await prepare_dessert()


if __name__ == '__main__':
    # run the async function by main thread
    asyncio.run(cook())
