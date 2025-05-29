# Mean Reversion Strategy w/ Dynamic Thresholds
# This strategy trades a stock based on whether it's far from its recent average price
# For example, let's say we base a lookback on a 20-day moving average and a threshold of 2%
# Let's say the moving average is 12%. If the stock rises to 14% - we initiate a sell.
# If it falls to 12% - we initiate a buy.
# To make this strategy dynamic, use a rolling window and optimize for the best lookback / threshold based on --
# computed P&L
#Important Note: Since I am using yfinance data in the daily range, this investing decision is only being made once a
#day, you can change the frequency or import data to adjust this decision to a higher frequency one
#Since I have two parameters in this case: lookback and threshold and I am making an investment decision only once
# a day, I am doing 2 * 252, thus generating 504 data points or 504 days of historical data.
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pylab as plt


#Pulling a little more than 504 days of data of AAPL stock for the backtest
data = yf.download("AAPL", start="2023-5-23", end="2025-5-28")
#Keep the necessary columns
data = data[['Open', 'Close']]
data.dropna(inplace=True)

print("The total amount of trading days downloaded", len(data))
data.tail()

#Parameters - loockback + threshold
lookback_range = range(10, 61) #This is the amount of days we base our average on
entry_threshold_range = range(0.02) #this is the threshold to buy/enter at
exit_threshold_range = range(0.02) #this is the threshold to sell/exit at
window_size = 63

returns = []
positions = []

#Optimization loop. Brute force check all the best thresholds + lookback period
#This optimization loops is a forward walk meaning. For each day t we compute the best lookback, entry/exit threshold to make that days
#trade. We then continue forward and reoptimize the next day, and then the next, and so on . . .
#The profit and loss of this strategy is the aggregate of all the "optimized" days and this is the result of our backtest
#I will also extend this to calculate the sharpe ratio

for t in range(window_size, len(data) - 1):
    position = 0 # this is the position for the current day, we can either 0 be free of capital or 1 hold
    entry_price = 0
    training_data = data.iloc[t - window_size:t]
    best_profit_and_loss = -np.inf
    #This will be a tuple to store the best_params for that day
    best_params = None
    for lookback_value in lookback_range:
        for threshold_entry in entry_threshold_range:
            for threshold_exit in exit_threshold_range:
                profit_and_loss = 0
                position = 0 # 0 indicates closed position, 1 indicates bought position
                #simulate the trading strategy on a training window of the past 63 days using this combination
                # we are starting at lookback_value because you need at least lookback_value days of prior data to compute a valid moving average and then you can simulate the trading from there
                for i in range(lookback_value, len(training_data) - 1):
                    moving_average = training_data.iloc[i-lookback_value:i].mean()
                    price = training_data['Close'].iloc[i]
                    if position == 0 and price < moving_average * (1-threshold_entry):
                        position = 1
                        entry_price = training_data['Open'].iloc[i+1]
                    elif position == 1 and price > moving_average * (1-threshold_exit):
                        exit_price = training_data['Open'].iloc[i + 1] #your exit price is the next day you're able to sell at based on the open
                        profit_and_loss += exit_price - entry_price
                        position = 0 #reset the position

            if profit_and_loss > best_profit_and_loss:
                best_profit_and_loss = profit_and_loss
                best_params = (lookback_value, threshold_entry, threshold_exit)

    #apply the optimal parameters calculated from the last 63 days to the current day to make
    #a trading decision
    lookback_value, threshold_entry, threshold_exit = best_params
    moving_average = training_data.iloc[-lookback_value:].mean()
    price_today = data['Close'].iloc[t]
    open_today = data['Open'].iloc[t]
    open_tomorrow = data['Open'].iloc[t + 1]

    if position == 0:
        if price_today < moving_average * (1-threshold_entry):
            entry_price = open_tomorrow
            position = 1 #close the position
            returns.append(0) #no returns yet
        else:
            returns.append(0)
    elif position == 1:
        if price_today > moving_average * (1+threshold_exit):
            #Sell at open tomorrow
            exit_price = open_tomorrow
            ret = (exit_price - entry_price) / entry_price
            returns.append(ret)
            position = 0
    else:
        returns.append(0)  # Still holding











