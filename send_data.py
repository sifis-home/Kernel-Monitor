import datetime
import hashlib
import json
import platform
import re
import threading
import time

import websocket


def publish_thread(data):
    requestor_id = platform.node()

    # Get current date and time
    now = datetime.datetime.now()

    # Generate a random hash using SHA-256 algorithm
    hash_object = hashlib.sha256()
    hash_object.update(bytes(str(now), "utf-8"))
    hash_value = hash_object.hexdigest()

    # Concatenate the time and the hash
    request_id = str(requestor_id) + str(now) + hash_value
    request_id = (
        re.sub("[^a-zA-Z0-9\n\.]", "", request_id)
        .replace("\n", "")
        .replace(" ", "")
    )

    ws = websocket.WebSocketApp(
        "ws://localhost:3000/ws",
        on_open=on_open,
        on_error=on_error,
        on_close=on_close,
    )

    def send_data():
        ws_req = {
            "RequestPostTopicUUID": {
                "topic_name": "SIFIS:Privacy_Aware_Device_KERNEL_monitor",
                "topic_uuid": "KERNEL_monitor",
                "value": {
                    "description": "KERNEL monitor",
                    "requestor_id": str(requestor_id),
                    "request_id": str(request_id),
                    "connected": True,
                    "Data Type": "String",
                    "Dictionary": str(data),
                },
            }
        }
        time.sleep(5)
        ws.send(json.dumps(ws_req))

    def keep_sending_data():
        Flag = 0
        while Flag == 0:
            if ws.sock and ws.sock.connected:
                send_data()
                Flag = 1
            else:
                print("Websocket not connected, waiting for reconnection...")
                time.sleep(1)

    # Start the thread that sends data periodically
    data_thread = threading.Thread(target=keep_sending_data)
    data_thread.start()

    # Start the websocket connection
    ws.run_forever()  # Remove dispatcher parameter as it's not necessary anymore


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")


def on_open(ws):
    print("### Connection established ###")


def send_data(data):
    # Start a new thread to publish the data
    publish_data = threading.Thread(target=publish_thread, args=(data,))
    publish_data.start()

    return "Data Sent"
