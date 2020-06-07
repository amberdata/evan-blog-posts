import os
import json
import datetime
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
    gross_daily, all_activity = inf_outf.main()
    ohlcv = bitcoin_data()
    if os.getenv("PLOT"):
        plot(gross_daily, ohlcv)
    df_out = gross_daily.join(ohlcv)
    df_out.to_csv("results/gross_daily.csv")
    with open("results/all_activity.json", "w") as fout:
        json.dump(all_activity)


if __name__ == "__main__":
    main()