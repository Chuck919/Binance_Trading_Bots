import numpy as np
from ema import ema as exponential_moving_average

def macd(closing_prices, short_window, long_window, signal_window):
    # Calculate Short-Term EMA
    short_ema = exponential_moving_average(closing_prices, short_window)

    # Calculate Long-Term EMA
    long_ema = exponential_moving_average(closing_prices, long_window)

    # Calculate MACD Line
    macd_line = [short - long for short, long in zip(short_ema, long_ema)]

    # Calculate Signal Line (9-period EMA of MACD)
    signal_line = exponential_moving_average(macd_line, signal_window)

    # Calculate MACD Histogram
    macd_histogram = [macd - signal for macd, signal in zip(macd_line, signal_line)]

    return [macd_line, signal_line, macd_histogram]