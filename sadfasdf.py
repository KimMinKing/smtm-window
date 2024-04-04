import os
import jwt  # PyJWT
import uuid
import hashlib
from urllib.parse import urlencode, unquote
import requests


ACCESS_KEY = os.environ["UPBIT_OPEN_API_ACCESS_KEY"]
SECRET_KEY = os.environ["UPBIT_OPEN_API_SECRET_KEY"]
SERVER_URL = os.environ["UPBIT_OPEN_API_SERVER_URL"]

def send_order():
      
    params = {
    'market': 'KRW-CTC',
    'side': 'bid',
    'ord_type': 'limit',
    'price': '1300',
    'volume': '10'
    }

    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

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
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
    'Authorization': authorization,
    }

    res = requests.post(SERVER_URL + '/v1/orders/', params=params, headers=headers)
    print(res.text)
    print(res.json())
    return res
            

def orderchance():
    params = {
    'market': 'KRW-BTC'
    }
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

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
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
    'Authorization': authorization,
    }

    res = requests.get(SERVER_URL + '/v1/orders/chance', params=params, headers=headers)

    return res.json()


def ordercheck():
    params = {
    'states[]': ['done', 'cancel']
    }
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

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
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
    'Authorization': authorization,
    }

    res = requests.get(SERVER_URL + '/v1/orders', params=params, headers=headers)
    return res.json()

def getacount():
    payload = {
        'access_key': ACCESS_KEY,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
    'Authorization': authorization,
    }

    res = requests.get(SERVER_URL + '/v1/accounts',  headers=headers)
    return res.json()

result=send_order()
print(result)

chance=orderchance()
print(chance)

orderche=ordercheck()

acount=getacount()
print(acount)