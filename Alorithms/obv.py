def obv(klines):
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