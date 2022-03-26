"""
A synchronous call invokes a method, wait for it to completes execution before returning a result to the caller.
No other method can run during the execution of the method.

A method is synchronous by default

"""
import time
import datetime


# define a method to calculate factorial, and sleep for 1 second during each multiply step
def factorial(n: int) -> int:
    _result = 1
    print("Started calculation for n=" + str(n))
    for i in range(1, n+1):
        # sleep for a second
        time.sleep(1)

        print('[{}][{}] counter = {}'.format(datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S"), n, i))

        # multiply factorial value
        _result = _result * i

    return _result


# we run the method twice, and note that the method executes sequentially requiring 25 (10 + 15) seconds in total
if __name__ == '__main__':
    print('Factorial of 10 = {}'.format(factorial(10)))
    print('Factorial of 15 = {}'.format(factorial(15)))
