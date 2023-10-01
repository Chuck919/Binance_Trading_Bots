import sqlite3
from binance.client import Client
from decimal import Decimal, ROUND_DOWN
import json

'''
Sample input:

bots_dict = {
    'smart_grid_1' : ['BTCUSDT', 50, 50].
    'smart_grid_2' : ['ETHUSDT', 25, 50]
    }

'''

#gets binance information
api_key = 'YOUR API KEY'
api_secret = 'YOUR API SECRET'
client = Client (api_key, api_secret, tld='us')

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

class GridBot:
    def __init__(self, key, variables):
        self.key = key
        self.symbol = variables[0]
        self.total_budget = variables[1]
        self.step = variables[2]
        self.orders = []
        self.profit = 0.0
        self.threshold = None
        self.bought = 0

        self.create_data()

        self.crash_check()

        self.print_local_variables()

    def create_data(self):
        with sqlite3.connect('trading_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT bot_name FROM GridOrders WHERE bot_name = ?', (self.key,))
            existing_record = cursor.fetchone()

        if existing_record:
            pass
        else:
            with sqlite3.connect('trading_data.db') as conn:
                cursor = conn.cursor()
                # Serialize the list 'self.orders' to JSON before storing it
                orders_json = json.dumps(self.orders)
                cursor.execute('''
                    INSERT INTO GridOrders (bot_name, orders, bought, profit)
                    VALUES (?, ?, ?, ?)
                ''', (self.key, orders_json, self.bought, self.profit))
                conn.commit()

    def store_data(self):
        try:
            with sqlite3.connect('trading_data.db') as conn:
                cursor = conn.cursor()
                # Serialize the list 'self.orders' to JSON before storing it
                orders_json = json.dumps(self.orders)
                cursor.execute('''
                    UPDATE GridOrders
                    SET orders = ?,
                        bought = ?,
                        profit = ?
                    WHERE bot_name = ?
                ''', (orders_json, self.bought, self.profit, self.key))
                conn.commit()  # Commit the changes
        except sqlite3.Error as e:
            print("SQLite error:", e)
        except Exception as e:
            print("Error:", e)

    def get_orders(self):
        with sqlite3.connect('trading_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT orders, bought, profit FROM GridOrders WHERE bot_name = ?
            ''', (self.key,))
            rows = cursor.fetchone()  # Use 'fetchone' since there should be only one row
            return rows


    def crash_check(self):
        try:
            rows = self.get_orders()
            orders_json, self.bought, self.profit = rows
            self.orders = json.loads(orders_json)
            self.print_local_variables()
            print('check')
        except:
            pass


    def place_buy_order(self, price):
        buy_order = client.create_order(
        symbol=self.symbol,
        side='BUY',
        type='LIMIT',
        timeInForce='GTC',  # Good 'Til Canceled
        quantity=0.0001,
        price=price)

        order_id = buy_order['orderId']

        self.orders.append(order_id)

    def print_local_variables(self):
        local_vars = self.__dict__
        for var_name, var_value in local_vars.items():
          print(f"{var_name}: {var_value}")

    def place_sell_order(self, price):
        sell_order = client.create_order(
        symbol=self.symbol,
        side='SELL',
        type='LIMIT',
        timeInForce='GTC',
        quantity=0.0001,
        price=price)

        order_id = sell_order['orderId']

        self.orders.append(order_id)



    def cancel_orders(self, price):
        self.print_local_variables()
        for i in self.orders:
            order_info = client.get_order(symbol=self.symbol, orderId=i)
            if order_info['status'] == 'NEW' or order_info['status'] == 'PARTIALLY_FILLED':
                cancel_response = client.cancel_order(symbol=self.symbol, orderId=i)
            else:
                if order_info['side'] == 'BUY':
                    self.bought += 1
                    print('bought')
                elif order_info['side'] == 'SELL':
                    self.bought -= 1
                    print('sold')
                    self.profit += self.step/price
                    print(self.profit)

        self.orders = []

        self.store_data()

    def place_orders(self):
        if self.bought >= 1:
            self.place_sell_order(float(Decimal(self.threshold + self.step).quantize(Decimal('0.01'), rounding=ROUND_DOWN)))
        elif self.bought >= 2:
            self.place_sell_order(float(Decimal(self.threshold + 2 * self.step).quantize(Decimal('0.01'), rounding=ROUND_DOWN)))

        self.place_buy_order(float(Decimal(self.threshold - self.step).quantize(Decimal('0.01'), rounding=ROUND_DOWN)))
        self.place_buy_order(float(Decimal(self.threshold - 2 * self.step).quantize(Decimal('0.01'), rounding=ROUND_DOWN)))

        self.store_data()

    def main(self, new_price):

        if new_price*0.0001*(self.bought + len(self.orders)) > self.total_budget:
            pass

        elif self.bought == 0:
            buy_order = client.order_market_buy(symbol=self.symbol, quantity=0.0001)
            self.bought += 1
            self.store_data()
            self.threshold = new_price
            self.place_orders()
            print(self.get_orders())

        elif self.threshold == None:
            self.threshold = new_price

        elif new_price > self.threshold + self.step and new_price < self.threshold + 2*self.step:
            self.threshold += self.step
            self.cancel_orders(new_price)
            self.place_orders()

        elif new_price < self.threshold - self.step and new_price > self.threshold - 2*self.step:
            self.threshold = None
            self.cancel_orders(new_price)
            self.place_orders()

        elif new_price > self.threshold + 2*self.step or new_price < self.threshold - 2*self.step:
            self.threshold = None
            self.cancel_orders(new_price)

        else:
            pass



    def price_check(self, tickers):
        for ticker in tickers:
            symbol_check = ticker['symbol']
            if symbol_check == self.symbol:
                new_price = float(ticker['price'])
        self.main(new_price)



