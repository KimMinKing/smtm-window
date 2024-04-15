import requests
import math
import time


class UpbitMarket:

    def __init__(self, count=None):
        self.count = count
        self.marketname=[]
        self.marketper={}
        self.btc={}
        self.profitper=50

    def getmarketname(self):
        url = "https://api.upbit.com/v1/market/all"
        response = requests.get(url)
        markets = response.json()
        self.marketname = []  # 빈 리스트를 초기화합니다.
        for market in markets:  # markets 리스트의 각 요소에 대해 반복합니다.
            self.marketname.append(market['market'])  # markets 리스트의 각 요소의 'market' 키에 해당하는 값을 self.marketname 리스트에 추가합니다.
        return str(self.marketname)
    
    def tostr(self, lists):

        try:
            return str(lists)
        except ValueError as e:
            print(e)


    def tess(self, start):
        math.factorial(100000)
        end = time.time()

        print(f"{end - start:.5f} sec")


    def get_tickers_prices(self):
        url = f"https://api.upbit.com/v1/ticker"
        params = {"markets": ','.join(self.marketname)}
        response = requests.get(url, params=params)
        data = response.json()
        self.marketper = {}
        for ticker in data:
            if ticker['market'].startswith('KRW'):
                self.marketper[ticker['market']] = float(ticker['signed_change_rate'])


    def savebtc(self):
        self.btc = {1234:23}




    def plusmarket(self, market):
        # self.get_tickers_prices()

        # 양의 퍼센트 변화를 가진 종목들을 저장할 딕셔너리
        positive_changes = {ticker: change for ticker, change in self.marketper.items() if change > 0}

        # 음의 퍼센트 변화를 가진 종목들을 저장할 딕셔너리
        negative_changes = {ticker: change for ticker, change in self.marketper.items() if change < 0}
        # 양의 퍼센트 변화를 가진 종목들의 개수
        positive_count = len(positive_changes)
        # 음의 퍼센트 변화를 가진 종목들의 개수
        negative_count = len(negative_changes)

        # 퍼센트 변화가 3% 이상인 종목들을 저장할 딕셔너리
        significant_positive_changes = {ticker: change for ticker, change in positive_changes.items() if change >= 0.03}

        print("양의 퍼센트 변화를 가진 종목들의 개수:", positive_count)
        print("음의 퍼센트 변화를 가진 종목들의 개수:", negative_count)
        #print("퍼센트 변화가 3% 이상인 종목들:", significant_positive_changes)
        if positive_count < negative_count:    #과반수 이상이 하락 종목이어야 함. 
            self.profitper=90
        else:
            self.profitper=80

        if market in self.marketper:
            subper = self.marketper[market]
            
            if subper > 0.002:
                print(f"{market}종목은 2%보다 높습니다. {subper}")
                self.profitper=self.profitper-10
                return
            print(f"{market}종목은 2%보다 높지 않습니다. {subper}")

        
        return self.profitper


    