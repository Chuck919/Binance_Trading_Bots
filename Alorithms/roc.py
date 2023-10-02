def roc(closing_prices, n):

    current_price = closing_prices[-1]
    price_n_periods_ago = closing_prices[-n]

    roc = ((current_price - price_n_periods_ago) / price_n_periods_ago) * 100

    return roc