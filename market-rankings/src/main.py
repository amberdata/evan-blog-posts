""" Automatically create a universe of assets for intraday trading.
"""

import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import utils, config


api_key = utils.get_key()["AMBERDATA_API_KEY"]
headers = {'x-api-key': api_key}

def get_market_rankings():
    "Gets the market rankings data and does basic cleaning"
    # get the data
    url = "https://web3api.io/api/v2/market/rankings"
    querystring = {
        "sortType": "tradeVolume",
        "size": config.SIZE
    }
    payload = utils.get_response(url, headers, querystring)["data"]
    # save the results in a dataframe
    df = pd.DataFrame(payload).drop([
        "icon", 
        "maxSupply", 
        "totalSupply", 
        "tokenVelocity", 
        "transactionVolume", 
        "uniqueAddresses", 
        "specifications", 
        "address",
        "decimals",
        "circulatingSupply",
        "rank"
    ], axis=1)
    # make sense of the blockchain column
    df["blockchain"] = df.blockchain.map(lambda x: x["name"])
    # non-numeric columns
    non_num = ["name", "symbol", "blockchain"]   
    # changing numeric columns to float64
    df = pd.concat([df[non_num], df.drop(non_num, axis=1).apply(pd.to_numeric, axis=1)], axis=1)
    return df

def get_universe(df):
    "Whittles down the market data to the stock universe"
    # get the standard deviation in hourly price change in our data
    s = df.changeInPriceHourly.std()
    # selecting our asset universe
    universe = df.query(f"abs(changeInPriceWeekly) > {config.D_WEEKLY} & tradeVolume > {config.MIN_VOL} & abs(changeInPriceHourly) > {config.N_SIGMA*s} & currentPrice < {config.MAX_PRICE}")
    # return the results
    return universe

def get_pairs(universe):
    "Get's the pairs for the selected asset universe"
    # lets get the pairs available to trade
    url = "https://web3api.io/api/v2/market/prices/pairs"
    # recieve the payload
    payload = utils.get_response(url, headers)
    # get the base and quote
    pairs = [pair.split("_") for pair in payload if len(pair.split("_")) == 2]
    # matching the quotes to our selected universe
    universe_pairs = {}
    for symbol in universe.symbol:
        universe_pairs[symbol.lower()] = [[c for c in p if c != symbol.lower()][0] for p in pairs if symbol.lower() in p]
    return universe_pairs

def get_wap_data(base, quote):
    "returns the TWAP/VWAP for our quotes"
    # getting the WAP data
    url = f"https://web3api.io/api/v2/market/prices/{base}/wap/latest"
    wap = utils.get_response(url, headers)
    # test if there is any data
    if not wap:
        print(f"No WAP data for {base}")
        return {}
    # try to find a pair for our currency
    try:
        return wap[f"{base}_{quote}"]
    except KeyError:
        print(f"Error finding WAP pair for {base}")
        return {}

def display_results(df, universe_pairs):
    "Displays the best base's to trade"
    # assume BTC is the best way to buy a coin if we cannot do
    # so with our native currency
    # arrays to store results
    curr_avail, curr_wap = [], []
    best_symb, best_wap = [], []
    # which we have to buy with BTC, and which to buy with our currency
    for base, quotes in universe_pairs.items():
        if config.CURRENCY in quotes:
            curr_avail.append(base)
            curr_wap.append(get_wap_data(base, config.CURRENCY))
        else:
            if "btc" in quotes:
                best_symb.append(base)
                best_wap.append(get_wap_data(base, "btc"))
    
    # display the results
    cols = ["name", "symbol", "changeInPriceHourly", "currentPrice", "tradeVolume"]
    if curr_wap[0]:
        curr_wap = pd.DataFrame(curr_wap).drop(["timestamp"], axis=1)
    else:
        curr_wap = pd.DataFrame(curr_wap)
    if best_wap[0]:
        best_wap = pd.DataFrame(best_wap).drop(["timestamp"], axis=1)
    else:
        best_wap = pd.DataFrame(best_wap)

    if curr_avail:
        print("\nBase available to purchase with fiat:")
        fiat = df[df.symbol.map(lambda x: x.lower()).isin(curr_avail)][cols].reset_index(drop=True).join(curr_wap)
        print(fiat)
    else:
        print("\nUnable to purchase any bases with fiat")
    print(f"\nAble to purchase with btc:")
    btc = df[df.symbol.map(lambda x: x.lower()).isin(best_symb)][cols].reset_index(drop=True).join(best_wap)
    print(btc)
    return fiat, btc

def main():
    # get the market ranking data
    df = get_market_rankings()
    if os.getenv("PLOT"):
        df.changeInPriceHourly.plot.hist(bins=20)
        plt.title("Histogram of hourly change in price")
        plt.show()
    # calculate the asset universe
    universe = get_universe(df)
    print(f"Asset universe: \n{universe}")
    # get the pairs for our asset universe
    universe_pairs = get_pairs(universe)
    print(f"\nUniverse pairs: \n{universe_pairs}\n")
    # show the results
    fiat, btc = display_results(df, universe_pairs)
    # save the results
    now = datetime.now().strftime("%y-%m-%d_%H-%M")
    fiat.to_csv(f"results/{now}_fiat.csv", index=False)
    btc.to_csv(f"results/{now}_btc.csv", index=False)
    
    
if __name__ == "__main__":
    main()