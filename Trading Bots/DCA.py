class DCABot:
    def __init__(self, key, variables):
        self.key = key
        self.symbol = variables[0]
        self.original_amount = variables[1]
        self.amount = self.original_amount
        self.buys = variables[3]
        a, b = variables[4].split(' ')
        
        if b == 'sec':
            self.interval = a
        
        elif b == 'min':
            interval = a*60
            
        elif b == 'hours':
            interval = a*60*60
            
        elif b == 'days':
            interval = a*60*60*24
        
        elif b == 'weeks':
            interval = a*60*60*24*7
            
        self.interval = interval
        self.original_interval = self.intervals

    def buy_order(self, price):
        buy_amount = (self.amount/self.buys)/price
        buy_order = client.order_market_buy(symbol=self.symbol, quantity=float(Decimal(buy_amount).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))
        self.amount -= buy_amount
        self.buys -= 1
        if self.amount <= 0 or self.buys == 0:
            self.stop_bot
            
        print(f'BOUGHT. {self.amount} left')
        
    def main(self, new_price):
        if self.interval <= 0:
            self.buy_order(new_price)
            self.amount = self.original.amount
            self.interval = self.original_interval
        
        else:
            self.interval -= 5
            
    def stop_bot(self):
        global crypto_bots
        crypto_bots.pop(self.key)
        print(crypto_bots)
        print(f'bot {self.key} stopped')

    def price_check(self, tickers):
        with self.lock:
            for ticker in tickers:
                symbol_check = ticker['symbol']
                if symbol_check == self.symbol:
                    new_price = float(ticker['price'])
        self.main(new_price)
