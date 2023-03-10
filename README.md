# Binance_Trading_Bots

This is a Python trading bot that uses Binance API to automate a martingale trading strategy. The bot is designed to work with Binance cryptocurrency exchange.
This bot was also designed to be ran on Pythonanywhere, therefore some features can be improved if ran on a local server (such as using Websockets).

### Disclaimer
This bot is for educational purposes only and should not be used with real money without proper testing and risk management. The developers of this bot are not responsible for any losses incurred while using this bot. Use at your own risk.

### Set up
Install python-binance library:
`pip install python-binance`

Create a binance account and click on your profile and select API management. You can then create a label key for your API (useful if you're going to use more than one API) and then your API key and API secret will be created after verification. **Keep in mind that this is the only time your API secret will be available, so make sure to save it somewhere.** 

Make sure to enable trading and it is also recommended to restrict your IP for safety. Copy and paste your API key to the first line of API.txt and your API secret to the second line, and you should be good to go!

The following is also a very helpful resource: [Binance Python API A Step-By-Step Guide](https://algotrading101.com/learn/binance-python-api-guide/)

### Inputs
Open the [Contribution guidelines for this project](Binance_Trading_Bots/)
Coin Pair: ETHUSD
Price Scale(%): 0.5
Rebounce(%): 0.2
Take Profit(%): 0.3
Trailing(%): 0.1
Stable Coin Amount to Use: 100
Volume Scale: 1.1
Orders: 7
