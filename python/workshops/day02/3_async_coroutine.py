"""
Asynchronous programming allows us to define non-blocking methods to run more codes concurrently.
A non-blocking method contains section of codes (usually I/O such as file access or API calls)
where it provides opportunity for other codes to run whilst awaiting for a response/result.

asyncio is the Python module to facilitate asynchronous programming.

Compared to threading which uses pre-emptive multitasking, asyncio uses cooperative multitasking.
The tasks must cooperate by announcing when  they are ready to be switched out, hence more syntax like async/await
are needed to make this happen.

"""
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
    # TODO run and print result from fetch_data()

    # run a coroutine
    data = asyncio.run(fetch_data_async())
    print(data)




