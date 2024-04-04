import logging
import os
import jwt  # PyJWTimport uuid
import hashlib
from urllib.parse import urlencode, unquote
import requests
import uuid
import numpy as np
import winsound as sd

logging.basicConfig(level=logging.DEBUG)

ACCESS_KEY = os.environ["UPBIT_OPEN_API_ACCESS_KEY"]
SECRET_KEY = os.environ["UPBIT_OPEN_API_SECRET_KEY"]

def send_order(query):
    query_string = unquote(urlencode(query, doseq=True)).encode("utf-8")
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    print(query)
    res = requests.post('https://api.upbit.com' + '/v1/orders', json=query, headers=headers)

    print(res.json())
    return res

def yte():
    botmoney = np.array([147000, 157000, 201000, 210000, 219000])
    botmoneyalpha = 8000
    total=201000
    differences = botmoney- total
    botpricetrue = (differences >= 0)
    botpricetrue = differences < botmoneyalpha
    print(differences)
    print(botpricetrue)
    selected_values = (differences >= 0) & (differences < 8000)
    print(f"sel : {selected_values}")
    trueindexlist=np.where(botpricetrue)[0] 
    trueprice=botmoney[min(trueindexlist)]
    print(trueprice)

def calculate_order_quantity(self, symbol, investment_amount):
        # 현재 시장 가격 가져오기
        price_data = self.binance_client.futures_symbol_ticker(symbol=symbol)
        current_price = float(price_data['price'])

        # 거래소의 최소 및 최대 주문 수량 조건 및 주문 단위(step size) 확인
        min_qty, max_qty, step_size = self.get_lot_size(symbol)

        # 최소 노셔널 값 조건 고려 (최소 20 USDT)
        min_notional = 20
        if investment_amount < min_notional:
            investment_amount = min_notional

        # 주문 수량 계산 (레버리지 이미 적용된 investment_amount 사용)
        order_quantity = investment_amount / current_price

        # 주문 수량을 거래소의 조건에 맞게 조정
        order_quantity = self.adjust_quantity_to_lot_size(order_quantity, min_qty, max_qty, step_size)

        # 소수점 두 자리까지 반올림
        order_quantity = round(order_quantity, 2)

        return order_quantity

def adjust_price_to_unit(price):
    # 가격 단위에 맞게 가격을 조정하는 함수
    steps = [(2000000, 1000), (1000000, 500), (500000, 100), (100000, 50),
             (10000, 10), (1000, 1), (100, 0.1), (10, 0.01), (1, 0.001),
             (0.1, 0.0001), (0.01, 0.00001), (0.001, 0.000001),
             (0.0001, 0.0000001), (0, 0.00000001)]
    for step, unit in steps:
        if price >= step:
            return round(price / unit) * unit
    return price


params = {
    'market': 'KRW-BTC',
    'side': 'bid',
    'ord_type': 'limit',
    'price': '1300',
    'volume': '10'}

if __name__ == '__main__':
    result = send_order(params)
    abc=adjust_price_to_unit(1290.74)
    print(abc)