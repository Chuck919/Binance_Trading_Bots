# Binance_Trading_Bots

These are Python trading bots that use Binance API to automate a specific trading strategy. The bots are designed to work with Binance.US cryptocurrency exchange.
This bot was also designed to be ran on Pythonanywhere with their always on tasks, therefore some features can be improved if ran on a local server or another host (such as using Websockets).

## Disclaimer
These bots are for educational purposes and the developers of these bots are not responsible for any losses incurred while using this bot. Use at your own risk.

## Set up
Install python-binance library:
`pip install python-binance`

Create a binance account and click on your profile and select API management. You can then create a label key for your API (useful if you're going to use more than one API) and then your API key and API secret will be created after verification. **Keep in mind that this is the only time your API secret will be available, so make sure to save it somewhere.** 

Make sure to enable trading and it is also recommended to restrict your IP for safety. Copy and paste your API key to the first line of API.txt and your API secret to the second line, and you should be good to go!

The following is also a very helpful resource: [Binance Python API A Step-By-Step Guide](https://algotrading101.com/learn/binance-python-api-guide/)

It will then print the `round_profit`, `total_profit`, and `transactions` on the console, and the `total_profit` will be recorded into the [profit_log.txt](https://github.com/Chuck919/Binance_Trading_Bots/blob/main/Crypto%20Trading%20Bot/profit_log.txt) file and reset the bot to start another round.

# Happy Trading!

