import requests


class UpbitMarket:

    def __init__(self, count=None):
        self.count = count

    def getmarketname(self):
        url = "https://api.upbit.com/v1/market/all"
        response = requests.get(url)
        markets = response.json()
        market_names = [market['market'] for market in markets]
        return str(market_names)
    
    def tostr(self, lists):

        try:
            return str(lists)
        except ValueError as e:
            print(e)


    def marketper(self, min=10):
        #10rest로 10분 전 애들을 구하는거 
        pass
    