import os
import json
import datetime
import argparse
import pandas as pd

import config, utils
import inf_outf


def bitcoin_data():
    pair = "xbtusd_bitmex"

    url = "https://web3api.io/api/v2/market/ohlcv/"+pair+"/historical"

    querystring = {
        "exchange":"bitmex",
        "startDate":config.startTime,
        "endDate":config.endTime,
        "timeInterval":"days"
    }

    headers = {'x-api-key': config.api_key}

    payload = utils.get_response(url, headers=headers, queryString=querystring)

    ohlcv = pd.DataFrame(payload["data"]["bitmex"], columns=payload["metadata"]["columns"]).iloc[1:]
    ohlcv = ohlcv.drop(["open", "high", "low", "timestamp"], axis=1)
    ohlcv.index = [datetime.datetime.fromtimestamp(ts//1000).date() for ts in config.index]
    return ohlcv


def main():
    parser = argparse.ArgumentParser(description="Controlling the analysis size from the command line")
    parser.add_argument("--n-addresses", type=int, default=250,
                        help="The number of addresses to run in this batch")
    args = parser.parse_args()
    # the main analysis
    gross_daily, all_activity = inf_outf.main(args.n_addresses)
    # get bitcoin data over the period
    ohlcv = bitcoin_data()
    # display the results
    if os.getenv("PLOT"):
        plot(gross_daily, ohlcv)
    # save the files
    df_out = gross_daily.join(ohlcv)
    df_out.to_csv("results/gross_daily.csv")
    with open("results/all_activity.json", "w") as fout:
        json.dump(all_activity, fout)


if __name__ == "__main__":
    main()
