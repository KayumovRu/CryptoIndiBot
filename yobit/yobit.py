import sys
import os
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode
import sqlite3


def YobitAPI():
    API_URL = 'https://yobit.net/api/3/'
    TAPI_URL = 'https://yobit.net/tapi/'

    # reading the key and secret from a file
    curdir = os.path.dirname(os.path.abspath(__file__)) # used if there are problems with displaying the progress bar below
    try:
        f = open(curdir + '\key.txt', 'w+')
        key_list = f.read().splitlines()
        KEY = key_list[0]
        SECRET = key_list[1]
        return API_URL, TAPI_URL, KEY, SECRET
    except:
        sys.exit("Key reading error. Check the file key.txt")

# use API_URL
def GetRate(pair, API_URL):
    ticker_json = {}
    try:
        url = API_URL + 'ticker/' + pair + '?ignore_invalid=1'
        ticker_json.update(requests.get(url).json())
        return ticker_json
    except:
        sys.exit("GET (ticker) request error. Check that the site is available.")