"Listens to the Bitcoin blockchain and watches for whale activity"
import os
import ssl
import json
from datetime import datetime
import websockets
import asyncio
from log import logger
import config
from utils import get_key


# the threshold for whale activity in shatoshiss
VALUE_THRESHOLD = config.BTC_THRESHOLD * 10**8

def init_data_file():
    "initializes the data file"
    # write a new results file with a header if we do not have one
    if "results.csv" not in os.listdir("./data"):
        with open("data/results.csv", "w") as d:
            d.write("timestamp, address, value\n")

def check_for_whale(data):
    "checks whether a specific pending transaction can be suspected whale activity"
    address, value = data["from"], data["value"]
    # check if the value of the pending txn is larger than our threshold
    if value >= VALUE_THRESHOLD:
        # send the whale activity info to stdout
        logger.info(f"Whale address: {address[0]}, shatoshis: {value}")
        # write the data to a csv file
        with open("data/results.csv", "a") as d:
            d.write(f"{datetime.now()}, {address}, {value}\n")

async def on_response(response):
    "executes when we get a response back"
    # load the response as a dictionary
    json_message = json.loads(response)
    # if there is data in the response, perform the whale check
    if json_message.get('params') and json_message.get('params').get('result'):
        result = json_message.get('params').get('result')
        check_for_whale(result)

async def listen(api_key):
    "Opens the websocket connection and listens for data"
    # the amberdata websocket uri
    uri = 'wss://ws.web3api.io'
    # our headers for the connection
    headers = {
        "x-api-key": api_key["AMBERDATA_API_KEY"],
        "x-amberdata-blockchain-id": "bitcoin-mainnet"
    }
    # create the websocket item
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        logger.info(f"Connected to Websocket at {uri}")
        # the message to pass for pending transactions
        message = json.dumps({
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'subscribe',
            'params': ['pending_transaction']
        })
        # send our message to the websocket
        await websocket.send(message)
        # continuously listen for data and process
        while True:
            # the response from the websocket
            response = await websocket.recv()
            # interpret the response
            await on_response(response)

def main():
    # get the api key
    api_key = get_key()
    # initialize the data file
    init_data_file()
    # open the connection and start recieving data
    asyncio.get_event_loop().run_until_complete(listen(api_key))
    # keep listening 
    asyncio.get_event_loop().run_forever()
    logger.info('main end')


if __name__ == "__main__":
    main()