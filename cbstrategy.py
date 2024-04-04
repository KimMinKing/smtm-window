import copy
import time
import json
import numpy as np
from datetime import datetime
from ttldict import TTLDictionary
from decimal import Decimal, ROUND_DOWN
from log_manager import LogManager
import winsound

class CBstrategy():

    """
    inInitalialized: 최초 잔고는 초기화할 때만 갱신된다.
    data : 거래 데이터 리스트, ohlcv 데이터
    result : 거래 요청 결과 리스트
    request : 마지막 거래 요청
    budget : 시작 잔고
    balance : 현재 잔고
    min_price : 최소 주문 금액
    """
    COMMISSION_RATIO = 0.0005
    ISO_DATEFORMAT = "%Y-%m-%dT%H:%M:%S"
    # botmoney = np.array([154000, 163000, 206000, 212000, 220000])
    botmoney = np.array([151000,160000, 201000, 210000, 220000, 230000])
    botmoneyalpha = 8000
    STEP=2

    def __init__(self, ttltime=3):
        self.is_intialized = False
        self.is_simulation = False
        self.rsi_info = None
        self.rsi = []
        self.data = {}
        self.result = []
        self.add_spot_callback = None
        self.budget = 0
        self.balance = 0
        self.asset_amount = 100000
        self.min_price = 0
        self.profitper=0.004
        self.stoplossper=0.0023
        #self.logger = LogManager.get_logger(__class__.__name__)
        self.waiting_request = {}
        self.position = None
        self.checklist={}
        self.blacklist=["KRW-BTC", "KRW-XRP"]
        self.selllist=[]
        self.current_process = "ready"
        self.process_unit = (0, 0)  # budget and amount
        self.marketvollist={}
        self.showprocess=False
        self.ttl = TTLDictionary(ttl=5)
        self.logger = LogManager.get_logger(__class__.__name__)
        
    def initialize(self, budget, min_price=5000, profit=0.004, stoploss=0.0023):
        """
        예산과 최소 거래 가능 금액을 설정
        """

        if self.is_intialized:
            return
        
        self.is_intialized = True
        self.budget = budget
        self.balance = 100000
        self.profitper=profit
        self.stoplossper=stoploss
        self.min_price = min_price
        #ttl 정의를 해야할듯?
        self.ttl.start_ttl()
    
    def update_trading_info(self, info):
        """
        새로운 거래 정보 업데이트
        Returns: 거래정보 딕셔녀리
        {
            "market":거래 시장 종류 KRW-BTC
            "date_time": 정보의 기준 시간
            "trade_price": 거래 가격
            "total": 거래 금액
        }
        """
        
        if self.is_intialized is not True:
            return
        
        #info 데이터를 msg로 해서 update process 로 보냄
        
        msg = json.loads(info.decode('utf-8'))  
        self.data={
            "market" : msg.get('code'),
            "trade_volume" : msg.get('trade_volume', 0),
            "trade_price" :msg.get('trade_price', 0),
            "ask_bid" : msg.get('ask_bid'),
            "time" : msg.get('trade_time'),
            "total" : msg.get('trade_volume') * msg.get('trade_price')
        }

        final_requests=[]
        get_request=None
        #데이터가 있으면 getrequest로 전달
        
        if self.data["trade_volume"]:
            #조건이 성립된다면 값이 들어가고
            get_request=self.__update_process(self.data)


        #매도리스트가 있다면    
        if len(self.selllist)>0:

            now = datetime.now().strftime(self.ISO_DATEFORMAT)  #시간넣기
            for item in self.selllist:
                item['date_time']=now
                request=self.__create_sell(item)
                final_requests.append(request)

            self.selllist.clear()
            

        #값이 들어와서 데이터 정리하기
        if get_request is not None:
            now = datetime.now().strftime(self.ISO_DATEFORMAT)  #시간넣기

            #체결안된 주문 리스트들 취소하기
            for request_id in self.waiting_request:
                print(f"취소 주문 추가! {request_id}")
                final_requests.append({
                        "id": request_id,
                        "type": "cancel",
                        "price": 0,
                        "amount": 0,
                        "date_time": now,
                    })

            #매수주문 정리
            if get_request['side']=="buy":

                request= self.__create_buy(get_request)
                print(f"_create 들어가는데 {request}")
                request["date_time"] = now  #시간 넣어주기
                final_requests.append(request)
                #익절가 매도 추가
                if get_request['profit'] is not None:
                    profit_request={
                        "market":get_request['market'],
                        "side": "sell",
                        "price": self.adjust_price_to_unit(get_request['price']+get_request['price']*get_request['profit']),
                        "amount": self.marketvollist[get_request['market']],
                        "order_type": "limit",
                        "date_time": now
                    }

                    sellrequest= self.__create_sell(profit_request)

                    final_requests.append(sellrequest)

            #매도
            elif get_request['side']=="sell":
                request= self.__create_sell(get_request)
                request["date_time"] = now  #시간 넣어주기
                final_requests.append(request)
                
        return final_requests


        #print(info)
        #self.data.append(copy.deepcopy(info))

#TTL로 데이터 가공해서 보내려고
    def __update_process(self, info):
        
        market=self.data["market"]
        total=self.data["total"]
        tradeprice = self.data['trade_price']
        ask_bid=self.data["ask_bid"]
        tradetime=self.data["time"]

        if market in self.blacklist:
            return
        elif self.showprocess:
            print(f"{market} - {tradeprice} - {ask_bid} - {tradetime}")


        
        


        differences = total - self.botmoney
        
        botpricetrue = (differences >= 0) & (differences < self.botmoneyalpha)

        
        #봇가격이 아니라면 꺼져




        if botpricetrue.any():
            trueindexlist=np.where(botpricetrue)[0]     #빼기 했을 때 true 것들이 어디 있냐
            trueprice=self.botmoney[min(trueindexlist)] #15100 거기서 가장 작은 인덱스값을 가진 가격


            #마켓에 해당하는 가격이 있는거고
            if trueprice in self.ttl.dictionary[market].keys():
                current_value=0
                #2 가격이 있다면 짝수는 매도 홀수는 매수여야함.
                if self.ttl.dictionary[market][trueprice]['BID']%2 == 0:    #짝수
                    
                    if ask_bid=="ASK":   #매도라면
                            
                        current_value = self.ttl.dictionary[market][trueprice]['BID']   #매도의 숫자
                        self.ttl.dictionary[market][trueprice]['BID'] = current_value+1 #+1
                        #print(f"[{market}] - {trueprice}봇  -{int(total):,} - {tradetime} : [{tradeprice}]  - {self.ttl.dictionary[market][trueprice]['BID']}")        
                            
                elif self.ttl.dictionary[market][trueprice]['BID']%2 == 1:  #홀수
                    
                    if ask_bid=="BID":
                            
                        current_value = self.ttl.dictionary[market][trueprice]['BID']   #매도의 숫자
                        self.ttl.dictionary[market][trueprice]['BID'] = current_value+1 #+1
                        #print(f"[{market}] - {trueprice}봇  -{int(total):,} - {tradetime} : [{tradeprice}]  - {self.ttl.dictionary[market][trueprice]['BID']}")        
                            

                    #5쌍이나 있으면서 체크종목에 안들어갔다면
                    if current_value>3 and market not in self.checklist:
                        #조건 성립
                        #매수부분
                        if trueprice > 200000:          #20만 봇 특정
                            self.checklist.update({market:trueprice})
                            print(f"[{market}] - {trueprice}봇  -{int(total):,} - {tradetime} : [{tradeprice}]  - {self.ttl.dictionary[market][trueprice]['BID']}")        
                            
                            return {
                                "market":market,
                                "side": "buy",
                                "price": tradeprice,
                                "amount": round(self.balance / 2),
                                "order_type":"price",
                                "profit" : 0.04,    #4퍼센트
                                "stoploss" : 0.02
                            }

                        #그냥 15봇이다?
                        else:
                            self.checklist.update({market:trueprice})
                            
                            print(f"[{market}] - {trueprice}봇  -{int(total):,} - {tradetime} : [{tradeprice}]  - {self.ttl.dictionary[market][trueprice]['BID']}")        
                            return {
                                "market":market,
                                "side": "buy",
                                "price": tradeprice,
                                "amount": round(self.balance / 2),
                                "order_type":"price",
                                "profit" : self.profitper,
                                "stoploss" : self.stoplossper
                            }
                            
            #해당하는 가격이 없으면 가격을 넣고
            #1 제일 먼저 들어옴.  매수라면 값을 넣는다.
            elif ask_bid =="BID":
                self.ttl.add_value(market, trueprice , ask_bid)

                #시간 만료되면 
        if self.ttl.is_expired():
            callback=None
            #ttl데이터 리셋하는데 콜백으로 보여줘
            if self.checklist:
                #체크리스트를 6초에 한번씩 검사하는거야
                callback=self.callbackchecklist
            self.ttl.reset(callback)    #삭제가 되는건 맞고
            self.ttl.start_ttl()  # TTL 재설정

    def adjust_price_to_unit(self,price):
        # 가격 단위에 맞게 가격을 조정하는 함수
        steps = [(2000000, 1000), (1000000, 500), (500000, 100), (100000, 50),
                (10000, 10), (1000, 1), (100, 0.1), (10, 0.01), (1, 0.001),
                (0.1, 0.0001), (0.01, 0.00001), (0.001, 0.000001),
                (0.0001, 0.0000001), (0, 0.00000001)]
        for step, unit in steps:
            if price >= step:
                return round(price / unit) * unit
        return price

    def callbackchecklist(self, dicts):
        tradetime = self.data["time"]
        dellist = []

        # 딕셔너리 수정 대상 저장 리스트
        keys_to_remove = []
        for market in self.checklist:
            try:
                current_value = dicts[market][self.checklist[market]]['BID']
                if current_value < 2:
                    print(f"{market} 봇 종료 - {tradetime} : - 시장가 매도 수량 : {self.marketvollist[market]}")
                    keys_to_remove.append(market)
                    self.selllist.append({
                    "market":market,
                    "side": "sell",
                    "amount": self.marketvollist[market],
                    "order_type":"market",
                    })
                    

                else:
                    if self.checklist[market]>200000:
                        pass
                        # print(f"{market} : 20봇 화력은? 봇 개수 : {current_value}")

            except KeyError:
                
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

        
        

    def update_result(self, result):
        """
        요청한 거래의 결과 업데이트
        
        request : 거래 요청 정보
        result :
        {
            "request": 요청정보
            "type" : 유형
            "price" 거래 가격
            "amount" : 거래 수량
            "msg" : 거래 결과 메세지
            "state" : 거래 상태 requested, done
            "date_time" : 시간
        }
        """
        # print("update result 들어오고")
        
        if self.is_intialized is not True:
            return
        
        try:        #거래 결과상태가 request 인 경우 실제 처리는 되지 않은 상태이므로 waiting 딕셔너리 저장
            request = result["request"]
            if result["state"] == "requested":
                print(f"state request 추가 {result}")
                self.waiting_request[request['id']] = result
                return
            
            if result["state"] == "done" and request["id"] in self.waiting_request:      #상태가 done일 때 삭제
                del self.waiting_request[request['id']]

            
            total= float(result['price']) * float(result['amount']) #총 거래 금액   
            fee = total * self.COMMISSION_RATIO

            # if result['type'] == "buy":
            #     self.balance -= round(total + fee)
            #     print(f"update result = balance : {self.balance} -= total : {total} + fee : {fee}")
            # else:
            #     self.balance += round(total - fee)
            #     print(f"update result = balance : {self.balance} += total : {total} - fee : {fee}")
            
            self.logger.info(f"[RESULT] id: {result['request']['id']} ================")
            self.logger.info(f"type: {result['type']}, msg: {result['msg']}")
            self.logger.info(f"price: {result['price']}, amount: {result['amount']}")
            self.logger.info(f"balance: {self.balance}, asset_amount: {self.asset_amount}")
            self.logger.info("================================================")
            self.result.append(copy.deepcopy(result))
        except (AttributeError, TypeError) as msg:
            self.logger.error(msg)


    @classmethod
    def timestamp_id(self, cls):
        """unixtime(sec) + %M%S 형태의 문자열 반환"""
        time_prefix = round(time.time() * 1000)
        now = datetime.now()
        now_time = now.strftime("%H%M%S")
        return f"{time_prefix}.{now_time}"
    


    def __create_buy(self, request):
        budget = request['amount']
        if budget > self.balance:   
            budget = self.balance
        # print(f"budget : {budget}")
        budget -= budget * self.COMMISSION_RATIO    #수수료 더하기
        price = float(request['price'])             #진입 가격

        amount = budget / price                     #진입할 금액 / 가격 = 수량
        # print(f"amount : {amount}")

        final_value = amount * price                #수량*금액 = 진입할 진짜 금액
        print(f"marketvol 저장하는데 {amount} = {budget} / {price} | final : {final_value} realbud : {request['amount']} selfbalance = : {self.balance}")
        self.marketvollist.update({request['market']:amount})
        print(f"volist append : {self.marketvollist}")
        # 소숫점 4자리 아래 버림
        amount = Decimal(str(amount)).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
        


        #최소주문금액이 진입할 금액보다 크다면 진입 ㄴ
        if (self.min_price > budget or request['amount'] <= 0 or final_value > self.balance):
            print(f"minprice({self.min_price}) > budget({budget}) or amount({request['amount']}) <=0 or final({final_value}) > bal({self.balance})")
            self.logger.info(
                f"target_budget is too small or invalid unit {request['amount']}"
            )
            if self.is_simulation:
                return {
                    "id": self.timestamp_id(),
                    "type": "buy",
                    "price": 0,
                    "amount": 0,
                }
            return None
        

        #지정가 시장가 지정
        if request["order_type"]=="limit":
            return {
                "market":request['market'],
                "id": self.timestamp_id(),     #진입 id
                "type": "buy",                          #진입 buy
                "price": str(price),                    #진입가
                "amount": str(amount.normalize()),      #수량
            }
        elif request["order_type"]=="price":        #시장가
            return {
                "market":request['market'],
                "id": self.timestamp_id(),     #진입 id
                "type": "buy",                          #진입 buy
                "price": str(final_value),
                "amount":0                #총액
                
            }

    """ 
                    "market":market,
                    "side": "sell",
                    "amount": self.marketvollist[market],
                    "order_type":"market",
                    })
                    """

    def __create_sell(self, request):
        
        amount = float(request['amount'])
        if 'price' in request:        price = float(request['price'])
        else: price =0
        #보유량
        
        if Decimal(amount) > self.marketvollist[request['market']]:
            amount = float(self.marketvollist[request['market']])
            print(f"원래 수량은 {self.marketvollist}")
            print(f"현재 수량은 {request['market']} - {amount}?")

        total_value = price * amount

        # print(f"sell1 - amount:{amount} - total_value:{total_value} self_asset_amount :{self.asset_amount}")
        # 소숫점 4자리 아래 버림
        amount = Decimal(str(amount)).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)

        # print(f"sell2 - amount:{amount} - total_value:{total_value} - self.min:{self.min_price}")
        if amount <= 0 :
            print(f"too small amount {amount}")
            self.logger.info(f"asset is too small or invalid unit {request['amount']}")
            if self.is_simulation:
                return {
                    "id": self.timestamp_id(),
                    "type": "sell",
                    "price": 0,
                    "amount": 0,
                }
            return None

        #지정가 시장가 지정
        if request["order_type"]=="limit":

            return {
                "market":request['market'],
                "id": self.timestamp_id(),     #진입 id
                "type": "sell",                          #진입 buy
                "price": str(price),                    #진입가
                "amount": str(amount.normalize())    #수량
            }
        elif request["order_type"]=="market":        #시장가
            return {
                "market":request['market'],
                "id": self.timestamp_id(),     #진입 id
                "type": "sell",                         #진입 buy
                "amount": str(amount.normalize())              #총액
            }
        


    def timestamp_id(self):
        """unixtime(sec) + %M%S 형태의 문자열 반환"""
        time_prefix = round(time.time() * 1000)
        now = datetime.now()
        now_time = now.strftime("%H%M%S")
        return f"{time_prefix}.{now_time}"