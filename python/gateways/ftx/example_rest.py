import requests

# https://docs.ftx.com/#markets
# To get static information such as price and size increment
URL = 'https://ftx.com/api'
resp = requests.get(URL + '/markets')
print(resp.text)