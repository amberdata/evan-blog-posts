""" Listens to the mempool and watches for large transactions to/from BitMEX wallets
    Author: Evan Azevedo
    Org: Amberdata
"""
import os
import ssl
import json
from datetime import datetime
import asyncio
import websockets
import pandas as pd
from log import logger
import config
from utils import get_key
from bloomfilter import BloomFilter


class ListenMempool:
    "Opens a websocket and records large transactions in the bitcoin mempool"
    def __init__(self):
        # the threshold for whale activity in shatoshiss
        self.VALUE_THRESHOLD = config.BTC_THRESHOLD * 10**8
        # the amberdata websocket uri
        self.uri = 'wss://ws.web3api.io'

    def init_data_file(self):
        "initializes the data file"
        # write a new results file with a header if we do not have one
        if "results.csv" not in os.listdir("data"):
            with open("data/results.csv", "w") as d:
                # the target is the exchange column
                d.write("timestamp; from; to; hash; value; exchange\n")

    def init_addresses(self):
        "loads the BitMEX wallet addresses"
        # read in the data from csv
        df = pd.read_csv("data/addresses_all.csv", index_col=0)
        # drop an N/A values
        df.dropna(inplace=True)
        # put the addresses in the class 
        self.addresses = df.values

    def init_bf(self):
        "initializes the bloom filter"
        # number of objects in the bloom filter
        n = len(self.addresses)
        # the bloom filter object
        self.bloomf = BloomFilter(n, config.P)
        # display some info about the filter
        print(f"Bloom Filter stats:\n\tSize of bit array: {self.bloomf.size}") 
        print(f"\tFalse positive Probability: {self.bloomf.fp_prob}") 
        print(f"\tNumber of hash functions: {self.bloomf.hash_count}") 
        # iteratively add addresses to the bloom filter
        for address in self.addresses:
            self.bloomf.add(address)

    def query_bf(self, l_from, l_to):
        """ queries the bloom filter given a list of addresses from and to
            Return:
                0: address is not present in from or to fields
                1: address may be present in from field
                2: address may be present in to field
                3: address may be present in both fields
        """
        # boolean variables if the bloom filter returns true or false
        b_from, b_to = False, False
        # check the from address(es)
        for address in l_from:
            if self.bloomf.check(address) or address[:5]=='3BMEX' or address[:7]=='3BitMEX':
                b_from = True
        # check the to address(es)
        for address in l_to:
            if self.bloomf.check(address) or address[:5]=='3BMEX' or address[:7]=='3BitMEX':
                b_to = True 
        return 1*b_from + 2*b_to

    def check_for_wallet(self, data):
        "checks whether a specific pending transaction can be from a bitmex wallet"
        add_from, add_to, hash_num, value = data['from'], data['to'], data['hash'], data['value']
        # check if the value of the pending txn is larger than our threshold
        if value >= self.VALUE_THRESHOLD:
            # query the bloom filter
            exchange = self.query_bf(add_from, add_to)
            if exchange == 1:
                status = 'from'
            elif exchange == 2:
                status = 'to'
            else: status = 'neither'
            # log the large transaction
            logger.info(f"Large transaction: From: {add_from[0]}, To: {add_to[0]}, btc: {round(value/10**8, 3)}, status: {status}")
            # write the data to a csv file
            with open("data/results.csv", "a") as d:
                d.write(f"{datetime.now()}; {add_from}; {add_to}; {hash_num}; {value}; {exchange}\n")

    async def on_response(self, response):
        "executes when we get a response back"
        # load the response as a dictionary
        json_message = json.loads(response)
        # if there is data in the response, perform the whale check
        if json_message.get('params') and json_message.get('params').get('result'):
            # parse the result into a dict object
            result = json_message.get('params').get('result')
            # check if the transaction is engaging with one of the wallets
            self.check_for_wallet(result)

    async def listen(self):
        "Opens the websocket connection and listens for pending transactions"
        # our headers for the connection
        headers = {
            "x-api-key": self.api_key["AMBERDATA_API_KEY"],
            "x-amberdata-blockchain-id": "bitcoin-mainnet"
        }
        # outer loop
        while True:
            # create the websocket item
            async with websockets.connect(self.uri, extra_headers=headers, ping_interval=None) as websocket:
                logger.info(f"Connected to Websocket at {self.uri}")
                # the message to pass for pending transactions
                message = json.dumps({
                    'jsonrpc': '2.0',
                    'id': 2,
                    'method': 'subscribe',
                    'params': ["pending_transaction"]
                })
                # send our message to the websocket
                await websocket.send(message)
                # continuously listen for data and process
                while True:
                    try:
                        # the response from the websocket
                        response = await asyncio.wait_for(websocket.recv(), timeout=25)
                    except Exception as e:
                        logger.error(str(e))
                        try:
                            pong = await websocket.ping()
                            await asyncio.wait_for(pong, timeout=100)
                            logger.debug('Ping OK, keeping connection alive...')
                            continue
                        except:
                            # sleep for 30 seconds
                            await asyncio.sleep(30)
                            break  # inner loop
                    # interpret the response
                    await self.on_response(response)
                    
    def main(self):
        # get the api key
        self.api_key = get_key()
        # initialize the data file
        self.init_data_file()
        # initialize the addresses
        self.init_addresses()
        # initialize the bloom filter
        self.init_bf()
        # open the connection and start recieving data
        asyncio.get_event_loop().run_until_complete(self.listen())
        # keep listening 
        asyncio.get_event_loop().run_forever()
        logger.info('main end')


if __name__ == "__main__":
    ListenMempool().main()
