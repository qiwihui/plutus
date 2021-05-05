#!/usr/bin/env python

import websocket

def on_message(wsapp, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("Opening")
    ws.send("""{"op":"unconfirmed_sub"}""")


wsapp = websocket.WebSocketApp("wss://ws.blockchain.info/inv",
    on_message=on_message, on_open=on_open, on_error = on_error, on_close = on_close)
wsapp.run_forever()
