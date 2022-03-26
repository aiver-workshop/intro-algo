"""
In a process, threading allows multiple tasks to execute concurrently, i.e. appear to run simultaneously

Threading uses a technique called pre-emptive multitasking where the operating system knows about each thread
and can temporarily interrupt (i.e. pause) and resume the execution of any threads "at any time".


Further readings:
https://realpython.com/python-gil/

"""
import time
import datetime
from threading import Thread


# a factorial method similar to exercise 1, but return the result via a result placeholder
def factorial(n: int, result: [int]):
    _result = 1
    print("Started calculation for n=" + str(n))
    for i in range(1, n+1):
        # sleep for a second - release the GIL, allowing other threads to run
        time.sleep(1)

        print('[{}][{}] counter = {}'.format(datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S"), n, i))

        # multiply factorial value
        _result = _result * i

    result[0] = _result


# to demonstrate two threads computing in parallel
if __name__ == '__main__':
    result_1 = [None] * 1
    thread_1 = Thread(target=factorial, args=(10, result_1))

    result_2 = [None] * 1
    thread_2 = Thread(target=factorial, args=(15, result_2))

    # TODO start executing both threads

    # TODO wait for both threads to finish

    print('Factorial of 10 = {}'.format(result_1[0]))
    print('Factorial of 15 = {}'.format(result_2[0]))

