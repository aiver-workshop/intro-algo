import asyncio
import time


# a normal (synchronous) method
def fetch_data():
    for i in range(3):
        print("[sync] fetching data " + str(i))
        time.sleep(1)
    return "data_a"


# a coroutine is a method with async keyword to indicate that its execution can be suspended before reaching return
# places where it can be suspended are the await statement
async def fetch_data_async():
    for i in range(3):
        print("[asyncio] fetching data " + str(i))
        await asyncio.sleep(1)
    return "data_b"


if __name__ == '__main__':
    data = fetch_data()
    print(data)

    # run a coroutine
    data = asyncio.run(fetch_data_async())
    print(data)