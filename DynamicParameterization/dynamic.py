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
for t in range(window_size):

