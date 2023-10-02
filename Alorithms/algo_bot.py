import sqlite3
import time
import numpy as np
from binance.client import Client
import threading
from decimal import Decimal, ROUND_DOWN
from main import Algorithms
from main import Check


api_key = 'YOUR API KEY'
api_secret = 'YOUR API SECRET'

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
            profit REAL
        )
    ''')
    
interval = Client.KLINE_INTERVAL_1MINUTE  # 1-minute interval
limit = 1000

class AlgoBot:
    def __init__(self, variables):
        self.key = variables['key']
        self.symbol = variables['symbol']
        self.checks = {key: value for index, (key, value) in enumerate(variables.items()) if index >= 4}
        self.signals = {key: None for key in self.checks.keys()}
        self.use = variables['use']
        self.heikin = variables['Heikin Ashi']
        self.bought = None
        self.amount = None
        self.transactions = 0
        self.profit = 0
        self.check 

        self.crash_check()

    def increment_buy_orders(self):
        with sqlite3.connect('trading_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO TradingOrders (bot_name, amount, price)
                VALUES (?, ?, ?)
            ''', (self.key, self.amount, self.bought))

            conn.commit()

    def delete_buy_orders(self):
        with sqlite3.connect('trading_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM TradingOrders WHERE bot_name = ?
            ''', (self.key,))

            cursor.execute('''
                UPDATE TradingOrders
                SET profit = ?
                WHERE bot_name = ?
            ''', (self.profit, self.key))
            conn.commit()

    def get_orders(self):
        with sqlite3.connect('trading_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT amount, price, profit FROM TradingOrders WHERE bot_name = ?
            ''', (self.key,))
            rows = cursor.fetchall()
            return rows

    def crash_check(self):
        try:
            rows = self.get_orders()
            for i in rows:
                self.amount = i[0]
                self.bought = i[1]
                self.profit = i[2]
        except:
            pass

    def recent_order(self, side):
        all_orders = client.get_all_orders(symbol=self.symbol)

        most_recent_order = None
        for order in all_orders:
            if order['side'] == side:
                if most_recent_order is None or order['time'] > most_recent_order['time']:
                    most_recent_order = order

        if order['type'] == 'MARKET':
            executed_qty = float(order['executedQty'])
            quote_qty = float(order['cummulativeQuoteQty'])

            execution_price = quote_qty / executed_qty
            return [quote_qty, execution_price]


    def print_local_variables(self):
        local_vars = self.__dict__
        for var_name, var_value in local_vars.items():
            print(f"{var_name}: {var_value}")

    def main(self, new_price):
        interval = Client.KLINE_INTERVAL_1MINUTE
        limit = 1000

        klines = client.get_historical_klines(symbol, interval, limit=limit)

        if self.heikin == 'y' or self.heikin == 'Y':
            klines = algos.heikin_ashi(klines)

        closing_prices = [float(kline[4]) for kline in klines]
        print(closing_prices[-1])

        if 'macd' in self.checks:
            params = self.checks.get('macd')
            #print(f'macd: {algos.macd(closing_prices, params[0], params[1], params[2])}')
            signal = check.macd_check(algos.macd(closing_prices, params[0], params[1], params[2]))
            self.signals['macd'] = signal

        if 'rsi' in self.checks:
            params = self.checks.get('rsi')
            #print(f'rsi: {algos.rsi(closing_prices, params)}')
            signal = check.rsi_check(algos.rsi(closing_prices, params))
            self.signals['rsi'] = signal

        if 'bb' in self.checks:
            params = self.checks.get('bb')
            #print(f'bb: {algos.bb(closing_prices, params[0], params[1])}')
            signal = check.bb_check(algos.bb(closing_prices, params[0], params[1]), new_price)
            self.signals['bb'] = signal

        if 'obv' in self.checks:
            signal = check.obv_check(algos.obv(klines))
            #print(f'bb: {algos.obv(klines)}')
            self.signals['obv'] = signal

        if 'ema' in self.checks:
            signal = check.ema_check(closing_prices, new_price)
            #print(f'bb: {algos.ema(closing_prices, 20)}')
            self.signals['ema'] = signal

        if 'sma' in self.checks:
            signal = check.sma_check(closing_prices, new_price)
            #print(f'sma: {algos.sma(closing_prices, 20)}')
            self.signals['sma'] = signal

        if 'roc' in self.checks:
            params = self.checks.get('roc')
            signal = check.roc_check(algos.roc(closing_prices, params))
            #print(f'roc: {algos.roc(closing_prices, params)}')
            self.signals['roc'] = signal

        if 'vwap' in self.checks:
            params = self.checks.get('vwap')
            signal = check.vwap_check(algos.vwap(klines, params), new_price)
            #print(f'vwap: {algos.vwap(klines)}')
            self.signals['vwap'] = signal

        print(self.signals)

        unique_values = set(self.signals.values())
        if len(unique_values) == 1 and 'BUY' in unique_values and self.bought == None:
            self.buy_order(new_price)

        elif len(unique_values) == 1 and 'SELL' in unique_values and self.bought == None:
            self.sell_order(new_price)

        else:
            pass


    def buy_order(self, new_price):
        buy_order = client.order_market_buy(symbol=self.symbol, quantity=float(Decimal(self.use / new_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))

        order_details = self.recent_order('BUY')

        self.amount = order_details[0] # * (1 -  buying fee)
        self.bought = order_details[1]

        self.increment_buy_orders()

    def sell_order(self, new_price):
        sell_order = client.order_market_sell(symbol = self.symbol, quantity = self.amount)
        self.transactions += 1

        round_profit = ((new_price - self.bought) * self.amount / self.bought) #* (1 - selling fee)

        self.profit += round_profit
        self.use += self.profit
        self.bought = None

        self.delete_buy_orders()


    def price_check(self, tickers):
        for ticker in tickers:
            symbol_check = ticker['symbol']
            if symbol_check == self.symbol:
                new_price = float(ticker['price'])
        self.main(new_price)