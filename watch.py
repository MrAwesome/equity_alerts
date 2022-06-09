#!/usr/bin/env python3

import requests
import sys
from pprint import pprint
from tda import auth, client

from secrets import TDA_CLIENT_ID, TEXTBELT_API_KEY, PHONE_NUM

TOK_PATH = 'tda_token.json'
API_KEY = f'{TDA_CLIENT_ID}@AMER.OAUTHAP'
REDIRECT_URI = 'http://localhost'

def tda_auth():
    try:
        c = auth.client_from_token_file(TOK_PATH, API_KEY)
    except FileNotFoundError:
        from selenium import webdriver
        with webdriver.Chrome() as driver:
            c = auth.client_from_login_flow(driver, API_KEY, REDIRECT_URI, TOK_PATH)

    return c

try:
    c = tda_auth()

    tickerfile = open("prices.txt", "r")
    tickerlines = tickerfile.read().strip().split("\n")
    tickerfile.close()

    info = {l: {"target_price": float(r)} for [l, r] in [x.split(" ") for x in tickerlines]}

    cryptonames = ['BTC']

    tickers = [x for x in info if x not in cryptonames]
    cryptos = [x for x in info if x in cryptonames]

    resp = c.get_quotes(tickers).json()

    cryp = requests.get('https://production.api.coindesk.com/v2/tb/price/ticker?assets='+",".join(cryptos)).json()

    for crypto in cryptos:
        info[crypto]['current_price'] = cryp['data'][crypto]['ohlc']['c']


    for ticker in tickers:
        info[ticker]['current_price'] = resp[ticker]['mark']


    for (ticker, data) in info.items():
        current_price = data['current_price']
        target_price = data['target_price']
        data['under'] = current_price < target_price

    under = [t for t in info if info[t]['under']]
    not_under = [t for t in info if not info[t]['under']]

    if len(under) > 0:
        msg = "\n".join([t + ": " + str(info[t]['current_price']) for t in under])
        requests.post('https://textbelt.com/text', {
            'phone': str(PHONE_NUM),
            #TODO: urlencode
            'message': '⚠️ PRICE ALERT! ⚠️\n' + msg,
            'key': TEXTBELT_API_KEY,
            })

    newcontents = "\n".join([t + " " + str(info[t]['target_price']) for t in not_under])
    tickerwrite = open("prices.txt", "w")
    tickerwrite.write(newcontents)
    tickerwrite.close()
except Exception as e:
    requests.post('https://textbelt.com/text', {
        'phone': PHONE_NUM,
        'message': 'Error in price script!',
        'key': TEXTBELT_API_KEY,
        })
    sys.exit(1)
