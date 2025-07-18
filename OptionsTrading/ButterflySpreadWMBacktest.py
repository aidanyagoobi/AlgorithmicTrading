import pandas as pd
from polygon import RESTClient
def butterfly_calendar_spread():
    """This backtest strategy is on a calendar spread for a lower vol stock
    waste management ticker: WM. I will be analyzing the calendar spreads effectiveness
    and reporting some key metrics"""


def main():
    api_key = open("api_key.txt").read()
    client = RESTClient(api_key)
    aggs = client.get_aggs("O:WM250718C00230000", timespan="day", multiplier=1,
                    from_="2025-03-15", to="2025-07-15") #grabbing WM stock option for the past month
    df = make_df(aggs)
    print(df) #verify



def make_df(aggs):
    """Makes a usable dataframe from the options data"""
    data = []
    for agg in aggs:
        data.append(
            {
                "date": agg.timestamp,
                "open": agg.open,
                "high": agg.high,
                "low": agg.low,
                "close:": agg.close,
                "volume": agg.volume,
                "transactions": agg.transactions
            }
        )
    data = pd.DataFrame(data)
    data.index = pd.to_datetime(data.date, unit="ms").dt.date
    data.drop(columns=['date'], inplace=True) #redundant - we already set the date as the index
    return data

if __name__ == "__main__":
    main()