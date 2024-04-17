import numpy as np
import time
import winsound as sd
from datetime import datetime, timedelta
from collections import defaultdict
from data_process import DataProcess
class StrategyCanL:

    botmoney = np.array([148000,158000,168000,198000, 205000, 211000, 215000, 222000])
    botmoneyalpha = 5000
    COMMISSION_RATIO = 0.0005

    def __init__(self, budget=10000):
        self.budget=budget
        self.blacklist=['KRW-CVC','KRW-STRAX','KRW-BTC','KRW-BTT']
        self.ttl = TTLDictionary(ttl=4)
        self.data_process = DataProcess()
        self.checklist={}
        self.endlist={}
        self.finallist={}
        self.locklist={}
        self.asset={}


    def initialize(self, budget,count=1, min_price=5000, profit=0.0065, stoploss=0.0043):
        """
        예산과 최소 거래 가능 금액을 설정
        """
        #ttl 정의를 해야할듯?
        self.marketcount=count
        self.maxprice=self.budget/self.marketcount
        self.profit=profit
        self.stoploss=stoploss
        self.showprocess=False
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
        elif self.showprocess:
            print(f"{market} - {tradeprice} - {askbid}")
        

        differences = np.abs(self.botmoney-total)   #total을 특정 봇 가격에 계산
        
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


                self.checkqualification(market, trueprice, tradeprice,data)      #조건이 성립되었나 확인


            elif askbid=="BID":       #조건이 해당하지 않으니 그냥 값을 채워 넣는다.
                self.ttl.add_value(market, trueprice , askbid)     #'KRW-BTC' : 156000 : {BID : 0}

            
            self.timeexpired()


    def checkqualification(self, market, trueprice, tradeprice, data):

        try:    #keyerr 나나 확인하고
            current_value = self.ttl.dictionary[market][trueprice]['BID']
        except KeyError as e:
            print(f"key err  -  {e}")
            return None

        #key err 안나면 checklist에 있나 확인
        if market in self.checklist.keys():
            return
        #없으면 봇이 두번 왔다가고 했으니 매수
        elif current_value>3 and market not in self.checklist.keys():
            tradetime=self.data_process.getnow()
            print(f"{tradetime} : {market} 봇 시작 - {trueprice}봇 -", end="")
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
            print(f" {tradeprice}원 |  ")




    def updateprocess(self, data):

        market=data["market"]
        tradeprice=data["trade_price"]

        if market not in self.checklist.keys() and market not in self.finallist.keys():
        #봇도 없고 진입도 없다면
        #그냥 끄셈
            return
            
        elif market in self.checklist.keys() and market in self.finallist.keys() and market not in self.locklist.keys():
        #       봇은 돌아가고                       진입도 했으며                       익손절을 안했을 때

            #익절가와 손절가를 확인함

            if "targetprice" in self.checklist[market]:
                #익절가가 생성 되었으면
                tradetime=self.data_process.getnow()
                if tradeprice > self.checklist[market]['targetprice']:
                    #익절
                    order={
                        "id": self.timestamp_id(), 
                        "market":market,
                        "type": "sell",
                        "amount": self.asset[market],
                        "price":tradeprice,
                        "progress" : 3
                    }
                    print(f"{tradetime} : {market} 익절가 도달 : - 처리 수량 : {self.asset[market]} | 가격 : {tradeprice} > {self.checklist[market]['targetprice']}")
                    self.endlist.update({market:order})
                    self.locklist.update({market:order})

                elif tradeprice < self.checklist[market]['outprice']:
                    #손절
                    order={
                        "id": self.timestamp_id(), 
                        "market":market,
                        "type": "sell",
                        "amount": self.asset[market],
                        "price":0,
                        "progress" : 3
                    }
                    print(f"{tradetime} : {market} 손절가 도달 : - 처리 수량 : {self.asset[market]} | 가격 : {tradeprice} < {self.checklist[market]['outprice']}")
                    self.endlist.update({market:order})
                    self.locklist.update({market:order})

            

        elif market not in self.checklist.keys() and market in self.finallist.keys():
        #           봇은 안돌아가고                           진입에는 있다면
        #진입에서 매도를 할거임. 봇이 끝난 매도
            order={
                "id": self.timestamp_id(), 
                "market":market,
                "type": "sell",
                "amount": self.asset[market],
                "price":0,
                "progress" : 4
                }
            self.endlist.update({market:order})


        elif market in self.checklist.keys() and market not in self.finallist.keys():
        #           봇은 돌아가는데                         진입에 없다면
        #final list에 추가하면서 진입을 하는거임
            self.finallist.update({market:self.checklist[market]})



        progress=self.finallist[market]["progress"]

        return self.check_progress(market, progress)



    def check_progress(self, market, progress):

        orderlist=[]

        if progress==0:     #아직 거래 안된거
            print(f"채결이 안됨.")
            orderlist.append(self.finallist[market])
            self.finallist[market]["progress"]=9
        
        elif progress==1:   #매수 완료됬으니 실행하고
            if market in self.endlist.keys ():  #매도 리스트가 있다면 매도하고
                print(f"매수가 완료되어서 매도를 신청할거임")
                self.finallist.update({market:self.endlist[market]})
                print(f"endlist를 삭제할거임. 왜냐? 봇이 끝나서 매도를 걸었다가 뺄거기 때문에")
                del self.endlist[market]
                orderlist.append(self.finallist[market])

                
        elif progress==2:   #봇이 끝나서 매도 신청하면 2로 됨
            print(f"봇이 종료되어 매도를 신청하면 여기로 들어올거임")

        elif progress==3: 
            print(f"익절로 매도를 신청하면 여기로 들어올거임")

        elif progress==4:
            print(f"봇이 종료되어 매도를 신청하면 여기로 들어올거임")

        elif progress==5:   #손절 혹은 익절을 한거면 3으로 됨
            print(f"익절로 매도가 완료되면 봇이 돌 때 까지 가만히 있을거임")
            if market in self.endlist.keys():
                del self.endlist[market]
                del self.finallist[market]
            if market in self.checklist.keys():
                del self.checklist[market]
            

        elif progress==6:
            # 모든것이 끝나서 다 삭제를 할거임.
            print(f"final list랑 모든걸 삭제할거임")
            if market in self.endlist.keys():
                del self.endlist[market]
                del self.finallist[market]
            if market in self.checklist.keys():
                del self.checklist[market]

        if orderlist:
            return orderlist
        
        return None





    def update_result(self, response):
        #임시로 콜백받아서 수량을 적을거임.
        #"amount": self.finallist[market]["amount"] 이걸 수정
        #print(f"response : {response}")
        market=response["code"]
        #거래량을 저장하고 asset에
        if "volume" in response:
            self.asset.update({market:response["volume"]})

     
        if "ask_bid" in response:
            tradetime=self.data_process.getnow()

            #매수라면
            if response['ask_bid']=='BID':
                #자동매매일 때
                if market in self.finallist.keys():
                    self.finallist[market]["progress"]=1
                    self.finallist[market]["targetprice"]=response['price']+(response['price']*self.profit)
                    self.finallist[market]["outprice"]=response['price']-(response['price']*self.stoploss)
                    print(f"###{tradetime}### {market} 시장가 매수 주문이 {response['price']}에 성공하였습니다 ###", end="")
                    print(f"목표가 :{self.checklist[market]['targetprice']} | 손절가 {self.checklist[market]['outprice']}")

            elif response['ask_bid']=='ASK':
                if market in self.finallist.keys():
                    self.finallist[market]["progress"]+=2
                    del self.endlist[market]

                    print(f"###{tradetime}### {market} 시장가 매도 주문이 {response['price']}에 성공하였습니다 ###")
        
        print("-----------------------")



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

        for market in self.checklist.keys():

            try:
                current_value = dicts[market][self.finallist[market]["trueprice"]]['BID']
                if current_value <3:
                    sellbool=True
            except KeyError:
                sellbool=True

            if sellbool:
                tradetime=self.data_process.getnow()
                print(f"{tradetime} : {market} 봇 종료 : - 처리 수량 : {self.asset[market]}")
                if market not in self.asset.keys():
                    print(f"{market} 봇이 끝났지만 잔고가 없음")
                    return

                dellist.append(market)

                
        for market in dellist:
            # print(f"{market}을 삭제합니다. -> {self.checklist}")
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
