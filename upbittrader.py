import os
import requests
import uuid
import hashlib
import jwt  # PyJWT
from datetime import datetime
from worker import Worker
from urllib.parse import urlencode, unquote
class UpbitTrader:


    def __init__(self, budget=100000, commission_ratio=0.0005):

        self.ACCESS_KEY = os.environ["UPBIT_OPEN_API_ACCESS_KEY"]
        self.SECRET_KEY = os.environ["UPBIT_OPEN_API_SECRET_KEY"]
        self.SERVER_URL = 'https://api.upbit.com'

        self.worker=Worker("UpbitTrader-Worker")
        self.worker.start()
        self.balance=budget
        self.commission_ratio = commission_ratio

        #콜백은 잘 몰라서 strategy에 update_result로 함
    def send_request(self, request_list, callback):
        for request in request_list:
            if request is None:
                print("request 가 none이래")
                continue

            self.worker.post_task(
                {
                    "runnable": self._execute_order,
                    "request": request,
                    "callback": callback,
                }
            )


    def _execute_order(self, task):
        data = task["request"]
        request = data
        # print(f"data : {data}")
        # print(f"request : {request}")

        if data is None:
            print(data)
            return
        
        #취소 주문
        if request["type"] == "cancel":
            self.cancel_request(request["id"])
            return
        
        #매수인가?
        is_buy = request["type"] == "buy"

        #금액과 수량을 곱하는데
        amount = 1 if float(request["amount"]) == 0 else float(request["amount"])

        if is_buy and float(request["price"]) * amount > self.balance:
            request_price = float(request["price"]) * amount
            print(f"계좌가 너무 작아요!{float(request['price'])} * {amount} {request_price} > {self.balance}")
            return
        
        #주문 넣기.
        response = self._send_order(
            request["market"], is_buy, request["price"], volume=request["amount"]
        )
        if response is None:
            print("response is None 에러!")
            return

        # if float(request["amount"]) == 0:       #시장가로 매수하고 수량이 정해지지 않으면 이걸 실행
        #     response = self.getamount(response)
        # task["callback"](response)




    def getamount(self, response):
        info=self.get_account_info()
        quantity=info['asset'][response['market']]['quantity']
        response['quantity'] = quantity
        response['trades_count']=+1
        return response


    def _send_order(self, market, is_buy, price=None, volume=None):
        #print(f"주문 ##### ")
        print(f"{market} {'매수' if is_buy else '매도'} 주문 - 가격 : {price}, 수량 : {volume}")
        

        if price !=0 and volume != 0:    #코인가격과 수량이 존재하면 지정가
            # 지정가 주문
            final_price = price
            query = self._create_limit_order_query(
                market, is_buy, final_price, volume
            )
            
        elif volume != 0 and is_buy is False:
            # 시장가 매도
            # print(f"### {market} 시장가 매도 주문이 접수되었습니다 ###")
            query = self._create_market_price_order_query(market, volume=volume)

        elif price !=0 and is_buy is True:
            # 시장가 매수
            # print(f"### {market} 시장가 매수 주문이 접수되었습니다 ###")
            query = self._create_market_price_order_query(market, price=price)

        else:
            # 잘못된 주문
            print("trader에 잘못된 주문이 들어왔습니다")
            return None
        

        query_string = unquote(urlencode(query, doseq=True)).encode("utf-8")
        jwt_token = self._create_jwt_token(
            self.ACCESS_KEY, self.SECRET_KEY, query_string
        )
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}


        try:
            response = requests.post(self.SERVER_URL + "/v1/orders", json=query, headers=headers)
            response.raise_for_status()
            result = response.json()
        except ValueError as err:
            print("!!!!!!!!")
            print(f"Invalid data from server: {err}")
            return None
        except requests.exceptions.HTTPError as msg:
            print(response.json())
            print(msg)
            return None
        except requests.exceptions.RequestException as msg:
            print("###########")
            print(msg)
            return None
        
        return result




    @staticmethod
    def _create_jwt_token(a_key, s_key, query_string=None):
        payload = {
            "access_key": a_key,
            "nonce": str(uuid.uuid4()),
        }
        if query_string is not None:
            msg = hashlib.sha512()
            msg.update(query_string)
            query_hash = msg.hexdigest()
            payload["query_hash"] = query_hash
            payload["query_hash_alg"] = "SHA512"

        return jwt.encode(payload, s_key)




    
    def get_account_info(self):
        """계좌 정보를 요청한다
        Returns:
            {
                balance: 계좌 현금 잔고
                asset: 자산 목록, 마켓이름을 키값으로 갖고 (평균 매입 가격, 수량)을 갖는 딕셔너리
                quote: 종목별 현재 가격 딕셔너리
                date_time: 현재 시간
            }
        """
        result = {
            "balance": 0,  # 계좌 현금 잔고
            "asset": {},  # 자산 목록
            "quote": {},  # 종목별 현재 가격
            "date_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # 현재 시간
        }
        

        #trade_info = self.get_trade_tick()
        
        data_list = self._query_account()
        markets=self.get_market_names()
        market_info=self.get_market_info(markets)   

        #result["balance"] = int(float(data_list[0]["balance"]))

        for item in data_list:

            market = f"KRW-{item['currency']}"

            if item['currency']=="KRW":
                result["balance"]=float(item["balance"])
                
            else:
                result["asset"][market] = {
                    "average_price": float(item["avg_buy_price"]),
                    "quantity": float(item["balance"])
                }

            if market in markets:
                for utem in market_info:
                    if utem['market']==market:
                        #print(utem)
                        result["quote"][market] = float(utem["trade_price"])


        return result

    def _request_get(self, url, headers=None, params=None):
        try:
            if params is not None:
                response = requests.get(url, params=params, headers=headers)
            else:
                response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
        except ValueError as err:
            print(f"Invalid data from server: {err}")
            return None
        except requests.exceptions.HTTPError as msg:
            print(msg)
            return None
        except requests.exceptions.RequestException as msg:
            print(msg)
            return None

        return result

    def _query_account(self):
        """
        Upbit에 계좌 정보 요청

        response:
            currency: 화폐를 의미하는 영문 대문자 코드, String
            balance: 주문가능 금액/수량, NumberString
            locked: 주문 중 묶여있는 금액/수량, NumberString
            avg_buy_price: 매수평균가, NumberString
            avg_buy_price_modified: 매수평균가 수정 여부, Boolean
            unit_currency: 평단가 기준 화폐, String
        """
        jwt_token = self._create_jwt_token(self.ACCESS_KEY, self.SECRET_KEY)
        authorize_token = "Bearer {}".format(jwt_token)
        headers = {"Authorization": authorize_token}

        return self._request_get(self.SERVER_URL + "/v1/accounts", headers=headers)
    

    def get_market_info(self, markets):
        market=markets = ','.join(markets)
        url = f"https://api.upbit.com/v1/ticker?markets={market}"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        return data

    def get_market_names(self):

        url = "https://api.upbit.com/v1/market/all?isDetails=true"

        headers = {"accept": "application/json"}

        res = requests.get(url, headers=headers)

        current = res.json()
        markets = [item['market'] for item in current if 'KRW' in item['market']]

        return markets


        
    @staticmethod
    def _create_limit_order_query(market, is_buy, price, volume):
        query = {
            "market": market,
            "side": "bid" if is_buy is True else "ask",
            "volume": str(volume),
            "price": str(price),
            "ord_type": "limit",
        }
        # query_string = urlencode(query).encode()
        return query
    
    @staticmethod
    def _create_market_price_order_query(market, price=None, volume=None):
        query = {
            "market": market,
        }

        if price is None and volume is not None:    #시장가 매도
            query["side"] = "ask"
            query["volume"] = str(volume)
            query["ord_type"] = "market"
        elif price is not None and volume is None:  #시장가 매수
            query["side"] = "bid"
            query["price"] = str(price)
            query["ord_type"] = "price"
        else:
            return None

        # query_string = urlencode(query).encode()
        return query
    