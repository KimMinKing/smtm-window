import os
import copy
import uuid
from datetime import datetime
import threading
import hashlib
from urllib.parse import urlencode, unquote
import requests
import jwt  # PyJWT
from worker import Worker
from log_manager import LogManager
class uptradertest:

    RESULT_CHECKING_INTERVAL = 5
    ISO_DATEFORMAT = "%Y-%m-%dT%H:%M:%S"

    NAME = "Upbit"
    
    def __init__(self, budget=1000000, commission_ratio=0.0005, opt_mode = True):

        self.order_map = {}
        self.logger = LogManager.get_logger(__class__.__name__)
        self.worker=Worker("UpbitTrader-Worker")
        self.worker.start()
        self.ACCESS_KEY = os.environ["UPBIT_OPEN_API_ACCESS_KEY"]
        self.SECRET_KEY = os.environ["UPBIT_OPEN_API_SECRET_KEY"]
        self.SERVER_URL = 'https://api.upbit.com'
        self.is_opt_mode = opt_mode
        self.balance=budget
        self.commission_ratio = commission_ratio

        # self.asset = (0, 0)  # avr_price, amount
        # self.balance = budget
        # self.commission_ratio = commission_ratio


    def send_request(self, request_list, callback):
        """거래 요청을 처리한다

        request_list: 한 개 이상의 거래 요청 정보 리스트
        [{
            "market" : 거래마켓
            "id": 요청 정보 id "1607862457.560075"
            "type": 거래 유형 sell, buy, cancel
            "price": 거래 가격
            "amount": 거래 수량
            "date_time": 요청 데이터 생성 시간
        }]
        callback(result):
        {
            "request": 요청 정보
            "type": 거래 유형 sell, buy, cancel
            "price": 거래 가격
            "amount": 거래 수량
            "state": 거래 상태 requested, done
            "msg": 거래 결과 메세지
            "date_time": 거래 체결 시간
        }
        """
        
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
        request = task["request"]
        if request is None:
            print(request)
            return

        if request["type"] == "cancel":
            self.cancel_request(request["id"])
            return
        
        if "price" in request:
            pass
        else:
            request["price"] = 0
            
        is_buy = request["type"] == "buy"

        if is_buy and float(request["price"]) * float(request["amount"]) > self.balance:
            request_price = float(request["price"]) * float(request["amount"])
            self.logger.warning(
                f"계좌가 너무 작아요! {request_price} > {self.balance}"
            )
            return
        
        #오더 주문을 넣어서 값이 들어왔어
        response = self._send_order(
            request["market"], is_buy, request["price"], volume=request["amount"]
        )
        if response is None:
            task["callback"]("error!")
            return
        
        #print(f"response : {response}")
                
        #result에 요청된 이라고 저장되었어.
        result = self._create_success_result(request)
        self._check_order_result(response, result)  #값 잘 들어갔나 확인
        self.order_map[request["id"]] = {
            "uuid": response["uuid"],
            "callback": task["callback"],
            "result": result,
        }
        task["callback"](result)
        self.logger.debug(f"주문 추가 {self.order_map[request['id']]}")
        self.post_query_result_task()       #결과 업데이트 하는 큐 추가?

    def _send_order(self, market, is_buy, price=None, volume=None):
        self.logger.info(f"주문 ##### {'매수' if is_buy else '매도'}")
        self.logger.info(f"{market}, 가격 : {price}, 수량 : {volume}")
        

        if price !=0 and volume != 0:    #코인가격과 수량이 존재하면 지정가
            # 지정가 주문
            final_price = price
            query = self._create_limit_order_query(
                market, is_buy, final_price, volume
            )
            
        elif volume != 0 and is_buy is False:
            # 시장가 매도
            self.logger.warning(f"### {market} 시장가 매도 주문이 접수되었습니다 ###")
            query = self._create_market_price_order_query(market, volume=volume)

        elif price !=0 and is_buy is True:
            # 시장가 매수
            self.logger.warning(f"### {market} 시장가 매수 주문이 접수되었습니다 ###")
            query = self._create_market_price_order_query(market, price=price)

        else:
            # 잘못된 주문
            self.logger.error("trader에 잘못된 주문이 들어왔습니다")
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
            self.logger.error(f"Invalid data from server: {err}")
            return None
        except requests.exceptions.HTTPError as msg:
            print(response.json())
            self.logger.error(msg)
            return None
        except requests.exceptions.RequestException as msg:
            print("###########")
            self.logger.error(msg)
            return None
        
        return result
    


    def _execute_order2(self, task):
        # request = task["request"]
        request=task

        if request["type"] == "cancel":
            self.cancel_request(request["id"])
            return

        if request["price"] == 0:
            self.logger.warning("[REJECT] market price is not supported now")
            return

        is_buy = request["type"] == "buy"
        
        if is_buy and float(request["price"]) * float(request["amount"]) > self.balance:
            request_price = float(request["price"]) * float(request["amount"])
            self.logger.warning(
                f"[REJECT] balance is too small! {request_price} > {self.balance}"
            )
            task["callback"]("error!")
            return

        if is_buy is False and float(request["amount"]) > self.asset[1]:
            self.logger.warning(
                f"[REJECT] invalid amount {float(request['amount'])} > {self.asset[1]}"
            )
            task["callback"]("error!")
            return

        #오더 주문을 넣어서 값이 들어왔어
        response = self._send_order(
            request["market"], is_buy, request["price"], volume=request["amount"]
        )
        if response is None:
            task["callback"]("error!")
            return
        
        #result에 요청된 이라고 저장되었어.
        result = self._create_success_result(request)

        self._check_order_result(response, result)


    def _check_order_result(self, response, result):
        # 주문 결과를 확인하고 처리하는 로직을 여기에 구현
        # response와 result를 기반으로 주문 상태를 확인하고 적절한 처리를 수행
        # 예를 들어, 주문이 성공적으로 처리되었는지 확인하고 결과를 콜백 함수에 전달하는 등의 작업을 수행
        print(f"trader-check_order_response -> {response}")
        print(f"trader-check_order_result -> {result}")



    def cancel_request(self, request_id):
        """거래 요청을 취소한다
        request_id: 취소하고자 하는 request의 id
        """
        if request_id not in self.order_map:
            return

        order = self.order_map[request_id]
        del self.order_map[request_id]
        result = order["result"]
        response = self._cancel_order(order["uuid"])    #주문을 취소한다. 리턴을 받음

        if response is None:
            # 이미 체결된 경우, 취소가 안되므로 주문 정보를 조회
            response = self._query_order_list([order["uuid"]])
            if len(response) > 0:
                response = response[0]
            else:
                return

        self.logger.debug(f"canceled order {response}")
        result["date_time"] = response["created_at"].replace("+09:00", "")
        # 최종 체결 가격, 수량으로 업데이트
        result["price"] = (
            float(response["price"]) if response["price"] is not None else 0
        )
        result["amount"] = float(response["executed_volume"])
        result["state"] = "done"
        print(f"call_callback 입니다 {result}")
        self._call_callback(order["callback"], result)


    def _cancel_order(self, request_uuid):
        """
        Upbit에 취소 주문 전송

        request:
            request_uuid: 취소할 주문의 UUID, String

        response:
            uuid: 주문의 고유 아이디, String
            side: 주문 종류, String
            ord_type: 주문 방식, String
            price: 주문 당시 화폐 가격, NumberString
            avg_price: 체결 가격의 평균가, NumberString
            state: 주문 상태, String
            market: 마켓의 유일키, String
            created_at: 주문 생성 시간, String
            volume: 사용자가 입력한 주문 양, NumberString
            remaining_volume: 체결 후 남은 주문 양, NumberString
            reserved_fee: 수수료로 예약된 비용, NumberString
            remaining_fee: 남은 수수료, NumberString
            paid_fee: 사용된 수수료, NumberString
            locked: 거래에 사용중인 비용, NumberString
            executed_volume: 체결된 양, NumberString
            trade_count: 해당 주문에 걸린 체결 수, Integer
        """
        self.logger.info(f"CANCEL ORDER ##### {request_uuid}")

        query = {
            "uuid": request_uuid,
        }
        query_string = urlencode(query).encode()

        jwt_token = self._create_jwt_token(
            self.ACCESS_KEY, self.SECRET_KEY, query_string
        )
        authorize_token = "Bearer {}".format(jwt_token)
        headers = {"Authorization": authorize_token}

        try:
            response = requests.delete(
                self.SERVER_URL + "/v1/order", params=query_string, headers=headers
            )
            response.raise_for_status()
            result = response.json()
        except ValueError as err:
            self.logger.error(f"Invalid data from server: {err}")
            return None
        except requests.exceptions.HTTPError as msg:
            self.logger.error(msg)
            return None
        except requests.exceptions.RequestException as msg:
            self.logger.error(msg)
            return None

        return result
    

    def _query_order_list(self, uuids, is_done_state=True):
        """
        Upbit에 주문 리스트 요청
        전달 받은 uuid 리스트에 대한 주문 상태를 조회한다

        response:
            uuid: 주문의 고유 아이디, String
            side: 주문 종류, String
            ord_type: 주문 방식, String
            price: 주문 당시 화폐 가격, NumberString
            state: 주문 상태, String
            market: 마켓의 유일키, String
            created_at: 주문 생성 시간, DateString
            volume: 사용자가 입력한 주문 양, NumberString
            remaining_volume: 체결 후 남은 주문 양, NumberString
            reserved_fee: 수수료로 예약된 비용, NumberString
            remaining_fee: 남은 수수료, NumberString
            paid_fee: 사용된 수수료, NumberString
            locked: 거래에 사용중인 비용, NumberString
            executed_volume: 체결된 양, NumberString
            trade_count: 해당 주문에 걸린 체결 수, Integer
        """
        query_states = ["wait", "watch"]
        if is_done_state:
            query_states = ["done", "cancel"]

        states_query_string = "&".join(
            ["states[]={}".format(state) for state in query_states]
        )
        uuids_query_string = "&".join(["uuids[]={}".format(uuid) for uuid in uuids])
        query_string = "{0}&{1}".format(
            states_query_string, uuids_query_string
        ).encode()

        jwt_token = self._create_jwt_token(
            self.ACCESS_KEY, self.SECRET_KEY, query_string
        )
        authorize_token = "Bearer {}".format(jwt_token)
        headers = {"Authorization": authorize_token}

        return self._request_get(
            self.SERVER_URL + "/v1/orders", params=query_string, headers=headers
        )


    

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
    

    def _create_success_result(self, request):
        return {
            "state": "requested",
            "request": request,
            "type": request["type"],
            "price": request["price"],
            "amount": request["amount"],
            "msg": "success",
        }
    

    def post_query_result_task(self):
        self.worker.post_task({"runnable": self._update_order_result})



    def _update_order_result(self, task):
        # task는 사용되지 않으므로 삭제한다
        del task
        
        # 대기 중인 주문의 UUID들을 모으기 위한 빈 리스트를 생성한다
        uuids = []
        # 대기 중인 주문 목록을 순회하며 UUID를 수집한다
        for request_id, order in self.order_map.items():
            uuids.append(order["uuid"])

        # UUID가 없으면 아무 작업도 수행하지 않는다
        if len(uuids) == 0:
            return

        # 대기 중인 주문들의 UUID를 사용하여 주문 결과를 조회한다
        results = self._query_order_list(uuids)
        # 조회 결과가 없으면 아무 작업도 수행하지 않는다
        if results is None:
            return

        # 대기 중인 요청을 담을 딕셔너리를 초기화한다
        waiting_request = {}
        # 대기 중인 주문들을 순회하며 처리 여부를 확인한다
        for request_id, order in self.order_map.items():
            is_done = False
            # 주문 결과 목록을 순회하며 해당 주문의 결과를 찾는다
            for query_result in results:
                if order["uuid"] == query_result["uuid"]:
                    # 주문 결과를 찾으면 로그를 출력한다
                    self.logger.debug("완료된 주문 발견! =====")
                    # self.logger.debug(order)
                    # self.logger.debug(query_result)
                    # 주문 결과를 업데이트한다
                    result = order["result"]
                    result["date_time"] = query_result["created_at"].replace(
                        "+09:00", ""
                    )
                    # 최종 체결 가격이 있으면 업데이트하고, 없으면 0으로 설정한다
                    if "price" in query_result:  
                        result["price"] = (
                            float(query_result["price"])
                        )
                    else: result["price"]=0

                    # 체결된 양을 업데이트한다
                    result["amount"] = float(query_result["executed_volume"])
                    # 주문 상태를 'done'으로 설정한다
                    result["state"] = "done"
                    # 콜백 함수를 호출하여 결과를 반환한다
                    self._call_callback(order["callback"], result)
                    # 처리가 완료되었음을 표시한다
                    is_done = True

            # 처리가 완료되지 않은 주문은 대기 목록에 추가한다
            if is_done is False:
                #self.logger.debug(f"대기하는 주문 {order}")
                waiting_request[request_id] = order
        
        # 대기 중인 주문 목록을 업데이트한다
        self.order_map = waiting_request
        # 대기 중인 주문 개수를 로그로 출력한다
        self.logger.debug(f"나중에 업데이트, 주문 대기 개수 {len(self.order_map)}")
        


        # if len(self.order_map) > 0:
        #     self.post_query_result_task()

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

        result["balance"] = int(float(data_list[0]["balance"]))

        for item in data_list:

            market = f"KRW-{item['currency']}"
            result["asset"][market] = {
                "average_price": float(item["avg_buy_price"]),
                "quantity": float(item["balance"])
            }

            if market in markets:
                for utem in market_info:
                    if utem['market']==market:
                        #print(utem)
                        result["quote"][market] = float(utem["trade_price"])

        # result["quote"][self.market_currency] = float(trade_info[0]["trade_price"])
        self.logger.debug(f"account info {result}")
        return result


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
        print(headers)
        res = requests.get(url, headers=headers)
        print(res)
        current = res.json()
        markets = [item['market'] for item in current if 'KRW' in item['market']]

        return markets
    

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
    

    
    def _request_get(self, url, headers=None, params=None):
        try:
            if params is not None:
                response = requests.get(url, params=params, headers=headers)
            else:
                response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
        except ValueError as err:
            self.logger.error(f"Invalid data from server: {err}")
            return None
        except requests.exceptions.HTTPError as msg:
            self.logger.error(msg)
            return None
        except requests.exceptions.RequestException as msg:
            self.logger.error(msg)
            return None

        return result


    def _call_callback(self, callback, result):
        result_value = float(result["price"]) * float(result["amount"])
        fee = result_value * self.commission_ratio

        # if result["state"] == "done" and result["type"] == "buy":
        #     self.balance -= round(result_value + fee)
        # elif result["state"] == "done" and result["type"] == "sell":
        #     self.balance += round(result_value - fee)

        callback(result)

