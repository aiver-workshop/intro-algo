"""
Make a REST call to FTX exchange to get market static data: https://docs.ftx.com/?python#rest-api

Reference: https://realpython.com/python-requests/

"""
import requests

# Get the URL
URL = ''        # TODO

# Specify the end point - https://docs.ftx.com/?python#markets
METHOD = ''     # TODO

# GET
resp = requests.get(URL + '/' + METHOD)

# print the result
# TODO

# convert to JSON object
# TODO

# get and print the price and size increment of BTC perpetual future
# TODO

