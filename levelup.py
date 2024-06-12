import multiprocessing as mp
from uptrader import uptradertest
import requests
import time
from datetime import datetime
from decimal import Decimal
import pprint
import locale

class abc:
    
    ISO_DATEFORMAT = "%Y-%m-%dT%H:%M:%S"
    def __init__(self):
        print("abc")

    def run(self):
        
        url = "https://api.upbit.com/v1/ticker?markets="

        headers = {"accept": "application/json"}
        
        response = requests.get(url, headers=headers)

        print(response.text)

            #모든 마켓들 이름만 가져옴
        #모든 마켓들 이름만 가져옴
    def allmarket(self):
        

        url = "https://api.upbit.com/v1/market/all?isDetails=true"

        headers = {"accept": "application/json"}
        print(headers)
        res = requests.get(url, headers=headers)
        print(res)
        current = res.json()
        markets = [item['market'] for item in current if 'KRW' in item['market']]

        return markets
    
    #모든 마켓들을 한번에 전송해서 값을 가져옴
    def get_changerate(self, markets):
        changerates = {}
        print(markets)
        market=markets = ','.join(markets)
        print("1")
        url = f"https://api.upbit.com/v1/ticker?markets={market}"
        print("2")
        headers = {"accept": "application/json"}
        print("3")
        response = requests.get(url, headers=headers)
        print("4")
        response.raise_for_status()
        print("5")
        data = response.json()

        return data

    def timestamp_id(self):
        """unixtime(sec) + %M%S 형태의 문자열 반환"""
        time_prefix = round(time.time() * 1000)
        now = datetime.now()
        now_time = now.strftime("%H%M%S")
        return f"{time_prefix}.{now_time}"

    def update_process(self):
        return {
            "market":"KRW-CTC",
            "side": "buy",
            "price": 1120,
            "amount": round(50000 / 1),
            "order_type":"market",
            "profit" : 0.05,
            "stoploss" : 0.02
        }
        
    
    def create_buy(self, request):
        now = datetime.now().strftime(self.ISO_DATEFORMAT)  #시간넣기
        #지정가 시장가 지정
        budget = request['amount']
        budget -= budget * 0.00005    #수수료 더하기
        price = float(request['price'])             #진입 가격
        amount = budget / price           
        final_value = amount * price 
        if request["order_type"]=="market":
            return {
                "market":request['market'],
                "id": self.timestamp_id(),     #진입 id
                "type": "buy",                          #진입 buy
                "price": str(price),                    #진입가
                "amount": str(amount),      #수량
                "date_time":now
            }
        elif request["order_type"]=="price":        #시장가
            return {
                "market":request['market'],
                "id": self.timestamp_id(),     #진입 id
                "type": "buy",                          #진입 buy
                "date_time":now,
                "amount":0,
                "price": str(final_value)                #총액
            }




if __name__ == "__main__":
    abcd=abc()
    trader=uptradertest()
    
    sttt=abcd.allmarket()
    ass=abcd.get_changerate(sttt)
    print(ass)
    # request=[]
    # request.append(abcd.create_buy(getre))


    # def send_request_callback(result):
    #     print(f"콜백 ! - {result}")

    # trader.send_request(request, send_request_callback)


