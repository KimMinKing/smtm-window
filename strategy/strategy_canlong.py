import numpy as np
import time
from collections import defaultdict
from data_process import DataProcess
class StrategyCL:

    botmoney = np.array([154000,163000, 209000, 217000, 226000, 230000])
    botmoneyalpha = 8000


    def __init__(self, budget=10000):
        self.budget=budget
        self.blacklist=[]
        self.ttl = TTLDictionary(ttl=3)
        self.data_process = DataProcess()

    def initialize(self, budget, min_price=5000, profit=0.004, stoploss=0.0023):
        """
        예산과 최소 거래 가능 금액을 설정
        """
        #ttl 정의를 해야할듯?
        self.ttl.start_ttl()
        

    def addblacklist(self, blacklist):
        self.blacklist.append(blacklist)


    def checkdata(self, data):

        market=data["market"]
        askbid=data["ask_bid"]

        if market in self.blacklist:
            return
        

        differences = self.botmoney-data["total"]   #total을 특정 봇 가격에 계산
        
        botpricetrue = (differences >= 0) & (differences < self.botmoneyalpha)  

        if botpricetrue.any():      #조건에 해당되며 인덱스를 찾음
            trueindexlist=np.where(botpricetrue)[0]
            trueprice=self.botmoney[min(trueindexlist)]

            if trueprice in self.ttl.dictionary[market].keys():

                current_value=0

                if self.ttl.dictionary[market][trueprice]['BID']%2 == 0 and askbid=="ASK":    #짝수  | 2 가격이 있다면 짝수는 매도 홀수는 매수여야함.
                    
                    current_value = self.ttl.dictionary[market][trueprice]['BID']
                    self.ttl.dictionary[market][trueprice]['BID'] = current_value+1

                elif self.ttl.dictionary[market][trueprice]['BID']%2 == 1 and askbid=="BID" : #홀수
      
                    current_value = self.ttl.dictionary[market][trueprice]['BID']   #매도의 숫자
                    self.ttl.dictionary[market][trueprice]['BID'] = current_value+1 #+1
                        
                self.checkqualification(market, trueprice)      #조건이 성립되었나 확인


            elif askbid=="BID":       #조건이 해당하지 않으니 그냥 값을 채워 넣는다.
                self.ttl.add_value(market, trueprice , askbid)     #'KRW-BTC' : 156000 : {BID : 0}

            
            self.timeexpired()


    def checkqualification(self, market, trueprice):
        current_value = self.ttl.dictionary[market][trueprice]['BID']

        if current_value>3 and market not in self.checklist:    #단주매매 4번 이상, 진입하지 않았다면
            self.checklist.update({market:trueprice})           #일단 확인 리스트에 넣어


    def updateprocess(self):
        """ 
            checklist에 들어간거 확인하고
            조건 더 추가 한 다음
            또 다른 변수에 수수료를 곱해서
            차감 한다.
        """
        pass



    def timeexpired(self):

        #시간 만료되면 
        if self.ttl.is_expired():
            callback=None
            #ttl데이터 리셋하는데 콜백으로 보여줘
            if self.checklist:
                #체크리스트를 6초에 한번씩 검사하는거야
                callback=self.callbackchecklist
            self.ttl.reset(callback)    #삭제가 되는건 맞고
            self.ttl.start_ttl()  # TTL 재설정


    def callbackchecklist(self, dicts):
        dellist = []

        # 딕셔너리 수정 대상 저장 리스트
        keys_to_remove = []
        sellbool=False

        for market in self.checklist:
            try:
                current_value = dicts[market][self.checklist[market]]['BID']
                if current_value < 3:
                    sellbool=True
            except KeyError:
                sellbool=True

            if sellbool:
                tradetime=self.data_process.getnow()
                print(f"{market} 봇 종료 - {tradetime} : - 처리 수량 : {self.marketvollist[market]}")
                
                keys_to_remove.append(market)
                self.selllist.append({
                    "market":market,
                    "side": "sell",
                    "amount": self.marketvollist[market],
                    "order_type":"market",
                })
                

        # 반복문이 끝난 후 딕셔너리 수정
        for market in keys_to_remove:
            del self.checklist[market]


class TTLDictionary:
    def __init__(self, ttl):
        self.dictionary = defaultdict(dict) 
        self.ttl_start_time = None
        self.ttl_duration = ttl

    def start_ttl(self):
        self.ttl_start_time = time.time()
        

    def is_expired(self):
        return time.time() >= self.ttl_start_time + self.ttl_duration

    def reset(self, callback=None):
        if callback is not None:
            self.callback=callback
            self.callback(self.dictionary)
        self.dictionary = defaultdict(dict)
        self.ttl_start_time = None

    def add_value(self, key, value, value2):
        if self.ttl_start_time is None:
            print("Error: TTL not started. Use start_ttl method to start TTL.")
            return
        self.dictionary[key][value]={value2:0}
        #[KRW-BTC][161000]={BID:0}

    def __str__(self):
        return str(self.dictionary)
