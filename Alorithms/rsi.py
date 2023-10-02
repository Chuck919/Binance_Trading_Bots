import numpy as np

def rsi(closing_prices, window):
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