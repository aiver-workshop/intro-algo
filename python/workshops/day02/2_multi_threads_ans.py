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

    # start executing both threads
    thread_1.start()
    thread_2.start()

    # wait for both threads to finish
    thread_1.join()
    thread_2.join()

    print('Factorial of 10 = {}'.format(result_1[0]))
    print('Factorial of 15 = {}'.format(result_2[0]))

