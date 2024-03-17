import requests
import pprint
import locale
import time
import pandas as pd
from upbittickdataprovider import UpbitTickProvider


class UpbitMarket:

    def __init__(self, count=500, backtest=None):
        self.count=count
        self.backtest=backtest
        print("upbitmarket 입장")



    def pdsetting(self):
        pd.set_option('display.float_format', lambda x: '%.3f' % x)
        # row 생략 없이 출력
        pd.set_option('display.max_rows', 150)
        # col 생략 없이 출력
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)


    #모든 마켓들을 한번에 전송해서 값을 가져옴
    def get_changerate(self, markets):
        changerates = {}
        market=result = ','.join(markets)
        url = f"https://api.upbit.com/v1/ticker?markets={market}"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        df=pd.DataFrame(data)
        return df

    #모든 마켓들 한번에 틱 데이터 가져옴?
    def ticks_markets():
        pass

    #모든 마켓들 이름만 가져옴
    def allmarket(self):
        

        url = "https://api.upbit.com/v1/market/all?isDetails=true"

        headers = {"accept": "application/json"}

        res = requests.get(url, headers=headers)

        current = res.json()
        markets = [item['market'] for item in current if 'KRW' in item['market']]

        return markets

    #모든 데이터를 보기좋게 가공함
    def betterlook(self, markets):
            # 남겨야 하는 컬럼들 선택
        selected_columns = ['market', 'trade_time_kst', 'opening_price','high_price','trade_price','prev_closing_price','change','signed_change_rate','trade_volume','acc_trade_price','acc_trade_volume_24h','timestamp']

        # 새로운 데이터프레임 생성
        new_df = markets[selected_columns].copy()
        new_df.rename(columns={'trade_time_kst': 'time', 'opening_price':'open', 'high_price':'high', 'prev_closing_price':'last', 'signed_change_rate':'percent','acc_trade_volume_24h':'acc24vol'}, inplace=True)

        # 'market' 열을 인덱스로 설정
        new_df.set_index('market', inplace=True)
        new_df=new_df.sort_values(by='percent', ascending=False)

        new_df.to_csv('data.csv', encoding='utf-8-sig',index=True)
        return new_df


    def plusmarket(self,market):
        plmarket= market[market['percent'] > 0]

        marketlist=plmarket.index.tolist()
        return marketlist


    # market=allmarket()


    # price=pd.DataFrame(get_changerate(market))

    # data=gagong(price)


    # print(len(data))
# 실행 코드
if __name__ == "__main__":
    test=UpbitMarket()
    markets=test.allmarket()
    markets=test.get_changerate(markets)
    ret=test.betterlook(markets)
    plusmarket=test.plusmarket(ret)
    
    print(len(plusmarket))