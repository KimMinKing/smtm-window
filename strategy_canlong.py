import numpy as np
import time
import winsound as sd
from datetime import datetime, timedelta
from collections import defaultdict
from data_process import DataProcess
class StrategyCL:

    botmoney = np.array([155000,164000,205000, 213000, 221000, 229000, 240000])
    botmoneyalpha = 8000
    COMMISSION_RATIO = 0.0005

    def __init__(self, budget=100000):
        self.budget=budget
        self.blacklist=[]
        self.ttl = TTLDictionary(ttl=3)
        self.data_process = DataProcess()
        self.checklist={}
        self.endlist={}
        self.finallist={}


    def initialize(self, budget,count=1, min_price=5000, profit=0.004, stoploss=0.0023):
        """
        예산과 최소 거래 가능 금액을 설정
        """
        #ttl 정의를 해야할듯?
        self.marketcount=count
        self.maxprice=self.budget/self.marketcount
        self.ttl.start_ttl()
        

    def addblacklist(self, blacklist):
        self.blacklist.append(blacklist)

    def getamount(self):
        amount=self.budget/self.marketcount


    def checkdata(self, data):

        market=data["market"]
        askbid=data["ask_bid"]
        total=data["total"]
        tradeprice=data["trade_price"]

        if market in self.blacklist:
            return
        

        differences = self.botmoney-total   #total을 특정 봇 가격에 계산
        
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
                        
                self.checkqualification(market, trueprice, tradeprice)      #조건이 성립되었나 확인


            elif askbid=="BID":       #조건이 해당하지 않으니 그냥 값을 채워 넣는다.
                self.ttl.add_value(market, trueprice , askbid)     #'KRW-BTC' : 156000 : {BID : 0}

            
            self.timeexpired()


    def checkqualification(self, market, trueprice, tradeprice):

        try:    #keyerr 나나 확인하고
            current_value = self.ttl.dictionary[market][trueprice]['BID']
        except KeyError as e:
            print(f"key err  -  {e}")
            return None
            

        #key err 안나면 checklist에 있나 확인
        if market in self.checklist.keys():
            return
        
        #없으면 봇이 두번 왔다가고 했으니 매수
        if current_value>3 :
            tradetime=self.data_process.getnow()
            
            order={
                "id":self.timestamp_id(),
                "market":market,
                "type":'buy',
                "price":self.maxprice,
                "amount":0,
                "trueprice":trueprice,
                "progress":0
            }
            self.checklist.update({market:order})           #일단 확인 리스트에 넣어

            print(f"{tradetime} : {market} 봇 시작 - {trueprice}봇 - {tradeprice}원")

            

    def testbuy(self):
        tradetime=self.data_process.getnow()
        
        order={
            "id":self.timestamp_id(),
            "market":"KRW-DKA",
            "type":'buy',
            "price":6000,
            "amount":0
        }
        self.checklist.update({"KRW-DKA":order})           #일단 확인 리스트에 넣어

        print(f"{tradetime} : 봇 추가 KRW-DKA - TEST봇")
        


    def updateprocess(self):
        """ 
            checklist에 들어간거 확인하고
            finallist에서 
            1번은 시장가 매수
            2번은 지정가 매수
            3번은 지정가 매도
            4번은 시장가 매도
            0번은 성공한거
            9번은 실패한거
        """

        # checklist와 finallist의 키들을 비교하여 finallist에 있는지 확인
        for key in self.checklist.keys():       #checklist 에 있는 마켓들 다 반복
            if key in self.finallist and self.checklist[key]["id"] == self.finallist[key]["id"]:           #이미 final에 추가가 되었다면 패스
                return None
            else:
                self.finallist.update({key:self.checklist[key]})  #추가가 안되었으면 시장가 매수로 접수
                return [self.finallist]
                        

        for key in self.endlist.keys():         #endlist에 있는 마켓들 반복
            if key in self.finallist and self.endlist[key]["id"] == self.finallist[key]["id"]:           #이미 final에 추가가 되었으면 패스
                return None
            else:
                self.finallist.update({key:self.endlist[key]})  #안되었으면 시장가 매도로 접수
                return [self.finallist]


    def update_result(self, response):
        #임시로 콜백받아서 수량을 적을거임.
        #"amount": self.finallist[market]["amount"] 이걸 수정
        #print(f"response : {response}")
        if "quantity" in response:
            self.finallist[response["market"]]["amount"]=response["quantity"]
        print("_________________________________")

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


    def timestamp_id(self):
        """unixtime(sec) + %M%S 형태의 문자열 반환"""
        time_prefix = round(time.time() * 1000)
        now = datetime.now()
        now_time = now.strftime("%H%M%S")
        return f"{time_prefix}.{now_time}"

    def callbackchecklist(self, dicts):
        dellist = []

        # 딕셔너리 수정 대상 저장 리스트
        sellbool=False

        for market in self.checklist:
            try:
                current_value = dicts[market][self.checklist[market]["trueprice"]]['BID']
                if current_value < 2:
                    sellbool=True
            except KeyError:
                sellbool=True

            if sellbool:
                tradetime=self.data_process.getnow()
                print(f"{tradetime} : {market} 봇 종료 : - 처리 수량 : {self.finallist[market]['amount']}")

                order={
                "id": self.timestamp_id(), 
                "market":market,
                "type": "sell",                         #진입 buy
                "amount": self.finallist[market]["amount"],              #총액인데 안들어갈 확률도 있음. 에러 조심!
                "price":0,
                "progress" : 0
                }
                self.endlist.update({market:order})
                dellist.append(market)
                
        for market in dellist:
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
