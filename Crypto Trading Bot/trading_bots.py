import time
import linecache

def martingale_bot(client):
    variables = open('variables.txt','r')
    variables_list = []
    for line in variables:
        a, b = line.split(':')
        b = b.replace(' ', '')
        variables_list.append(b.replace('\n',''))
    variables.close()

    #gives a variable to each value in the variables list
    symbol = variables_list[0]
    scale = float(variables_list[1])
    rebounce = float(variables_list[2])
    profit = float(variables_list[3])
    trailing = float(variables_list[4])
    use = float(variables_list[5])
    volume = float(variables_list[6])
    orders = int(variables_list[7])

    print(f'Coin Pair: {symbol}\nPrice Scale(%): {scale}\nRebounce(%): {rebounce}\nTake Profit: {profit}\nTrailing(%): {trailing}\nStable Coin Amount to Use: {use}\nVolume Scale: {volume}\nOrders: {orders}')

    # keeps tracks of how many sells the bot performs and total profit
    transactions = 0
    print(f'\nTotal Transactions: {transactions}')
    round_profit = 0
    print(f'Round Profit: {round(round_profit, 4)}')
    try:
        total_profit = linecache.getline('profit_log.txt', 1).strip()
        total_profit = float(total_profit)
    except:
        total_profit = 0
    print(f'Total Profit: {round(total_profit, 4)}')

    #finds the amount that should be used for each purchase (finds volume scale)
    volume_list = []
    series_sum = (1-volume**orders)/(1-volume)
    x = (use + total_profit)/ series_sum
    for i in range(orders):
        volume_list.append(x*volume**i)

    price_bought = []
    amount_bought = []
    sell_price = 999999

    #checks if the code crashed or reset and updates buy amount
    try:
        with open("buy_orders.txt","r") as buy_orders:
            prices_before = linecache.getline('buy_orders.txt', 1).strip()
            price_bought = prices_before.split()
            for i in range(len(price_bought)):
                price_bought[i] = float(price_bought[i])
            amount_before = linecache.getline('buy_orders.txt', 2).strip()
            amount_bought = amount_before.split()
            for i in range(len(amount_bought)):
                amount_bought[i] = float(amount_bought[i])
            bought = int(linecache.getline('buy_orders.txt', 3).strip())
    except:
        price_bought = []
        amount_bought = []
        bought = 0

    while True:
        #checks recent price
        recent_price_chart = client.get_symbol_ticker(symbol=symbol)
        recent_price = float(recent_price_chart['price'])

        #updates sell price depending on price and amount bought
        if len(price_bought)>0 and len(amount_bought)>0:
            total_cost = 0
            for i in range(len(price_bought)):
                total_cost += price_bought[i] * amount_bought[i]
            sell_price = total_cost * (1 + profit/100) / sum(amount_bought)


        #buys first round automatically
        if bought == 0:
            buy_order = client.order_market_buy(symbol=symbol, quantity=round(volume_list[bought]/recent_price, 4))
            price_bought.append(recent_price)
            amount_bought.append(round(volume_list[bought]/recent_price, 4))
            bought += 1

            #keeps track of bought order in case bot crashes
            with open("buy_orders.txt","w") as buy_orders:
                for i in price_bought:
                    buy_orders.write(f'{i} ')
                buy_orders.write('\n')
                for i in amount_bought:
                    buy_orders.write(f'{i} ')
                buy_orders.write('\n')
                buy_orders.write(f'{bought}')

        #when recent price drops below price scale, trailing buy sequence starts
        if bought >= 1 and bought < orders and recent_price <= price_bought[-1]*(1-scale/100):

            trailing_buy = round(recent_price*(1+rebounce/100), 4)

            while True:
                recent_price_chart_trailing_buy = client.get_symbol_ticker(symbol=symbol)
                recent_price_trailing_buy = float(recent_price_chart_trailing_buy['price'])

                #if price drops below the recent price first evaluated, updates trailing buy and then updates recent price
                if recent_price_trailing_buy < recent_price:
                    trailing_buy = trailing_buy - (recent_price - recent_price_trailing_buy)
                    recent_price = recent_price_trailing_buy
                    time.sleep(0.5)

                #if price goes above trailing buy amount, creates a buy order
                elif recent_price_trailing_buy >= trailing_buy:
                    buy_order = client.order_market_buy(symbol=symbol, quantity=round(volume_list[bought]/recent_price_trailing_buy, 4))
                    price_bought.append(recent_price_trailing_buy)
                    amount_bought.append(round(volume_list[bought]/recent_price, 4))
                    bought += 1

                    #keeps track of bought order in case bot crashes
                    with open("buy_orders.txt","w") as buy_orders:
                        for i in price_bought:
                            buy_orders.write(f'{i} ')
                        buy_orders.write('\n')
                        for i in amount_bought:
                            buy_orders.write(f'{i} ')
                        buy_orders.write('\n')
                        buy_orders.write(f'{bought}')
                    break

                #continues the loop if none of the conditions are reached
                else:
                    time.sleep(0.5)
                    continue

        #when recent price goes above the sell price, starts the trailing sell sequence
        elif bought >= 1 and recent_price >= sell_price:

            trailing_sell = round(recent_price*(1-trailing/100), 4)

            while True:
                recent_price_chart_trailing_sell = client.get_symbol_ticker(symbol=symbol)
                recent_price_trailing_sell = float(recent_price_chart_trailing_sell['price'])

                #if price goes above recent price first evaluated, updates trailing sell and then updates recent price
                if recent_price_trailing_sell > recent_price:
                    trailing_sell = trailing_sell + (recent_price_trailing_sell - recent_price)
                    recent_price = recent_price_trailing_sell
                    time.sleep(0.5)

                #if price drops below trailing sell amount, creates a sell order and sells all that was bought this round and resets everything and prints transactions
                elif recent_price_trailing_sell <= trailing_sell:
                    free_symbol_sell_balance = client.get_asset_balance(asset = symbol[:3])
                    free_symbol_balance = float(free_symbol_sell_balance['free'])
                    sell_order = client.order_market_sell(symbol = symbol, quantity = free_symbol_balance)

                    #calculates profit
                    total_round_cost = 0
                    for i in range(len(price_bought)):
                        total_round_cost += price_bought[i] * amount_bought[i]
                    round_profit = round(recent_price_trailing_sell * sum(amount_bought) - total_round_cost, 4)
                    total_profit += round_profit

                    #recalculates volume
                    volume_list = []
                    series_sum = (1-volume**orders)/(1-volume)
                    x = (use + total_profit)/ series_sum
                    for i in range(orders):
                        volume_list.append(x*volume**i)

                    #saves total profit to a text file to prevent crashes from erasing data
                    with open("profit_log.txt","w") as profit_log:
                        profit_log.write(f'{total_profit}')

                    #resets parameters and prints
                    price_bought = []
                    amount_bought = []
                    sell_price = 999999
                    bought = 0
                    transactions += 1
                    print(f'\nTotal Transactions: {transactions}')
                    print(f'Round Profit: {round(round_profit, 4)}')
                    print(f'Total Profit: {round(total_profit, 4)}')
                    break

                #continues the loop if none of the conditions are reached
                else:
                    time.sleep(0.5)
                    continue

        #continues the loop and updates recent price if none of the conditions are reached
        else:
            time.sleep(0.5)
            continue
