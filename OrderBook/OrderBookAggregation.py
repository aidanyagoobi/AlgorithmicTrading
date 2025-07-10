import pandas as pd
import requests
import math
from decimal import Decimal #helps to deal w/ floating point errors

symbol = "SOLUSDT" #lower volume
url = "https://api.binance.us/api/v3/depth"

interval = Decimal('0.1') #aggregating up to 10 cents

params = {
    "symbol": symbol,
    "limit": 100, #generatres a hundred levels in either direction
}

data=requests.get(url, params).json()


bid_levels = pd.DataFrame(data["bids"], columns = ['price', 'quantity'], dtype=float)
print(bid_levels)

min_bid_level = math.floor(min(bid_levels.price) / float(interval)) * interval
max_bid_level = math.ceil(max(bid_levels.price) / float(interval) + 1) * interval
print("The min bid_level is", min_bid_level) #this is the bottom of the buckets on the bid size
print("The max bid level is", max_bid_level) #this is the top of the buckets on the bid size

bid_level_bounds = [float(min_bid_level + interval * x) for x in range(int((max_bid_level
                                         - min_bid_level)/interval) + 1) #creating all the interval ranges
                    ]
bid_levels['bin']=pd.cut(bid_levels.price, bins=bid_level_bounds, right= False, precision=10)

bid_levels = bid_levels.groupby("bing")