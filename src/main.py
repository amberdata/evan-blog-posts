import os
import matplotlib.pyplot as plt
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

def plot(gross_daily, ohlcv):
    fig, ax1 = plt.subplots()

    ax1.set_title(f"Inflow Outflow of {A} Addresses")
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Volume')
    ax1.plot(gross_daily)
    ax1.tick_params(axis='y')
    ax1.legend(["inflow", "outflow", "net"], loc=4)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:red'
    ax2.set_ylabel("price", color=color)  # we already handled the x-label with ax1
    ax2.plot(ohlcv.close, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.show()


def main():
    gross_daily = inf_outf.main()
    ohlcv = bitcoin_data()
    if os.getenv("PLOT"):
        plot(gross_daily, ohlcv)
    df_out = gross_daily.join(ohlcv)
    df_out.to_csv("results/gross_daily.csv")


if __name__ == "__main__":
    main()