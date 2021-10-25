import sys
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode
import sqlite3


# use API_URL
def GetInfo(pair, API_URL):
    ticker_json = {}
    try:
        url = API_URL + 'ticker/' + pair + '?ignore_invalid=1'
        ticker_json.update(requests.get(url).json())
        return ticker_json
    except:
        sys.exit("GetInfo: ошибка связи с Yobit по API")

def GetTrades(pair, API_URL):
    ticker_json = {}
    try:
        url = API_URL + 'trades/' + pair + '?ignore_invalid=1'
        ticker_json.update(requests.get(url).json())
        return ticker_json[pair]
    except:
        sys.exit("GetTrades: ошибка связи с Yobit по API")