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


#모든 데이터를 보기좋게 가공함
def betterlook(df):
    
    #살려둘 칼럼들
    selected_columns = ['market', 'trade_time_utc','trade_price','trade_volume','ask_bid', 'timestamp']
    new_df = df[selected_columns].copy()

    
    #총 거래 금액 칼럼 추가하기
    new_df['total'] = new_df['trade_price'] * new_df['trade_volume']
    #총거래금액 칼럼 int형으로 만들기

    #시간 타입 정하기
    new_df['trade_time_utc'] = pd.to_datetime(df['trade_time_utc'], format='%H:%M:%S')


    # #trade_time utc로 정렬해서 인덱스 재설정하기
    # new_df=new_df.sort_values(by='trade_time_utc')
    # new_df = new_df.reset_index(drop=True)
    # 종목별로 정렬하기
    sorted_df = new_df.groupby('market').apply(lambda x: x.sort_values(by='trade_time_utc')).reset_index(drop=True)


    return sorted_df

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



def new_botcheck3(market):
    market = betterlook(market)
    
    # 시간 차이 계산 (첫번째 조건)
    first_condition_time_diff = pd.to_datetime(market.iloc[-1]['trade_time_utc']) - pd.to_datetime(market.iloc[0]['trade_time_utc'])
    first_condition_met = first_condition_time_diff.total_seconds() < 50
    
    # 첫번째 조건이 충족되었을 때만 두번째 조건 검사
    if first_condition_met:
        # 총 거래 금액 칼럼 추가하기
        market['total'] = market['trade_price'] * market['trade_volume']
        
        # botmoney와의 가격 대 차이 계산 (두번째 조건)
        botmoney = np.array([151000, 161000, 206000, 226000, 236000])
        botmoneyalpha = 3800
        
        # 각 total 값과 botmoney 간의 차이 계산
        price_diffs = np.abs(market['total'].values[:, np.newaxis] - botmoney)

        # botmoneyalpha보다 작은 차이를 가지는 행의 인덱스 찾기
        valid_indices = np.where(np.min(price_diffs, axis=1) <= botmoneyalpha)[0]

        # botmoneyalpha보다 작은 차이를 가지는 행들을 새로운 데이터프레임에 저장
        new_df = market.iloc[valid_indices]


        ask_df = new_df[new_df['ask_bid'] == 'ASK']
        bid_df = new_df[new_df['ask_bid'] == 'BID']

        # 조건에 맞는 ask와 bid의 개수 파악
        ask_count = ask_df.shape[0]
        bid_count = bid_df.shape[0]

        # 결과 출력
        print("첫번째 조건 충족 여부:", first_condition_met)
        print("Ask의 개수:", ask_count ," -- ",ask_df['total'])
        print("Bid의 개수:", bid_count ," -- ",bid_df['total'])
        print(f"봇(추정)의 개수는 : {min(ask_count, bid_count)}")

    else:
        print("첫번째 조건 충족되지 않음")


lists=get_url("https://api.upbit.com/v1/trades/ticks?market=KRW-MVL&count=100")

#abc=botcs(lists)
new_botcheck3(lists)




end = time.time()
print(f"---- 프로그램 실행 시간은 {round(end-start, 1)}초")

