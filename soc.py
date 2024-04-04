
import requests
from collections import defaultdict
from threading import Thread
from pprint import pprint
import json
from websocket import WebSocketApp
import time
import math
from school import re
import numpy as np

class TTLDictionary:
    def __init__(self, ttl):
        self.dictionary = defaultdict(dict) 
        self.ttl_start_time = None
        self.ttl_duration = ttl

    def start_ttl(self):
        self.ttl_start_time = time.time()
        

    def is_expired(self):
        return time.time() >= self.ttl_start_time + self.ttl_duration

    def reset(self):
        #print(self.dictionary)
        self.dictionary = defaultdict(dict)
        self.ttl_start_time = None

    def add_value(self, key, value, value2):
        if self.ttl_start_time is None:
            print("Error: TTL not started. Use start_ttl method to start TTL.")
            return
        self.dictionary[key][value]={value2:0}
        #print(f"key : {key} - value : {value}")

    def __str__(self):
        return str(self.dictionary)

class UpbitReal:

    botmoney = np.array([151000, 161000, 206000, 226000, 236000])
    botmoneyalpha = 5000

    def __init__(self, request, callback=print):
        self.request = request
        self.callback = callback
        
        self.ws = WebSocketApp(
            url="wss://api.upbit.com/websocket/v1",
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=lambda ws, msg: self.on_error(ws, msg),
            on_close=lambda ws:     self.on_close(ws),
            on_open=lambda ws:     self.on_open(ws))
        self.running = False
        self.ttl = TTLDictionary(ttl=10)  # 10초 TTL을 가진 TTLDict 생성
        self.ttl.start_ttl()

    def on_message(self, ws, msg):
        msg = json.loads(msg.decode('utf-8'))
        market = msg.get('code')
        trade_volume = msg.get('trade_volume', 0)
        trade_price=msg.get('trade_price', 0)
        ask_bid = msg.get('ask_bid')
        time=msg.get('trade_time')
        
        if market and trade_volume and ask_bid:
            self.process_data(market, trade_volume, ask_bid,trade_price)

    # 값이 들어올 때마다 처리
    def process_data(self, market, value, ask_bid,trade_price):
        # self.ttl['KRW-BTC',"ASK"] = 232
        # self.ttl['KRW-BTC',"ASK"] = 2324
        # 현재 값을 저장
        
        
        #마켓이 있는거고
        count=0
        total=value*trade_price

        differences = np.abs(self.botmoney - total)
        botpricetrue = differences < self.botmoneyalpha

        #봇가격이 아니라면 꺼져
        if botpricetrue.any():
                
            trueindexlist=np.where(botpricetrue)[0]     #빼기 했을 때 true 것들이 어디 있냐
            trueprice=self.botmoney[min(trueindexlist)] #15100 거기서 가장 작은 인덱스값을 가진 가격

            #마켓에 해당하는 가격이 있는거고
            if trueprice in self.ttl.dictionary[market].keys():
                
                #매수매도라면
                if self.ttl.dictionary[market][trueprice] != ask_bid:
                    current_value = self.ttl.dictionary[market][trueprice]['BID']
                    self.ttl.dictionary[market][trueprice]['BID'] = current_value+1
                    if current_value==5:
                        print(f"{market}-{int(total):,}--{trueprice} - {self.ttl.dictionary[market][trueprice]['BID']}")
                    
            #해당하는 가격이 없으면 가격을 넣고
            elif ask_bid =="BID":
                self.ttl.add_value(market, trueprice , ask_bid)

                if self.ttl.is_expired():
                #print("Dictionary TTL expired, initializing...")
                    self.ttl.reset()
                    self.ttl.start_ttl()  # TTL 재설정





        # if self.ttl.data[market]:
        #     #마켓에 값은 있긴 있어
        #     abc= self.ttl.data[market][ask_bid]
            
        #     print(f"{market} -- {len(self.ttl.data[market][ask_bid])} -- ")
        #     #print(f"{self.ttl[market,ask_bid,value]}")
        #     if abc:
        #         if value in self.ttl.data[market][ask_bid]:
                    
        #             count=self.ttl.data[market][ask_bid][value]['count']+1
        #             if count>5:
                        
        #                 print(f"{market} |{value} {self.ttl.data[market][ask_bid][value]['count']} - !!!!!!!!")
                        
        #     self.ttl[market,ask_bid,value]= count
            
        # # if value == self.ttl.data[market][ask_bid][value]['value']:
        # #     print(f"{value} -- {self.ttl[market][ask_bid]} ")  # 적절한 알람 작동
        # else:
        #     #마켓이 없는거고
        #     self.ttl[market,ask_bid,value]= count



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

    abcd=re()
    abde=abcd.get()

    data=[]
    start = time.time()
    def callback(msg):
        abc={
            "market":msg['code'],
            "time":msg['trade_time'],
            "ask_bid":msg['ask_bid'],
            "trade_price":msg['trade_price'],
            "trade_volume":msg['trade_volume'],
            "total":msg['trade_price'] *  msg['trade_volume']
        }
        data.append(abc)
        print(abc)



    markets = '["KRW-DOGE", "KRW-LSK","KRW-CVC"]'
    request = '[{"ticket":"test"},{"type":"trade","codes":' + abde + '}]'
    real = UpbitReal(request=request)   
    #real.callback = callback  
    real.start()

    
    end = time.time()
    print(f"---- 프로그램 실행 시간은 {round(end-start, 1)}초")