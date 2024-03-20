import time
import pandas as pd
import winsound as sd
from datetime import datetime

class KILLBOT:

    #봇 가격, 오차범위
    botmoney = [151000, 161000, 206000, 226000, 236000]
    botmoneyalpha=8000
    

    def __init__(self):
        self.botper=0
        self.botnum=0
        self.timetrue=False
        self.botlist=[]
        print("killbot에 들어옴")

    #봇이 얼마나 있나 확인 하는 전략
    def botcheck(self, df):
        

        rows_with_conditions = df[df['total'].isin(self.botmoney)]
        
        bot_df = pd.DataFrame()
        #시간차 계산
        
        # 각 조건에 대해 범위 내에 있는 행을 선택하여 새로운 DataFrame에 추가
        for moenyone in self.botmoney:
            lower_bound = moenyone
            upper_bound = moenyone + self.botmoneyalpha
            rows_in_range = df[(df['total'] >= lower_bound) & (df['total'] <= upper_bound)]
            bot_df = pd.concat([bot_df, rows_in_range], ignore_index=True)

                # ASK와 BID를 각각 필터링하여 추출
        asks = bot_df[bot_df['ask_bid'] == 'ASK']
        bids = bot_df[bot_df['ask_bid'] == 'BID']

        nonebot=abs(len(asks)-len(bids))

        self.botnum=len(bot_df)-nonebot

    #최고 시간과 최저 시간의 계산
    """500개의 데이터의 처음과 끝이 3분이 넘냐는걸 확인하는거임"""
    def sttimecheck(self,df):

        self.timetrue=False

        # 최고값과 최저값 계산
        max_time = df['trade_time_utc'].max()
        min_time = df['trade_time_utc'].min()
        # 시간 차이 계산

        time_difference = max_time - min_time

        
        #시간 차이가 3분보다 작은지 확인
        if time_difference < pd.Timedelta(minutes=2):
            #시간확인하는 변수
            self.timetrue=True
        

    #전략의 메인 부분
    def killbotstrategy(self, df):

        #df의 정보를 가져오는거 기본 정보
        first_market = df.loc[0, 'market']
        price=df.loc[0,'trade_price']
        timea=(datetime.now()).strftime("%m%d:%H:%M:%S")

        #봇 숫자 확인
        self.botcheck(df)

        #봇 퍼센트로 환산
        self.botper='%.2f%%'% (self.botnum/len(df) * 100)

        #시간 확인
        self.sttimecheck(df)


        #봇이 돌아가서 리스트 안에 있으면 ing
        boting=first_market in self.botlist

        #전략       봇의 숫자가 120보다 크고 시간이 참이며
        botcheck=self.botnum > 140  and self.timetrue

        
        #스탑되는 봇 탐지  봇리스트에 있었으며, 봇의 숫자가 줄었읆
        botstop=boting and not self.timetrue or boting and self.botnum < 120

        #전략 끝나나 확인
        if botstop:
            if self.botcheck(df.head(50))<15:
                sd.Beep(1000, 500)
                self.botlist.remove(first_market)
                print(f"{timea}---퇴출---{first_market}---가격:{price} ")

        #돌아가고 있을 때
        elif first_market in self.botlist:
            pass

        #걸렸다.
        elif botcheck:
            
            sd.Beep(1000,500)
            self.botlist.append(first_market)
            print(f"{timea}---진입---{first_market}---가격:{price} ")
            return True