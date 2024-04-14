
import requests
from collections import defaultdict
from threading import Thread
from pprint import pprint
import json
from websocket import WebSocketApp
import time
import numpy as np
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

    def initalize(self, request, callback=print):
        self.request = request
        self.callback = callback


    def on_message(self, ws, msg):
        info = json.loads(msg.decode('utf-8')) 
        self.callback(info)

    def send_request_callback(self, result):
        pass

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
            time.sleep(0.5)
        self.ws.close()

    def start(self):
        self.running = True
        self.ws.run_forever()

    def restart_websocket(self):
        if self.ws:
            self.ws.close()
        time.sleep(5)  # 재시작 전 잠시 대기
        self.activate()

