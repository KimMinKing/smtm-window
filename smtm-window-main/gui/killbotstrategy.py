import time
import pandas as pd
import winsound as sd
from datetime import datetime
import numpy as np

class KILLBOT:

    #봇 가격, 오차범위
    botmoney = np.array([151000, 161000, 206000, 226000, 236000])
    botmoneyalpha=5000
    

    def __init__(self):
        self.botper=0
        self.botnum=0
        self.timetrue=False
        self.botlist=[]
        print("killbot에 들어옴")


        
    def new_botcheck2(self, df):
        if df is None:
            print("df가 없습니다.")
            return {}

        bot_counts = {}  # 각 마켓별 봇 개수를 저장할 딕셔너리 초기화

        asks = df[df['ask_bid'] == 'ASK']
        bids = df[df['ask_bid'] == 'BID']
        id=[]

        # asks와 bids의 모든 조합을 계산
        for aindex, ask in asks.iterrows():
            # 같은 시장에서만 거래
            market = ask['market']

            market_bids = df[df['market'] == market]
            # asks와 bids 간의 시간 차이를 계산
            mtime = (market_bids['trade_time_utc'] - ask['trade_time_utc']).dt.total_seconds()
            # asks와 bids 간의 총 거래 금액 차이를 계산
            mmoney = market_bids['total'] - ask['total']
            timecheck = (0 <= mtime) & (mtime < 3)
            moneycheck = abs(mmoney) < 4000
            
            # 시간 차이와 금액 차이를 만족하는 bids 선택
            valid_bids = market_bids[timecheck & moneycheck]
            
            # 이전 거래 체크를 추가
            beforecheck = ~valid_bids['timestamp'].isin(id)
            
            # 모든 조건을 만족하는 bids 선택
            valid_bids = valid_bids[beforecheck]
            
            # 봇가격과의 차이 계산
            diff = np.abs(self.botmoney - ask['total'])
            setbotcheck = np.any(diff < self.botmoneyalpha)
            if setbotcheck:
                bot_counts[market] = bot_counts.get(market, 0) + len(valid_bids)
                print(f"추가된 마켓 {market} - 기존 num : {bot_counts.get(market, 0)} -  추가된 num = {len(valid_bids)}")
                id.append(market_bids['timestamp'])
        return bot_counts



    #봇
    def new_botcheck(self, df):
        
        if df is None:
            print("df가 없습니다.")
            return 0

        id = []

        
        asks = df[df['ask_bid'] == 'ASK']
        bids = df[df['ask_bid'] == 'BID']

        
        
        # asks와 bids의 모든 조합을 계산
        for aindex, ask in asks.iterrows():
            # asks와 bids 간의 시간 차이를 계산
            mtime = (bids['trade_time_utc'] - ask['trade_time_utc']).dt.total_seconds()
            # asks와 bids 간의 총 거래 금액 차이를 계산
            mmoney = bids['total'] - ask['total']
            
            # 시간 차이, 금액 차이, 이전 거래 체크를 조건으로 필터링
            timecheck = (0 <= mtime) & (mtime < 3)
            moneycheck = abs(mmoney) < 4000
            beforecheck = ~bids['timestamp'].isin(id)
            
            # 모든 조건을 만족하는 bids 선택
            valid_bids = bids[timecheck & moneycheck & beforecheck]
            

            if not valid_bids.empty:
                # 봇가격과의 차이 계산
                diff = np.abs(self.botmoney - ask['total'])
                setbotcheck=np.any(diff < self.botmoneyalpha)
                if setbotcheck:
                    id.extend(valid_bids['timestamp'])

                
                # diff = np.abs(botmoney[:, np.newaxis] - ask['total'])
                # setbotcheck = np.any(diff < botmoneyalpha, axis=0)

                
                # # 조건을 만족하는 bids 선택
                # final_bids = valid_bids[setbotcheck]
                # print(f"{diff} -- {setbotcheck}")
                
                # if not final_bids.empty:
                #     print(f"{ask['timestamp']} - {final_bids.iloc[:, 'timestamp']} - {mmoney[final_bids.index]} = {mtime[final_bids.index]} | {final_bids['total']}")
                #     id.extend(final_bids['timestamp'])

        self.botnum=len(id)


    #봇이 얼마나 있나 확인 하는 전략
    def botcheck(self, df):
        
        if df is None:
            print("df가 없습니다.")
            return 0

        rows_with_conditions = df[df['total'].isin(self.botmoney)]
        
        bot_df = pd.DataFrame()
        #시간차 계산
        
        # 각 조건에 대해 범위 내에 있는 행을 선택하여 새로운 DataFrame에 추가
        for moenyone in self.botmoney:
            lower_bound = moenyone - self.botmoneyalpha
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
        if time_difference < pd.Timedelta(minutes=3):
            #시간확인하는 변수
            self.timetrue=True
        


    #전략의 메인 부분
    def killbotstrategy2(self, df):

        timea=(datetime.now()).strftime("%m%d:%H:%M:%S")
        grouped_df = df.groupby("market")

        #for문을 돌린다
        for market, market_df in grouped_df:
            self.new_botcheck3(market_df, marketname=market)
            price=market_df.iloc[0]['trade_price']
            if self.botnum>25:
                if market not in self.botlist:

                    sd.Beep(1000,1000)
                    print(f"!!!!!{timea} : {market} -- bot : {self.botnum} -- price : {price}")
                    self.botlist.append(market)
            elif market in self.botlist:
                sd.Beep(700,700)
                print(f"~~~~~{timea} : {market} -- bot : {self.botnum} -- price : {price}")
                self.botlist.remove(market)
        

    def new_botcheck3(self, market_df, marketname=None):
        #10개의 마켓이 있는데 그걸 그룹화 해서 따로 따로 쓴다는거

        # 시간 차이 계산 (첫번째 조건)
        first_condition_time_diff = pd.to_datetime(market_df.iloc[0]['trade_time_utc']) - pd.to_datetime(market_df.iloc[100]['trade_time_utc'])
        first_condition_met = first_condition_time_diff.total_seconds() < 20
        
        # 첫번째 조건이 충족되었을 때만 두번째 조건 검사
        if first_condition_met:
            #print(first_condition_time_diff.total_seconds(), "초")
            # 각 total 값과 botmoney 간의 차이 계산
            price_diffs = np.abs(market_df['total'].values[:, np.newaxis] - self.botmoney)

            # botmoneyalpha보다 작은 차이를 가지는 행의 인덱스 찾기
            valid_indices = np.where(np.min(price_diffs, axis=1) <= self.botmoneyalpha)[0]

            # botmoneyalpha보다 작은 차이를 가지는 행들을 새로운 데이터프레임에 저장
            new_df = market_df.iloc[valid_indices]


            ask_df = new_df[new_df['ask_bid'] == 'ASK']
            bid_df = new_df[new_df['ask_bid'] == 'BID']

            # 조건에 맞는 ask와 bid의 개수 파악
            ask_count = ask_df.shape[0]
            bid_count = bid_df.shape[0]

            self.botnum=min(ask_count, bid_count)
            #print(f"{marketname} - bot : {self.botnum}")

        else:
            self.botnum=0
