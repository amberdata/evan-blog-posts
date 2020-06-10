import os
import requests
import json
import datetime
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import config


def start_end_time():
    endTime = datetime.datetime.now()
    startTime = endTime - datetime.timedelta(config.N)

    endTime = str(int(endTime.timestamp()))
    startTime = str(int(startTime.timestamp()))
    return startTime, endTime

def get_key():
    "Get the API key from an .env file"
    if ".env" not in os.listdir("./"):
        print("Configuring API Key...")
        key = input("Amberdata API Key: ")
        with open(".env", "w") as f:
            f.write(f"AMBERDATA_API_KEY={key}\n")
    load_dotenv(verbose=True)
    return {
        "AMBERDATA_API_KEY": os.getenv("AMBERDATA_API_KEY")
    }

def get_response(url, headers=None, queryString=None):
    "Get the REST response from the specified URL"
    if not headers:
        headers = {'x-api-key': api_key}
    if queryString:
        response = requests.request("GET", url, headers=headers, params=queryString)
    else:
        response = requests.request("GET", url, headers=headers)
    response = json.loads(response.text)
    try:
        if response["title"] == "OK":
            return response["payload"]
    except Exception:
        print(response)
        return None
        
def inflow_outflow(data: dict):
    "Returns the inflow and outflow of the payload"
    # get the column names
    columns = data["metadata"]["columns"]
    # load the data, dropping timestampNano
    ad_hist = pd.DataFrame(data["data"], columns=columns).drop("timestampNanoseconds", axis=1)
    # change dtype of appropriate columns to Int
    ad_hist[["blockNumber", "timestamp", "value"]] = ad_hist[["blockNumber", "timestamp", "value"]].apply(pd.to_numeric)
    # sort by blockNum desc
    ad_hist = ad_hist.sort_values("timestamp").reset_index(drop=True)
    # calculate inflow and outflow
    ad_hist["diff"] = ad_hist["value"].diff()
    ad_hist["inflow"] = np.where(ad_hist["diff"] > 0, ad_hist["diff"], 0)
    ad_hist["outflow"] = np.where(ad_hist["diff"] < 0, abs(ad_hist["diff"]), 0)
    # return the result
    return ad_hist

def reindex(data, index):
    """ Returns the DataFrame calculated w/ inflow & outflow
    :type data: DataFrame
    :type index: List[int]
    :rtype: DataFrame
    """
    d = np.digitize(data.timestamp.values, index)
    g = data[["inflow", "outflow"]].groupby(d).sum()
    g = g.reindex(range(config.N), fill_value=0)
    g.index = config.index
    return g

def daily_inflow_outflow(address, headers, querystring):
    url = "https://web3api.io/api/v2/addresses/" + address + "/account-balances/historical"
    try:
        payload = get_response(url=url, headers=headers, queryString=querystring)
    except Exception:
        return None
    if len(payload["data"]) > 1:   # if there is activity in the period
        # calculate inflow / outflow
        data = inflow_outflow(payload)
        # get in the format to merge with master inflow/outflow data
        g = reindex(data, config.index)
        return g