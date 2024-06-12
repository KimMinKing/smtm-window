
import requests
from collections import defaultdict
from threading import Thread
from pprint import pprint
import json
from websocket import WebSocketApp
import time
import numpy as np
from cbstrategy import CBstrategy
from uptrader import uptradertest
import winsound as sd
from market import UpbitMarket
from log_manager import LogManager
import jwt  # PyJWT
import uuid
import os

class Upbitwebsocket:

    ACCESS_KEY = os.environ["UPBIT_OPEN_API_ACCESS_KEY"]
    SECRET_KEY = os.environ["UPBIT_OPEN_API_SECRET_KEY"]
    SERVER_URL = os.environ["UPBIT_OPEN_API_SERVER_URL"]

    def __init__(self):
        payload = {
        'access_key': self.ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
        }
        jwt_token = jwt.encode(payload, self.SECRET_KEY)
        authorization_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorization_token}

        self.ws = WebSocketApp(
            url="wss://api.upbit.com/websocket/v1",
            header=headers,
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=lambda ws, msg: self.on_error(ws, msg),
            on_close=lambda ws:     self.on_close(ws),
            on_open=lambda ws:     self.on_open(ws))
        self.running = False

    def initalize(self, request, callback=print, strategy=None):
        self.request = request
        self.callback = callback
        
        self.strategy= strategy
        self.logger = LogManager.get_logger(__class__.__name__)
        self.trader=uptradertest()
        self.strategy.initialize(100000)


    def on_message(self, ws, msg):
        info = json.loads(msg.decode('utf-8')) 
        if info.get('type') == "myTrade":
            #print(f"전략 웨이팅 : {self.strategy.waiting_request}")
            self.trader.post_query_result_task()
        else:
            target_request = self.strategy.update_trading_info(msg)


            # if len(target_request)>0:
            #     sd.Beep(300, 500)
            #     self.trader.send_request(target_request, self.send_request_callback)


    def on_message2(self, param):
        print(type(param))
        sd.Beep(300, 500)
        self.trader.send_request(param, self.send_request_callback)

    def send_request_callback(self, result):

        #self.logger.debug("send_request_callback is called")
        if result == "error!":
            self.logger.error("request fail")
            return
        self.strategy.update_result(result)

        if "state" in result and result["state"] != "requested":
            pass
            #원래는 analyzer 에 result 랑 같이 보내주는거임.

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

