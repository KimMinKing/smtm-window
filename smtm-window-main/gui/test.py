import requests
import pandas as pd
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# URL = "https://api.upbit.com/v1/trades/ticks"
start = time.time()


def save_dataframes_to_csv(datas, file_path='output.csv'):
    # CSV 파일에 데이터 추가
    for i, data in enumerate(datas, start=1):
        # DataFrame으로 변환
        df = pd.DataFrame(data, index=range(len(data)))

        
        # CSV 파일에 DataFrame 추가
        if i == 1:
            # 첫 번째 DataFrame일 때 파일을 새로 생성
            df.to_csv(file_path, encoding='utf-8-sig', index=False)
        else:
            # 나머지 DataFrame일 때 파일을 추가 모드로 열어서 추가
            df.to_csv(file_path, mode='a', encoding='utf-8-sig', index=False, header=False)



def get_url(url):
    response=requests.get(url).json()
    
    restype=type(response)
    if restype==dict:
        print(response)
        return response
    df = pd.DataFrame(response)
    return df


def botcs(df):
    botmoney = [151000, 161000, 206000, 226000, 236000]
    botmoney_array = np.array(botmoney)
    botmoneyalpha=5000

    
    id = []
    df['trade_time_utc'] = pd.to_datetime(df['trade_time_utc'], format='%H:%M:%S')

    #총 거래 금액 칼럼 추가하기
    df['total'] = df['trade_price'] * df['trade_volume']
    #총거래금액 칼럼 int형으로 만들기

    #ask , bid 변수 따로 생성
    asks = df[df['ask_bid'] == 'ASK']
    bids = df[df['ask_bid'] == 'BID']

    #ask 만큼 돌아가고 2중 for 문이야
    for aindex, ask in asks.iterrows():
        
        #bid 만큼 돌아가고
        for bindex, bid in bids.iterrows():

            #매도와 매수의 시간차를 구하고
            mtime=bid['trade_time_utc'] - ask['trade_time_utc']
            mtime=mtime.total_seconds() #초단위로 변경

            #매수와 매도의 가격차를 구한다.
            mmoney=bid['total'] - ask['total']
            
            #timecheck은 시간차가 3초 미만일 경우에만 조건 허용
            timecheck=0<=mtime<3

            #moneycheck은 매수매도의 가격이 4000보다 작아야 함.
            moneycheck=abs(mmoney) < 4000
            
            #beforecheck은 bid의 timestamp가 처음이어야 합니다. 발견된건 id로 들어간다는거죠
            beforecheck=bid['timestamp'] not in id

            if timecheck and moneycheck and beforecheck:
                #numpy로 계산 | 봇가격과 설정봇 가격들의 차를 구함
                diff = np.abs(botmoney_array - ask['total'])

                #위에 가격의 차가 들어가있음[151000-ask['total'], 161000,] 그러니까 배열에 true인게 있는지 찾는거임
                setbotcheck=np.any(diff < botmoneyalpha)

                #차이가 5000원 미만인거지
                if setbotcheck:
                    print(f"{ask['timestamp']} - {bid['timestamp']} - {mmoney} = {mtime} | {bid['total']}")

                    #고정값을 넣어서 다신 안나오게 하는거임.
                    id.append(bid['timestamp'])
                    break
            
    #         if bid['time'] - ask['time'] > 0.5:   #매도 타임이 매수보다 늦어야함
    #             if abs(bid['price']-ask['price']) > 2000:
    #                 #그러면 ask 다음 for로 넘어가는거임  
    #                 pass
    return len(id)


def botc(df):
    botmoney = np.array([151000, 161000, 206000, 226000, 236000])
    botmoneyalpha = 5000
    id = []

    df['trade_time_utc'] = pd.to_datetime(df['trade_time_utc'], format='%H:%M:%S')
    df['total'] = df['trade_price'] * df['trade_volume']
    
    asks = df[df['ask_bid'] == 'ASK']
    bids = df[df['ask_bid'] == 'BID']
    print(f"님 뭔데; {type(bids['total'])} bid 타입은 {type(bids)} df 타입은 {type(df)}")

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
            diff = np.abs(botmoney - ask['total'])
            setbotcheck=np.any(diff < botmoneyalpha)
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
                
    return len(id)


# list_of_urls = ["https://api.upbit.com/v1/trades/ticks?market=KRW-TT&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-MASK&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-APT&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-AVAX&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-KAVA&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-LINK&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-BTT&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-JST&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-TRX&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-STX&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",          
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",  
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",    
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",  
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",  
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",          
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",          
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",          
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
#                 "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",   
# ]
# print(len(list_of_urls))




lists=get_url("https://api.upbit.com/v1/trades/ticks?market=KRW-MBL&count=500")

#abc=botcs(lists)
abcs=botc(lists)
print(f"{2} -- {abcs}")



end = time.time()
print(f"---- 프로그램 실행 시간은 {round(end-start, 1)}초")



#   def new_botcheck2(self, df):
#         if df is None:
#             print("df가 없습니다.")
#             return {}

#         bot_counts = {}  # 각 마켓별 봇 개수를 저장할 딕셔너리 초기화

#         asks = df[df['ask_bid'] == 'ASK']
#         bids = df[df['ask_bid'] == 'BID']
#         id=[]

#         # asks와 bids의 모든 조합을 계산
#         for aindex, ask in asks.iterrows():
#             # 같은 시장에서만 거래
#             market = ask['market']

#             market_bids = df[df['market'] == market]
#             # asks와 bids 간의 시간 차이를 계산
#             mtime = (market_bids['trade_time_utc'] - ask['trade_time_utc']).dt.total_seconds()
#             # asks와 bids 간의 총 거래 금액 차이를 계산
#             mmoney = market_bids['total'] - ask['total']
#             timecheck = (0 <= mtime) & (mtime < 3)
#             moneycheck = abs(mmoney) < 4000
            
#             # 시간 차이와 금액 차이를 만족하는 bids 선택
#             valid_bids = market_bids[timecheck & moneycheck]
            
#             # 이전 거래 체크를 추가
#             beforecheck = ~valid_bids['timestamp'].isin(id)
            
#             # 모든 조건을 만족하는 bids 선택
#             valid_bids = valid_bids[beforecheck]
            
#             # 봇가격과의 차이 계산
#             diff = np.abs(self.botmoney - ask['total'])
#             setbotcheck = np.any(diff < self.botmoneyalpha)
#             if setbotcheck:
#                 bot_counts[market] = bot_counts.get(market, 0) + len(valid_bids)
#                 print(f"추가된 마켓 {market} - 기존 num : {bot_counts.get(market, 0)} -  추가된 num = {len(valid_bids)}")
#                 id.append(market_bids['timestamp'])
#         return bot_counts