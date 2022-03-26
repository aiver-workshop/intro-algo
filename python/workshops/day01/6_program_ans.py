"""
Write a simple program that prints a number from 1 to 20 once per second

"""
import time

if __name__ == '__main__':
    for i in range(1, 21):
        print(i)
        time.sleep(1)
