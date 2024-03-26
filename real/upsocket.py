
import requests
from collections import defaultdict
from threading import Thread
from pprint import pprint
import json
from websocket import WebSocketApp
import time
import math

import numpy as np
from cbstrategy import CBstrategy


class Upbitwebsocket:

    def __init__(self, request, callback=print, strategy=None):
        self.request = request
        self.callback = callback
        self.strategy= strategy
        self.strategy.initialize(100000)
        self.ws = WebSocketApp(
            url="wss://api.upbit.com/websocket/v1",
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=lambda ws, msg: self.on_error(ws, msg),
            on_close=lambda ws:     self.on_close(ws),
            on_open=lambda ws:     self.on_open(ws))
        self.running = False


    def on_message(self, ws, msg):
        self.strategy.update_trading_info(msg)
        # msg = json.loads(msg.decode('utf-8'))
        # market = msg.get('code')
        # trade_volume = msg.get('trade_volume', 0)
        # trade_price=msg.get('trade_price', 0)
        # ask_bid = msg.get('ask_bid')
        # time=msg.get('trade_time')
        
        # if market and trade_volume and ask_bid:
        #     print(f"{time} - {market} -  {trade_volume} - {ask_bid} ")


    def on_error(self, ws, msg):
        self.callback(msg)

    def on_close(self, ws):
        self.callback("closed")
        self.running = False

    def on_open(self, ws):
        th = Thread(target=self.activate, daemon=True)
        th.start()

    def activate(self):
        self.ws.send(self.request)
        while self.running:
            time.sleep(1)
        self.ws.close()

    def start(self):
        self.running = True
        self.ws.run_forever()

    def restart_websocket(self):
        if self.ws:
            self.ws.close()
        time.sleep(5)  # 재시작 전 잠시 대기
        self.activate()

        
if __name__ == "__main__":

    start = time.time()

    cbst=CBstrategy()

    markets = '["KRW-DOGE", "KRW-LSK","KRW-CVC"]'
    request = '[{"ticket":"test"},{"type":"trade","codes":' + markets + '}]'
    real = Upbitwebsocket(request=request, strategy=cbst)   
    #real.callback = callback  
    real.start()

    
    end = time.time()
    print(f"---- 프로그램 실행 시간은 {round(end-start, 1)}초")