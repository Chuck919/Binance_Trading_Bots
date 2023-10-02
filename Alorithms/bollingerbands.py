import numpy as np
from sma import sma as simple_moving_average

def bb(closing_prices, window, num_std_devs):
    closing_prices = np.array(closing_prices)
    sma = simple_moving_average(closing_prices, window)

    rolling_sd = np.std(closing_prices[-window:], ddof=0)

    # Calculate the upper and lower Bollinger Bands for the most recent data point
    upper_band = sma[-1] + (num_std_devs * rolling_sd)
    lower_band = sma[-1] - (num_std_devs * rolling_sd)

    return [upper_band, sma[-1], lower_band]