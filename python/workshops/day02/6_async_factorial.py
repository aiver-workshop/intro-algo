"""
We rewrite the factorial function in an async manner, and uses gather() as a shorter way of creating and await on tasks

"""

import asyncio
import datetime


# an async version of factorial method with an internal sleep
async def factorial(n: int) -> int:
    _result = 1
    print("Started calculation for n=" + str(n))
    for i in range(1, n+1):
        # TODO sleep for 1 second

        print('[{}][{}] counter = {}'.format(datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S"), n, i))

        # multiply factorial value
        _result = _result * i

    return _result


async def concurrent_calculation() -> []:
    # schedule two calls to run concurrently
    results = await asyncio.gather(factorial(10), factorial(15))

    # print the results
    print('Factorial of 10 = {}'.format(results[0]))
    print('Factorial of 15 = {}'.format(results[1]))

if __name__ == '__main__':
    asyncio.run(concurrent_calculation())
