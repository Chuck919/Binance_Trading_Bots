import sqlite3
import time
import numpy as np
from binance.client import Client
import threading
from decimal import Decimal, ROUND_DOWN

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

class Algorithms:
    def __init__(self):
        pass

    def bb(self, closing_prices, window, num_std_devs):
        closing_prices = np.array(closing_prices)
        sma = self.sma(closing_prices, window)

        rolling_sd = np.std(closing_prices[-window:], ddof=0)

        # Calculate the upper and lower Bollinger Bands for the most recent data point
        upper_band = sma[-1] + (num_std_devs * rolling_sd)
        lower_band = sma[-1] - (num_std_devs * rolling_sd)

        return [upper_band, sma[-1], lower_band]

    def sma(self, closing_prices, window):
        return np.convolve(closing_prices, np.ones(window) / window, mode='valid')

    def macd(self, closing_prices, short_window, long_window, signal_window):
        # Calculate Short-Term EMA
        short_ema = self.ema(closing_prices, short_window)

        # Calculate Long-Term EMA
        long_ema = self.ema(closing_prices, long_window)

        # Calculate MACD Line
        macd_line = [short - long for short, long in zip(short_ema, long_ema)]

        # Calculate Signal Line (9-period EMA of MACD)
        signal_line = self.ema(macd_line, signal_window)

        # Calculate MACD Histogram
        macd_histogram = [macd - signal for macd, signal in zip(macd_line, signal_line)]

        return [macd_line, signal_line, macd_histogram]

    def ema(self, data, window):
        alpha = 2 / (window + 1)
        ema = [data[0]]

        for i in range(1, len(data)):
            ema_value = alpha * data[i] + (1 - alpha) * ema[-1]
            ema.append(ema_value)

        return ema

    def roc(self, closing_prices, n):

        current_price = closing_prices[-1]
        price_n_periods_ago = closing_prices[-n]

        roc = ((current_price - price_n_periods_ago) / price_n_periods_ago) * 100

        return roc

    def obv(self, klines):
        obv = []
        prev_obv = 0

        for kline in klines:
            close_price = float(kline[4])
            volume = float(kline[5])

            if close_price > float(kline[3]):  # If the close price is higher than the low price
                prev_obv += volume
            elif close_price < float(kline[2]):  # If the close price is lower than the high price
                prev_obv -= volume

            obv.append(prev_obv)

        return obv

    def rsi(self, closing_prices, window):
        price_changes = np.diff(closing_prices)

        # Calculate gains and losses
        gains = np.where(price_changes > 0, price_changes, 0)
        losses = np.where(price_changes < 0, -price_changes, 0)

        # Calculate average gains and average losses for the specified window
        avg_gains = np.mean(gains[:-window])
        avg_losses = np.mean(losses[:-window])

        # Calculate initial RS (Relative Strength)
        if avg_losses == 0:
            rs = np.inf  # Set RS to positive infinity to avoid division by zero
        else:
            rs = avg_gains / avg_losses

        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))

        return rsi


    def vwap(self, klines, window):
        cumulative_ttp = 0
        cumulative_volume = 0

        for kline in klines[-window:]:
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])

            tp = (high_price + low_price + close_price) / 3  # Typical Price (TP)
            ttp = tp * volume

            cumulative_ttp += ttp
            cumulative_volume += volume

        if cumulative_volume != 0:
            vwap = cumulative_ttp / cumulative_volume
        else:
            vwap = 0  # Set vwap to 0 if cumulative_volume is zero

        return vwap

    def heikin_ashi(self, klines):
        ha_data = []

        ha_open = float(klines[0][1])  # Initial HA-Open is the first open price
        for kline in klines:
            timestamp, open_price, high, low, close, volume, *_ = kline
            open_price, high, low, close, volume = map(float, [open_price, high, low, close, volume])

            ha_close = (open_price + high + low + close) / 4
            ha_data.append([timestamp, ha_open, max(high, ha_close), min(low, ha_close), ha_close, volume])
            ha_open = (ha_open + ha_close) / 2

        return ha_data


class Check:
    def __init__(self):
        self.vwap_prev = None
        self.roc_prev = None
        self.algos = Algorithms()

    def roc_check(self, current_roc):
        #print(f'ROC: {current_roc}')
        #print(self.roc_prev)

        if self.roc_prev is None:
            self.roc_prev = current_roc
            return None

        if self.roc_prev < 0 and current_roc > 0:
            print(f'\n\nROC BUY: {current_roc}\n\n')
            return 'BUY'
        elif self.roc_prev > 0 and current_roc < 0:
            print(f'\n\nROC SELL: {current_roc}\n\n')
            return 'SELL'
        else:
            return None

    def vwap_check(self, vwap, new_price):
        #print(f'VWAP: {vwap}')

        if self.vwap_prev is None:
            self.vwap_prev = "above" if new_price > vwap else "below"
            return None
        if new_price > vwap and self.vwap_prev == "below":
            print(f'\n\nVWAP BUY: {new_price}\n\n')
            self.vwap_prev = "above"
            return 'BUY'
        elif new_price < vwap and self.vwap_prev == "above":
            print(f'\n\nVWAP SELL: {new_price}\n\n')
            self.vwap_prev = "below"
            return 'SELL'
        else:
            return None


    def bb_check(self, bb, new_price):
        #print(f'BB: {bb}')
        if new_price > bb[0]:
            print(f'\n\nBB BUY: {bb}\n\n')
            return 'BUY'
        elif new_price < bb[2]:
            print(f'\n\nBB SELL: {bb}\n\n')
            return 'SELL'
        else: return None

    def sma_check(self, closing_prices, new_price):
        sma5 = self.algos.sma(closing_prices, 5)
        sma8 = self.algos.sma(closing_prices, 8)
        sma13 = self.algos.sma(closing_prices, 13)
        #print(f'SMA: {sma5[-1]}, {sma8[-1]}, {sma13[-1]}')
        if sma5[-1] > sma8[-1] and sma5[-1] > sma13[-1] and new_price > sma5[-1]:
            return 'BUY'
        elif sma5[-1] < sma8[-1] and sma5[-1] < sma13[-1] and new_price < sma5[-1]:
            return 'SELL'
        else:
            return None

    def macd_check(self, macd):
        #print(f'MACD: {macd[2][-2]}, {macd[2][-1]}')
        if macd[2][-2] < 0 and macd[2][-1] > 0:
            print(f'\n\nMACD BUY: {macd[2][-2]}, {macd[2][-1]}\n\n')
            return 'BUY'
        elif macd[2][-2] > 0 and macd[2][-1] < 0:
            print(f'\n\nMACD SELL: {macd[2][-2]}, {macd[2][-1]}\n\n')
            return 'SELL'
        else:
            return None

    def ema_check(self, closing_prices, new_price):
        ema5 = self.algos.ema(closing_prices, 5)
        ema10 = self.algos.ema(closing_prices, 10)
        #print(f'EMA: {ema5[-1]}, {ema10[-1]}')
        if ema5[-1] > ema10[-1] and new_price > ema5[-1]:
            return 'BUY'
        elif ema5[-1] < ema10[-1] and new_price < ema5[-1]:
            return 'SELL'
        else:
            return None


    def obv_check(self, obv):
        #print(f'OBV: {obv[-2]}, {obv[-1]}')
        if obv[-2] >= obv[-1]:
            return 'SELL'
        elif obv[-2] < obv[-1]:
            return 'BUY'


    def rsi_check(self, rsi):
        #print(f'RSI: {rsi}')
        if rsi >= 70:
            print(f'RSI SELL: {rsi}')
            return "SELL"
        elif rsi <= 30:
            print(f'RSI BUY: {rsi}')
            return "BUY"
        else:
            return None