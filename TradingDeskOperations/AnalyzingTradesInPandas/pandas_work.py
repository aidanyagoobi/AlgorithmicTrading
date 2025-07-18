import pandas as pd


def main():
    df = pd.read_csv("trades.csv")
    df = df.dropna(subset=["Price"]) #drop all the null prices
    df["Volume"] = df["Volume"].fillna(0) #this fills all the empty volumes w/ 0
    df["Trader"] = df["Trader"].fillna("Unknown") #Fills in the missing trader
    print(df.info())
    df["Notional"] = df["Volume"] * df["Price"]
    total_notional_per_trader = df.groupby("Trader")["Notional"].sum()
    print("the total notional per trader is:\n", total_notional_per_trader)
    #here we can do some assertions to make sure that this is being computed correctly!
    average_trade_size_per_symbol = df.groupby("Symbol")["Volume"].mean()
    print("the average trade size per symbol is:", average_trade_size_per_symbol)

    sorted_notional_df = df.sort_values(by="Notional", ascending=False)

    sorted_notional_df.to_csv("cleaned_trades.csv", index=False)


if __name__ == "__main__":
    main()