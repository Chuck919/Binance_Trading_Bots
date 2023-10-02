def ema(data, window):
    alpha = 2 / (window + 1)
    ema = [data[0]]

    for i in range(1, len(data)):
        ema_value = alpha * data[i] + (1 - alpha) * ema[-1]
        ema.append(ema_value)

    return ema