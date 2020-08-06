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


def init():
    "initializes the data file"
    if "results.csv" not in os.listdir("./data"):
        with open("data/results.csv", "w") as d:
            d.write("timestamp, address, value\n")

def check_for_whale(data):
    "checks whether a specific pending transaction can be suspected whale activity"
    address, value = data["from"], data["value"]
    if value >= config.VALUE_THRESHOLD * 10**8:
        logger.info(f"Whale address: {address[0]}, txn value: {value}")
        with open("data/results.csv", "a") as d:
            d.write(f"{datetime.now()}, {address}, {value}\n")

async def listen(headers):
    uri = 'wss://ws.web3api.io'
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        logger.info(f"Connected to Websocket at {uri}")
        message = json.dumps({
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'subscribe',
            'params': ['pending_transaction']
        })
        await websocket.send(message)
        while not 0:
            response = await websocket.recv()
            json_message = json.loads(response)
            if json_message.get('params') and json_message.get('params').get('result'):
                result = json_message.get('params').get('result')
                print(result)
                check_for_whale(result)

def main():
    # get the api key
    api_key = get_key()
    # init
    init()
    # create a header with our api key
    headers = {
        "x-api-key": api_key["AMBERDATA_API_KEY"],
        "x-amberdata-blockchain-id": "bitcoin-mainnet"
    }
    asyncio.get_event_loop().run_until_complete(listen(headers))
    logger.info('main end')


if __name__ == "__main__":
    main()