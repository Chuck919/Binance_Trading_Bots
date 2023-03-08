from binance.client import Client
import linecache
import time
from trading_bots import martingale_bot


api_key = linecache.getline('API.txt', 1).strip()
api_secret = linecache.getline('API.txt', 2).strip()

client=Client(api_key,api_secret, tld='us')


martingale_bot(client)
