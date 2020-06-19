"""
    Queries historical account balances and creates inflow outflow
    from a set of addresses
"""

import datetime
import pandas as pd 
import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import utils, config


def main():
    querystring = {"startDate": config.startTime,
               "endDate": config.endTime}

    headers = {
        'x-amberdata-blockchain-id': "bitcoin-mainnet",
        'x-api-key': config.api_key
    }

    # create the output dataframe
    columns = ["inflow", "outflow"]
    gross_daily = pd.DataFrame(index=config.index, columns=columns).fillna(0)

    # Read the data
    print("Loading the addresses")
    # df = pd.read_excel("input/Cluster_addresses_of_Bitmex.xlsx", header=12, skipfooter=3)
    df = pd.read_csv("input/addresses_all.csv")
    # check if we are running the full calculation
    if config.A:
        addresses = df.iloc[:A].Address.values
    else:
        addresses = df.Address.values

    all_activity = {}
    # calculate inflow/outflow from the addresses in parallel
    for i in tqdm.trange(len(addresses) // config.P):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(utils.daily_inflow_outflow, addresses[config.P*i+j], \
                headers, querystring): addresses[config.P*i+j] for j in range(config.P) if i+j < len(addresses)}
            for future in as_completed(futures):
                address = futures[future]
                res = future.result()
                if res is not None:
                    gross_daily += res
                    all_activity[address] = res.to_json()
                else:
                    all_activity[address] = {}

            
    # calculate the net flows
    gross_daily["net"] = gross_daily["inflow"] - gross_daily["outflow"]
    # set index to datetime
    gross_daily.index = [datetime.datetime.fromtimestamp(ts//1000).date() for ts in config.index]
    # Rescale value by 10^8
    return gross_daily/10**8, all_activity