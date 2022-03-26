"""
Make a REST call to FTX exchange to get market static data: https://docs.ftx.com/?python#rest-api

Reference: https://realpython.com/python-requests/

"""
import requests

# Get the URL
URL = 'https://ftx.com/api'

# Specify the end point - https://docs.ftx.com/?python#markets
METHOD = 'markets'

# GET
resp = requests.get(URL + '/' + METHOD)

# print the result
print(resp.text)

# convert to JSON object
message = resp.json()

# get and print the price and size increment of BTC perpetual future
for data in message['result']:
    contract_name = data.get('name')
    if contract_name == 'BTC-PERP':
        price_increment = float(data.get('priceIncrement'))
        size_increment = float(data.get('sizeIncrement'))
        print('BTC-PERP - priceIncrement: {}, sizeIncrement: {}'.format(price_increment, size_increment))
        break


