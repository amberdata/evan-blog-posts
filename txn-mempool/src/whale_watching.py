"Listens to the Bitcoin blockchain and watches for whale activity"
import ssl
import json
from datetime import datetime
import websocket
from log import logger
import config
from utils import get_key


def on_open(ws):
    """Sends a message upon opening the websocket connection"""
    logger.info(f'websocket {ws.url} was connected')
    ws.send(json.dumps({
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'subscribe',
        'params': ['pending_transactions']
    }))
    
def check_for_whale(data):
    "checks whether a specific pending transaction can be suspected whale activity"
    address, value = data["from"], data["value"]
    if value >= config.VALUE_THRESHOLD * 10**8:
        logger.info(f"Whale address: {address[0]}, txn value: {value}")
        with open("logs/log.csv", "a") as l:
            l.write(f"{datetime.now()}, {address}, {value}\n")

def on_message(ws, message):
    "reacts to messages from the websocket"
    json_message = json.loads(message)
    if json_message.get('params') and json_message.get('params').get('result'):
        result = json_message.get('params').get('result')
        check_for_whale(result)

def main():
    # get the api key
    api_key = get_key()["AMBERDATA_API_KEY"]
    # instantiate the websocket object
    ws = websocket.WebSocketApp(config.AMBERDATA_WEBSOCKET_BASE)
    # create a header with our api key
    ws.header = {"x-api-key": api_key, "x-amberdata-blockchain-id": config.BLOCKCHAIN_ID}
    # function to open the websocket stream
    ws.on_open = on_open
    # function to perform when we recieve a message
    ws.on_message = on_message
    # continuously keep the connection open
    ws.run_forever(sslopt={'cert_reqs': ssl.CERT_NONE})
    logger.info('main end')


if __name__ == "__main__":
    main()