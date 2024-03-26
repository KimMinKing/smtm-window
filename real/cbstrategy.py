import copy
import time
import json
import numpy as np
from datetime import datetime
from ttldict import TTLDictionary

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
    botmoney = np.array([151000, 161000, 206000, 226000, 236000])
    botmoneyalpha = 5000


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
        self.asset_amount = 0
        self.min_price = 0
        #self.logger = LogManager.get_logger(__class__.__name__)
        self.waiting_requests = {}
        self.position = None
        self.checklist={}

        self.ttl = TTLDictionary(ttl=3)
        
    def initialize(self, budget, min_price=500000):
        """
        예산과 최소 거래 가능 금액을 설정
        """

        if self.is_intialized:
            return
        
        self.is_intialized = True
        self.budget = budget
        self.balance = budget
        self.min_price = min_price
        #ttl 정의를 해야할듯?
        self.ttl.start_ttl()
        self.checklist.update({"KRW-CVC":161000})
    
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

        
        
        #데이터가 있으면 getrequest로 전달
        
        if self.data["trade_volume"]:
            self.__update_process(self.data)
            


        #print(info)
        #self.data.append(copy.deepcopy(info))

#TTL로 데이터 가공해서 보내려고
    def __update_process(self, info):

        market=self.data["market"]
        total=self.data["total"]
        ask_bid=self.data["ask_bid"]
        differences = np.abs(self.botmoney - total)
        botpricetrue = differences < self.botmoneyalpha
        #봇가격이 아니라면 꺼져
        if botpricetrue.any():
                
            trueindexlist=np.where(botpricetrue)[0]     #빼기 했을 때 true 것들이 어디 있냐
            trueprice=self.botmoney[min(trueindexlist)] #15100 거기서 가장 작은 인덱스값을 가진 가격

            #마켓에 해당하는 가격이 있는거고
            if trueprice in self.ttl.dictionary[market].keys():
                
                #매도라면 한 쌍이 된다는거죠
                if self.ttl.dictionary[market][trueprice] != ask_bid:

                    current_value = self.ttl.dictionary[market][trueprice]['BID']
                    self.ttl.dictionary[market][trueprice]['BID'] = current_value+1

                    #5쌍이나 있으면서 체크종목에 안들어갔다면
                    if current_value>=4 and market not in self.checklist:
                        #조건 성립
                        #매수부분
                        self.checklist.update({market:trueprice})
                        print(f"{market}-{int(total):,}--{trueprice} - {self.ttl.dictionary[market][trueprice]['BID']}")
                    
            #해당하는 가격이 없으면 가격을 넣고
            elif ask_bid =="BID":
                self.ttl.add_value(market, trueprice , ask_bid)

                #시간 만료되면 
        elif self.ttl.is_expired():
            #print("Dictionary TTL expired, initializing...")
            callback=None
            #ttl데이터 리셋하는데 콜백으로 보여줘
            if market in self.checklist:
                print(self.checklist)
                print(self.ttl.dictionary)
                callback=self.callbackchecklist
            self.ttl.reset(callback, market)
            self.ttl.start_ttl()  # TTL 재설정


    def callbackchecklist(self, dicts, market):
        try:
            current_value =dicts[market][self.checklist[market]]['BID']
            if current_value <4:
                del self.checklist[market]
        except KeyError:
            print(f"{market} - 삭제다~")
            del self.checklist[market]
        
        
    def get_request(self):


        """
        데이터 분석 결과에 따라 거래 요청 정보를 생성한다.
        
        Returns:
        [{
            "id":요청정보 id
            "type": 거래유형 sell, buy, cancel
            "price": 거래 가격
            "amount": 거래 수량
            "date_time":요청 데이터 생성 시간, 시뮬레이션 모드에서는 데이터 시간

        }]"""

        if self.is_intialized is not True:
            return
        

        try:

            #데이터가 없는 경우는 없어

            last_closing_price = self.data['price']    #가격정보도 함께 오고

            now = datetime.datetime.now.strftime(self.ISO_DATEFORMAT)

            target_budget = self.budget/2           #왜냐면 다른 곳에서도 봇이 나올 수 있기에 2로 나눔

            if target_budget > self.balance:        #매수하려는 금액이 > 계좌보다 크다면
                target_budget = self.balance        #계좌에 남아있는 금액으로 ㄱㄱ
            
            amount = round(target_budget / last_closing_price, 4)   #매수하려는 금액 나누기 코인 가격 (거래 수량 임) 소숫점 4자리 반올림

            trading_request ={                      #최종 거래 요청 정보
                "id" :str(round(time.time(), 3)),
                "type" :"buy",
                "price" :last_closing_price,
                "amount" :amount,
                "date_time" : now
            }

            total_value = round(float(last_closing_price) * amount)     #가격*수량 해서 

            if self.min_price > total_value or total_value > self.balance:  #잔고보다 크거나 최소 주문 금액보다 작은지
                raise UserWarning("strategy - total value or balance is too small")
            
            self.logger.info(f"[REQ] id : {trading_request['id']}======================")     #최종 거래 요청 정보의 id
            self.logger.info(f"price: {trading_request['price']}, amount : {amount}")  #최종 거래 요청 정보의 price, 거래 수량
            self.logger.info(f"================================")
            
            final_requests=[]   #체결 안되고 대기 중인 거래 요청

            for reqeust_id in self.waiting_requests:        #거래 업데이트에서 체결 안된 애들 가져오는거 만약 있으면 for 도는거고
                self.logger.info(f"cancel request added! {reqeust_id}")
                final_requests.append({
                    "id" : reqeust_id,
                    "type" :"cancel",       #cancel로 전달해버리고
                    "price" :0,
                    "amount" :0,
                    "date_time" : now
                })

            final_requests.append(trading_request)      #취소를 먼저 하고 매수 요청을 하는거지 크~

            return final_requests                       #거래 요청 정보들을 리턴하는거.
        

        except (ValueError, KeyError) as msg:       #딕셔너리에 없는 키를 참조하거나 연산이나 함수가 부적절한 인자를 받았을 때
            self.logger.error(f"strategy - invalid data  {msg}")
        except IndexError:              #릿스트나 튜플을 인덱스로 접근하려 할 때
            self.logger.error(f"strategy - empty data")
        except AttributeError as msg:  
            self.logger.error(f"strategy - {msg}")
        except UserWarning as msg:
            self.logger.error(f"strategy - {msg}")



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
        
        if self.is_intialized is not True:
            return
        
        try:        #거래 결과상태가 request 인 경우 실제 처리는 되지 않은 상태이므로 waiting 딕셔너리 저장
            request = result["request"]
            if result["state"] == "requested":
                self.waiting_request[request['id']] = result
                return
            
            if result["state"] == "done" and result["id"] in self.waiting_request:      #상태가 done일 때 삭제
                del self.waiting_request[request['id']]

            
            total= float(result['price']) * float(result['amount']) #총 거래 금액   
            fee = total * self.COMMISSION_RATIO

            if result['type'] == "buy":
                self.balance -= round(total + fee)
            else:
                self.balance += round(total - fee)

            self.logger.info(f"[RESULT] id: {result['request']['id']} ================")
            self.logger.info(f"type: {result['type']}, msg: {result['msg']}")
            self.logger.info(f"price: {result['price']}, amount: {result['amount']}")
            self.logger.info(f"balance: {self.balance}, asset_amount: {self.asset_amount}")
            self.logger.info("================================================")
            self.result.append(copy.deepcopy(result))
        except (AttributeError, TypeError) as msg:
            self.logger.error(msg)