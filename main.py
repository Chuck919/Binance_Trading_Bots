import sqlite3
import time
import numpy as np
from binance.client import Client
import threading
from decimal import Decimal, ROUND_DOWN


# Binance API credentials
api_key = 'YOUR API KEY'
api_secret = 'YOU API SECRET'

# Initialize Binance client
client = Client(api_key, api_secret, tld='us')

with sqlite3.connect('trading_data.db') as conn:
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TradingOrders (
            order_id INTEGER PRIMARY KEY,
            bot_name TEXT,
            amount REAL,
            price REAL,
            profit REAL DEFAULT 0
        )
    ''')

with sqlite3.connect('trading_data.db') as conn:
  cursor = conn.cursor()

  # Create a table if it doesn't exist
  cursor.execute('''
        CREATE TABLE IF NOT EXISTS GridOrders (
            order_id INTEGER PRIMARY KEY,
            bot_name TEXT,
            orders TEXT,
            bought REAL,
            profit REAL DEFAULT 0.0
        )
    ''')

class PriceUpdater:
    def __init__(self, crypto_bots):
        self.crypto_bots = crypto_bots
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.update_prices)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def get_current_price(self):
        tickers = client.get_all_tickers()
        return tickers

    def update_prices(self):
      while self.running:
        current_price = self.get_current_price()
        for instance in crypto_bots.values():
            instance.price_check(current_price)
        time.sleep(5)

'''
Sample bots_dict:

bots_dict = {

    'AlgoBot 2': {
    'key': 'AlgoBot 2',
    'symbol': 'BTCUSDT',
    'use': 10,
    'Heikin Ashi': 'y',
    'roc': 9,},

    'AlgoBot 3': {
    'key': 'AlgoBot 3',
    'symbol': 'BTCUSDT',
    'use': 10,
    'Heikin Ashi': 'y',
    'rsi': 6,
    'bb': [20, 2],},

    'AlgoBot 4': {'key': 'AlgoBot 4', 'symbol': 'BTCUSDT', 'use': 10, 'Heikin Ashi': 'y', 'macd': [12, 26, 9], 'obv': 'y',},

    'trailingm_2': 
    ['BTCUSDT', 
    '0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2',  
    '0.1,0.1,0.1,0.2,0.2,0.3,0.3,0.4,0.4,0.5,0.5', 
    '0.4', 
    '0.2', 
    '100', 
    '1.1', 
    '11'],
    
    'smartg_1': ['BTCUSDT', 50, 50]   
    }
'''

crypto_bots = {}

for key in bots_dict.keys():
    print(key)

    if 'AlgoBot' in key:
      instance = AlgoBot(bots_dict[key])
    elif 'trailingm' in key:
      instance = TrailingMartBot(key, bots_dict[key])
    elif 'grid' in key:
      instance = GridBot(key, bots_dict[key])
    elif 'smartg' in key:
      instance = SmartGrid(key, bots_dict[key])
    elif 'martingale' in key:
        instance = MartBot(key, bots_dict[key])
    
    crypto_bots[key] = instance
    


price_updater = PriceUpdater(crypto_bots)
print('start')

price_updater.start()