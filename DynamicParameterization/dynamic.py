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
from tqdm import tqdm

# Pulling a little more than 504 days of data of AAPL stock for the backtest
data = yf.download("AAPL", start="2023-5-23", end="2025-5-28")
# Keep the necessary columns
data = data[['Open', 'Close']]
data.dropna(inplace=True)

print("The total amount of trading days downloaded", len(data))
data.tail()

# Parameters - loockback + threshold
lookback_range = range(10, 61)  # This is the amount of days we base our average on
entry_threshold_range = np.arange(0.01, 0.05, 0.01)  # this is the threshold to buy/enter at
exit_threshold_range = np.arange(0.01, 0.05, 0.01)  # this is the threshold to sell/exit at
window_size = 63

returns = []
position = 0  # persistent across all days
entry_price = 0  # persistent entry price

# Optimization loop. Brute force check all the best thresholds + lookback period
# This optimization loop is a forward walk meaning: for each day t we compute the best lookback, entry/exit threshold to make that day's
# trade. We then continue forward and reoptimize the next day, and then the next, and so on . . .
# The profit and loss of this strategy is the aggregate of all the "optimized" days and this is the result of our backtest
# I will also extend this to calculate the Sharpe ratio

for t in tqdm(range(window_size, len(data) - 1), desc="Backtesting Progress"):
    training_data = data.iloc[t - window_size:t]
    close_prices = training_data['Close'].values
    open_prices = training_data['Open'].values
    best_profit_and_loss = -np.inf
    best_params = None  # This will be a tuple to store the best_params for that day

    for lookback_value in lookback_range:
        for threshold_entry in entry_threshold_range:
            for threshold_exit in exit_threshold_range:
                profit_and_loss = 0
                sim_position = 0  # 0 indicates closed position, 1 indicates bought position
                sim_entry_price = 0

                # Simulate the trading strategy on a training window of the past 63 days using this combination
                for i in range(lookback_value, len(close_prices) - 1):
                    moving_average = np.mean(close_prices[i - lookback_value:i]).item()
                    price = close_prices[i]
                    if sim_position == 0 and price < moving_average * (1 - threshold_entry):
                        sim_position = 1
                        sim_entry_price = open_prices[i + 1].item()
                    elif sim_position == 1 and price > moving_average * (1 + threshold_exit):
                        exit_price = open_prices[i + 1].item()
                        profit_and_loss += exit_price - sim_entry_price
                        sim_position = 0

                if profit_and_loss > best_profit_and_loss:
                    best_profit_and_loss = profit_and_loss
                    best_params = (lookback_value, threshold_entry, threshold_exit)

    # Apply the optimal parameters calculated from the last 63 days to the current day to make a trading decision
    lookback_value, threshold_entry, threshold_exit = best_params
    moving_average = np.mean(training_data['Close'].values[-lookback_value:]).item()
    price_today = data['Close'].iloc[t].item()
    open_today = data['Open'].iloc[t].item()
    open_tomorrow = data['Open'].iloc[t + 1].item()

    if position == 0 and price_today < moving_average * (1 - threshold_entry):
        entry_price = open_tomorrow
        position = 1
        returns.append(0)  # No return yet
    elif position == 1 and price_today > moving_average * (1 + threshold_exit):
        exit_price = open_tomorrow
        ret = (exit_price - entry_price) / entry_price
        returns.append(ret)
        position = 0
    else:
        returns.append(0)

# After loop, show results
print("Number of trades executed:", sum([1 for r in returns if r != 0]))
print("Total return over period:", np.sum(returns))
print("Mean daily return:", np.mean(returns))
print("Sharpe Ratio Annualized:", (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) != 0 else 0)
