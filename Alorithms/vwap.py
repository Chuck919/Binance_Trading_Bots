def vwap(klines, window):
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
