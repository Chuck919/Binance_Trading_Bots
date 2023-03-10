# Binance_Trading_Bots

This is a Python trading bot that uses Binance API to automate a trailing martingale trading strategy. The bot is designed to work with Binance cryptocurrency exchange. I hope to make additional trading strategies in the future, but for now, I'm running the martingale trading strategy.
This bot was also designed to be ran on Pythonanywhere, therefore some features can be improved if ran on a local server (such as using Websockets).

## Disclaimer
This bot is for educational purposes only and should not be used with real money without proper testing and risk management. The developers of this bot are not responsible for any losses incurred while using this bot. Use at your own risk.

## Set up
Install python-binance library:
`pip install python-binance`

Create a binance account and click on your profile and select API management. You can then create a label key for your API (useful if you're going to use more than one API) and then your API key and API secret will be created after verification. **Keep in mind that this is the only time your API secret will be available, so make sure to save it somewhere.** 

Make sure to enable trading and it is also recommended to restrict your IP for safety. Copy and paste your API key to the first line of API.txt and your API secret to the second line, and you should be good to go!

The following is also a very helpful resource: [Binance Python API A Step-By-Step Guide](https://algotrading101.com/learn/binance-python-api-guide/)

### Inputs
Open the [variables.txt](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/variables.txt), and enter the following information:

`Coin Pair:` Enter the trading pair (e.g. ETHUSDT, BTCBUSD, etc)

`Price Scale(%): ` Enter the change in percentage you want the price to decrease before buying another order (e.g. if you put 5%, the bot will wait until the price has decreased 5% before buying another order)

`Rebounce(%): ` Enter the change in percentage you want the price to come up to, or "trail," before buying another order (e.g. If the price scale is 5% and rebounce is 1%, the bot will wait until the price drops by 5% and then wait until the price rebounds by 1% before buying)

`Take Profit(%): ` Enter the amount of profit in percentage to the amount of money you input that you want to earn each round (e.g. if you put $100 into the bot and want to earn $1 each round, then the Take Profit % would be 1)

`Trailing(%): ` Enter the change in percentage you want the price to decrease to, or "trail," before selling (similar to rebounce, but for selling)

`Stable Coin Amount to Use: ` Enter the amount you want to trade with (e.g. if the trading pair is ETHUSDT, then enter USDT amount you want the bot to use)

`Volume Scale: ` Enter the amount you want the buy orders to increase by as the price drops

`Orders: ` Enter the amount of safety orders (i.e. how many times the bot will buy)

This resources probably explains the terms better than I do: [Martingale Bot - Trailing Mode](https://www.pionex.com/blog/martingale-bot-trailing-mode/)

## The Bot
### main.py
The [main.py](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/main.py) will first create a `client` object using your API key and API secret code with the following code: `client=Client(api_key,api_secret, tld='us')` 

Keep in mind that the `tld='us'` portion of the code is only needed if you are using Binance.US, otherwise just omit that part.

### trading_bots.py
The [trading_bots.py](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/trading_bots.py) is where the bulk of the code is actually stored. Although I only have the martingale bot created right now, I intend to add more in the future and this setup will streamline that process.

The bot will first retrieve all the information from the [variables.txt](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/variables.txt) file and assign a variable to each of them. It will also keep track of your `round_profit` (profit made each time a sell is executed), `total_profit`, and `transactions` (each sell or round). The total profit is also stored in the [profit_log.txt](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/profit_log.txt) file so that it will still keep track of your total profit even if the bot crashes or Pythonanywhere resets. It will then use the **Volume Scale**, **Stable Coin Amount to Use**, and **Orders** to determine the `volume_list` (how much to buy for each buy order). It will also then check the information inside the [buy_orders.txt](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/buy_orders.txt) file to determine the most recent price that it bought at, amount that it bought, and the order amount as another way to protect against crashing.

The majority of the bot runs inside a `while True:` loop and gets the most recent price using the following code: 

`recent_price_chart = client.get_symbol_ticker(symbol=symbol)`
 
`recent_price = float(recent_price_chart['price'])`

**This process could be done a lot smoother and faster using the Python Binance Websocket with `from binance import ThreadedWebsocketManager`, but sadly because this code was meant to run on Pythonanywhere, websockets can't be used**

Every time the bot buys a order, it will be recorded into the [buy_orders.txt](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/buy_orders.txt) file, and each time a sell is made, the `round_profit`  `total_profit`, and `transactions` will be printed on the console, and the `total_profit` will be recorded into the [profit_log.txt](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/profit_log.txt) file.

## Logic/ How It Works
### Trailing Buys
The bot will automatically buy the first order and then constantly check and update the `recent_price` from Binance with a `time.sleep(0.5)` (waits 0.5 seconds before updating the price again) to prevent violating Binance API request limits. When the price has dropped below the price threshold (which is calculated using `price_bought[-1]*(1-scale/100)` i.e. the most recent price and price scale), the trailing buy is triggered. The bot will then compare the `recent_price` to the `recent_price_trailing_buy`. If the price is decreasing, then the bot will update the `recent_price` to the newest price, but if the price is increasing, then the `recent_price` remains the same. If the price goes above the **Rebounce** threshold, then the bot will trigger a buy using the following code: 

`buy_order = client.order_market_buy(symbol=symbol, quantity=round(volume_list[bought]/recent_price_trailing_buy, 4))`

It will then record the `price_bought` and `amount_bought` into the [buy_orders.txt](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/buy_orders.txt) file and start the process again.

### Trailing Sells
If the price goes above the **Take Profit** threshold, then the trailing sell is triggered and the process is similar to the trailing buys process, just reversed. The bot will then place a sell order using the following code:

`ell_order = client.order_market_sell(symbol = symbol, quantity = free_symbol_balance)`

It will then print the `round_profit`, `total_profit`, and `transactions` on the console, and the `total_profit` will be recorded into the [profit_log.txt](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/profit_log.txt) file and reset the bot to start another round.

# Happy Trading!

