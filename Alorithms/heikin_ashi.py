def heikin_ashi(klines):
    ha_data = []

    ha_open = float(klines[0][1])  # Initial HA-Open is the first open price
    for kline in klines:
        timestamp, open_price, high, low, close, volume, *_ = kline
        open_price, high, low, close, volume = map(float, [open_price, high, low, close, volume])

        ha_close = (open_price + high + low + close) / 4
        ha_data.append([timestamp, ha_open, max(high, ha_close), min(low, ha_close), ha_close, volume])
        ha_open = (ha_open + ha_close) / 2

    return ha_data