import re
import pandas as pd
def analyze_and_clean_exchange_logs(src):
    """This parses the log extracting the relevant fields:
    Timestamp, SYMBOL, PRICE, VOLUME, and TRADER. It fills in the missing fields
    w/ Unknown/0.0 and provides key metrics such as: the total number of trades,
    the trade with the highest Notional, and the total traded volume per Symbol
    """
    with open(src, 'r') as file:
        master_log = []
        for line in file:
            timestamp = re.search(r'(\d{4}-\d{2}-\w{5}:\d{2}:\d{2}Z)', line) #grab the corresponding timestamp
            if timestamp:
                timestamp = timestamp.group(1) #ensures that we get a match
            else:
                continue
            trade_info = dict(re.findall(r'(\w+)=(\w+)', line))
            #print(trade_info)
            #add timestamp to the trade dict
            trade_info["TIMESTAMP"] = timestamp
            #update the values and edit if it's null or not
            if trade_info.get("SYMBOL") is None:
                trade_info["SYMBOL"] = "Unknown"
            if trade_info.get("TRADER") is None:
                trade_info["TRADER"] = "Unknown"
            if trade_info.get("PRICE") is None:
                trade_info["PRICE"] = 0.0
            if trade_info.get("VOLUME") is None:
                trade_info["VOLUME"] = 0
            #extract the values and put them in the master log dict
            master_log.append(trade_info)

        df = pd.DataFrame(master_log)
        print(df)
        #This is error handling
        try:
            df["VOLUME"] = df["VOLUME"].astype(float)
        except ValueError:
            print("Invalid Price Format")
        df["PRICE"] = df["PRICE"].astype(float)
        df["NOTIONAL"] = df["PRICE"] * df["VOLUME"]
        total_number_of_trades = df["VOLUME"].sum()
        idx = df["NOTIONAL"].idxmax()
        largest_trade_notional = df.iloc[idx]
        total_traded_volume_per_symbol = df.groupby("SYMBOL")["VOLUME"].sum()
        print('The largest trade notional is\n', largest_trade_notional)
        print("The total number of trades is\n", total_number_of_trades)
        print("The total traded volume per symbol is\n", total_traded_volume_per_symbol)


def main():
    src = "exchange_logs.txt"
    analyze_and_clean_exchange_logs(src)

if __name__ == "__main__":
    main()