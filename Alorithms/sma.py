import numpy as np

def sma(closing_prices, window):
    return np.convolve(closing_prices, np.ones(window) / window, mode='valid')