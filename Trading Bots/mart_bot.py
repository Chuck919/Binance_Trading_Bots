import time
import sqlite3
import threading
from binance.client import Client
from decimal import Decimal, ROUND_DOWN

'''
Sample input:

bots_dict = {
'trailingm_1': ['ETHUSDT', '0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2',  '0.4', '100', '1.1', '11'],
'trailingm_2': ['BTCUSDT', '0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2', '0.4', '100', '1.1', '11']
    
}



'''

#gets binance information
api_key = 'YOUR API KEY'
api_secret = 'YOUR API SECRET'
client = Client (api_key, api_secret, tld='us')

# Create the database if it doesn't exist
with sqlite3.connect('trading_data.db') as conn:
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TradingOrders (
            order_id INTEGER PRIMARY KEY,
            bot_name TEXT,
            amount REAL,
            price REAL
        )
    ''')

class MartBot:
    def __init__(self, key, variables):
        self.key = key
        self.total_profit = 0
        self.transactions = 0
        self.sell_price = None
        self.symbol = variables[0]
        self.profit = float(variables[3])

        string_scale = variables[1].split(',')
        self.scale = [float(i) for i in string_scale]

        self.volume_list = []
        self.volume = float(variables[6])
        self.orders = int(variables[7])
        self.use = float(variables[5])
        series_sum = (1-self.volume**self.orders)/(1-self.volume)
        x = (self.use + self.total_profit)/ series_sum
        for i in range(self.orders):
            self.volume_list.append(x*self.volume**i)

        self.price_bought = []
        self.amount_bought = []
        self.bought = 0

        self.buying = False
        self.selling = False


        self.lock = threading.Lock()  # Lock for thread-safe printing

        self.crash_check()

    def print_local_variables(self):
        local_vars = self.__dict__
        for var_name, var_value in local_vars.items():
            print(f"{var_name}: {var_value}")

    def increment_buy_orders(self, amount, price):
        with sqlite3.connect('trading_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO TradingOrders (bot_name, amount, price)
                VALUES (?, ?, ?)
            ''', (self.key, amount, price))

            conn.commit()

    def delete_buy_orders(self):
        with sqlite3.connect('trading_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM TradingOrders WHERE bot_name = ?
            ''', (self.key,))

            conn.commit()

    def get_orders(self):
        with sqlite3.connect('trading_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT amount, price FROM TradingOrders WHERE bot_name = ?
            ''', (self.key,))
            rows = cursor.fetchall()
            return rows

    def crash_check(self):
        try:
            rows = self.get_orders()
            for i in rows:
                self.amount_bought.append(i[0])
                self.price_bought.append(i[1])
            self.bought = len(self.price_bought)
            total_cost = 0
            for i in range(len(self.price_bought)):
                total_cost += self.price_bought[i] * self.amount_bought[i]
            self.sell_price = total_cost * (1 + self.profit/100) / sum(self.amount_bought)
        except:
            pass

    def main(self, new_price):
        if self.bought == 0:
            self.buy_order(new_price)

        elif self.bought >= 1 and self.bought < self.orders and new_price <= self.price_bought[-1]*(1-self.scale[self.bought]/100):
            self.buy_order(new_price)

        elif self.bought >= 1 and new_price >= self.sell_price:
            self.sell_order(new_price)

        else:
            pass

    def price_check(self, tickers):
        with self.lock:
            for ticker in tickers:
                symbol_check = ticker['symbol']
                if symbol_check == self.symbol:
                    new_price = float(ticker['price'])
        self.main(new_price)

    def buy_order(self, new_price):
        with self.lock:
            buy_order = client.order_market_buy(symbol=self.symbol, quantity=float(Decimal(self.volume_list[self.bought] / new_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))
            '''
            buy_order = client.create_test_order(
                symbol=self.symbol,
                side='BUY',
                type='MARKET',
                quantity=round(self.volume_list[self.bought]/new_price, 4)
            )'''
        self.price_bought.append(new_price)
        self.amount_bought.append(float(Decimal(self.volume_list[self.bought] / new_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))
        print(self.amount_bought)
        print(self.price_bought)

        total_cost = 0
        for i in range(len(self.price_bought)):
            total_cost += self.price_bought[i] * self.amount_bought[i]
        self.sell_price = total_cost * (1 + self.profit/100) / sum(self.amount_bought)

        self.bought += 1

        self.increment_buy_orders(self.amount_bought[-1], new_price)
        print(f'{self.key} bought')

    def sell_order(self, new_price):
        with self.lock:
            selling_amount = float(Decimal(sum(self.amount_bought)).quantize(Decimal('0.0001'), rounding=ROUND_DOWN))
            sell_order = client.order_market_sell(symbol = self.symbol, quantity = selling_amount)
            '''
                symbol=self.symbol,
                side='SELL',
                type='MARKET',
                quantity=sum(self.amount_bought)
            )'''

        #calculates profit
        total_round_cost = 0
        for i in range(len(self.price_bought)):
            total_round_cost += self.price_bought[i] * self.amount_bought[i]
        round_profit = round(new_price * sum(self.amount_bought) - total_round_cost, 4)
        self.total_profit += round_profit


        self.volume_list = []
        series_sum = (1-self.volume**self.orders)/(1-self.volume)
        x = (self.use + self.total_profit)/ series_sum
        for i in range(self.orders):
            self.volume_list.append(x*self.volume**i)

        self.price_bought = []
        self.amount_bought = []
        self.sell_price = None
        self.bought = 0
        self.transactions += 1
        
        self.delete_buy_orders()
        print(f' {self.key} sold')