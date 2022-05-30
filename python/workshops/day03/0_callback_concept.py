import time
import random


# a callback - a method that is invoked when there is an event or data
def handle_number(number):
    if number < 50:
        print('Sending a buy order: ' + str(number))
    else:
        # simulate a bug
        b = 1/0


def handle_number_2(number):
    print(number * 2)


# registering the callback
# would be good to do some sanity check of the method signature
callback_method = handle_number

ok_flag = False

while True:
    time.sleep(1)

    # check flag to see if reconnection is needed
    if not ok_flag:
        print('Going to reconnect')
        ok_flag = True

    # assume this random number comes from a "source" - it could be an exchange
    # equivalent websocket receiving messages
    a = random.randint(1, 100)

    if callback_method:
        try:
            # if a callback method is registered, invoke/notify it
            callback_method(a)
        except:
            print("An exception occurred")
            # raise a flag to indicate that we should reconnect
            ok_flag = False
    else:
        print('no callback registered')

