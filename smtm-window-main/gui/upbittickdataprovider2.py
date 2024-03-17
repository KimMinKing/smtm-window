import requests
import pprint
import locale
import time
import pandas as pd
from upbittickdataprovider import UpbitTickProvider
from upbitmarket import UpbitMarket
from datetime import datetime, timezone, timedelta
import winsound as sd

class PyTicks:
    URL = "https://api.upbit.com/v1/trades/ticks"


    def __init__(self, market=None, count=500, backtest=None):
        self.market=market
        self.count=count
        self.truebot=[]
        self.backtest=backtest
        self.falsebotcount=0
        print("pyticks 입장")


    def initailize(self, markets):
        # start = time.time()
        for omarket in markets:
            self.market=omarket
            df=self.gettick()
            new_df = self.betterlook(df)
            botnum=self.botcheck(new_df)
            percent='%.2f%%'% (botnum/len(new_df) * 100)

            #이미 걸렸던 것 재확인
            if omarket in self.truebot and botnum <120:
                self.falsebotcount=self.falsebotcount+1     #재확인을 위한 체크

                #체크가 3번일 때
                if self.falsebotcount >2:
                    print(f"{omarket} : {percent} 봇 끝났나 확인해주세요")  #봇 종료 확인
                    self.falsebotcount=0
                    self.truebot.remove(omarket)

            #이미 걸렸던 것 재확인인데 그냥 아무 활동 안함
            elif omarket in self.truebot and botnum >120:
                pass

            #처음 걸린거
            elif botnum>120:
                #처음 걸렸다.
                
                print(f"{omarket} : {percent}")
                self.truebot.append(omarket)
                sd.Beep(2000, 1000)




                # self.main.alert(f"{omarket} : {percent}")
        # end = time.time()
        # print(f"---- 프로그램 실행 시간은 {round(end-start, 1)}초")


    def pdsetting(self):
        pd.set_option('display.float_format', lambda x: '%.3f' % x)
        # row 생략 없이 출력
        pd.set_option('display.max_rows', None)
        # col 생략 없이 출력
        pd.set_option('display.max_columns', None)
        # 로케일 설정 (한국어, 한국)
        locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')


        

    # 시간 문자열의 맨 뒤 두 자리를 추출하여 정수로 변환하는 함수
    def extract_seconds(self,time_str):
        # ":"를 기준으로 문자열을 분할하여 맨 뒤의 두 자리를 추출
        seconds_str = time_str.split(':')[-1]
        # 추출한 문자열을 정수로 변환하여 반환
        return int(seconds_str)



    def mintime(self,df):
        # trade_time_utc 열을 시간 형식으로 변환
        df['trade_time_utc'] = pd.to_datetime(df['trade_time_utc'], format='%H:%M:%S')

        # 최댓값과 최솟값 구하기
        max_time = df['trade_time_utc'].max()
        min_time = df['trade_time_utc'].min().time()
        min_time=min_time

        return min_time


    def diftime(self,df):
        # trade_time_utc 열을 시간 형식으로 변환
        df['trade_time_utc'] = pd.to_datetime(df['trade_time_utc'], format='%H:%M:%S')

        # 최댓값과 최솟값 구하기
        max_time = df['trade_time_utc'].max()
        min_time = df['trade_time_utc'].min()

        # 차이 계산
        time_difference = (max_time - min_time).seconds

        # # 결과 출력
        # print("최대 시간:", max_time)
        # print("최소 시간:", min_time)
        # print("시간 차이(초):", time_difference)

        return time_difference


    def botcheck(self, df):
        
        #봇 가격대
        botmoney = [151000, 161000, 206000, 226000, 236000]
        botmoneyalpha=8000
        rows_with_conditions = df[df['total'].isin(botmoney)]
        
        bot_df = pd.DataFrame()

        # 각 조건에 대해 범위 내에 있는 행을 선택하여 새로운 DataFrame에 추가
        for moenyone in botmoney:
            lower_bound = moenyone
            upper_bound = moenyone + botmoneyalpha
            rows_in_range = df[(df['total'] >= lower_bound) & (df['total'] <= upper_bound)]
            bot_df = pd.concat([bot_df, rows_in_range], ignore_index=True)

                # ASK와 BID를 각각 필터링하여 추출
        asks = bot_df[bot_df['ask_bid'] == 'ASK']
        bids = bot_df[bot_df['ask_bid'] == 'BID']

        nonebot=abs(len(asks)-len(bids))

        botnum=len(bot_df)-nonebot

        return botnum




    #모든 데이터를 보기좋게 가공함
    def betterlook(self, df):

        #살려둘 칼럼들
        selected_columns = ['market', 'trade_time_utc','trade_price','trade_volume','ask_bid']
        new_df = df[selected_columns].copy()

        
        #총 거래 금액 칼럼 추가하기
        new_df['total'] = new_df['trade_price'] * new_df['trade_volume']
        #총거래금액 칼럼 int형으로 만들기
        new_df['total']=new_df['total'].astype(int)

        #trade_time utc로 정렬해서 인덱스 재설정하기
        new_df=new_df.sort_values(by='trade_time_utc')
        new_df = new_df.reset_index(drop=True)

        return new_df


    def toutc(self, times):
        # 문자열 형식의 시간을 datetime 객체로 변환합니다.
        desired_time_kr = datetime.strptime(times, "%H:%M:%S")

        # UTC로 변환
        desired_time_utc = desired_time_kr - timedelta(hours=9)

        # UTC 시간을 문자열로 변환
        desired_time_utc_str = desired_time_utc.strftime("%H:%M:%S")

        return desired_time_utc_str


    """ 20240227005800
        20240227005710
        20240227005600
    """

    def getmoretick(self, df, time, aftertime,beforeday):
        #데이터의 초를 재봐 50초
        timetr=self.diftime(df)
        aftertime=timedelta(seconds=aftertime*60)   #몇분 더 원해요
        print(timedelta(seconds=timetr))

        wantsc=aftertime-timedelta(seconds=timetr) #요청한 시간- 획득한 데이터 시간
        aftertime=wantsc/60 #요청할 시간

        #시간 충족이 안됬어
        if wantsc>0:
            #시간 20240227005800 - 50 - 1
            wtime=time-timetr-1

            #지금 시간을 utc 시간으로 변경
            utctime=self.toutc(wtime)

            df = pd.concat(self.gettick(utctime,time= time ,aftertime=aftertime, beforeday=beforeday))

        return df
    
    def getmoreticks(self, df, time, aftertime, beforetime):

        timetr=self.diftime(df)    #df데이터의 시간의 기본값 데이터가 몇 초인지
        timetrdel=timedelta(seconds=timetr) #df테이터의 시간의 가공값

        mintime=self.mintime(df)   #데이터 상의 마지막 시간 )13:30:00

        aftertimedelta=timedelta(minutes=aftertime) #추가로 원하는 시간

        minus= aftertimedelta-timetrdel     #차이

        if minus>timedelta(seconds=1):
            #무한루프
            df=pd.concat()

        print(f"df의 데이터들의 시간 = {timetrdel} , 데이터의 마지막 시간 : {mintime}, 추가로 원하는 시간 = {aftertimedelta}, 차={minus}")
        #df의 데이터들의 시간 = 0:00:50 , 데이터의 마지막 시간 : 15:57:09, 추가로 원하는 시간 = 0:03:00, 차=0:02:10

        # df = pd.concat(upbittick.gettick(utctime,time= time ,aftertime=aftertime, beforeday=beforeday))

    #rest api를 실행하는 함수                       beforeday는 몇 일 전인지 1부터가 어제임
    #time은 13:30:00 형식이고, 까지임. 그러니까 13시30분00초 밑으로 나온다는거지. 
    #13시25분부터 30분까지 하고싶다면 aftertime을 5를 넣어야함.
    #           언제부터, 추가로 원하는 시간
    
    

    
    def gettick(self, df=None, time=None, aftertime=None, beforeday=0):
        
        if aftertime is not None:
            if df is None:
                print("11")
                # 초기에 데이터프레임이 없는 경우
                query_string={"market": self.market, "count": self.count, "to": time, "daysAgo":beforeday}
                response = requests.get(self.URL, params=query_string).json()
                data = response  # JSON 데이터를 딕셔너리나 리스트에 저장
                df = pd.DataFrame(data)  # 데이터프레임으로 변환

            # 재귀적으로 데이터를 가져오는 경우
            timetr=self.diftime(df)    # df데이터의 시간의 기본값 데이터가 몇 초인지
            timetrdel=timedelta(seconds=timetr) # df테이터의 시간의 가공값
            mintime=self.mintime(df)   # 데이터 상의 마지막 시간 (e.g., 13:30:00)
            aftertimedelta=timedelta(seconds=aftertime) # 추가로 원하는 시간
            minus = aftertimedelta - timetrdel  # 차이
            print(minus)
            if minus > timedelta(seconds=1):
                # 추가로 가져올 데이터가 있을 때
                query_string={"market": self.market, "count": self.count, "to": mintime, "daysAgo":beforeday}
                response = requests.get(self.URL, params=query_string).json()
                data = response  # JSON 데이터를 딕셔너리나 리스트에 저장
                new_df = pd.DataFrame(data)  # 새로운 데이터프레임 생성
                # 재귀적으로 데이터를 가져와서 이전 데이터프레임과 합침
                print("33")
                df = pd.concat([df, self.gettick(df=new_df, time=mintime, aftertime=minus.total_seconds(), beforeday=beforeday)], ignore_index=True)
        #백테스트가 아닐 때
                
        elif df is None and time is None and aftertime is None:
            query_string={"market": self.market, "count": self.count}
            response = requests.get(self.URL, params=query_string).json()
            df = pd.DataFrame(response)  # 데이터프레임으로 변환
        return df



    def test(self,ab):
        ab=ab-1
        print(f"{ab}, test1")
        if ab>1:
            ab=self.test(ab)
        return ab


# 실행 코드
if __name__ == "__main__":

    #프로그램 시간 체크
    start = time.time()

    # #생성 틱 고정
    # upbittick=PyTicks("KRW-THETA", 500)

    # #pandas 세팅
    # upbittick.pdsetting()

    # #지금 시간을 utc 시간으로 변경
    # utctime=upbittick.toutc("00:58:00")


    # #utc 시간 넣고 체결 정보 가져옴
    # #df = upbittick.gettick(time=utctime, aftertime=120, beforeday=1)

    # df = upbittick.gettick()
    # print(df)

    # #체결 정보 데이터의 처음과 끝 시간 파악하기
    # timetr=upbittick.diftime(df)

    # #체결 정보 가독성 좋게 만들기
    # new_df = upbittick.betterlook(df)

    # #체결정보 csv 파일로 저장하기
    # new_df.to_csv('betterlook.csv', encoding='utf-8-sig',index=True)

    # #봇의 갯수 파악하기
    # botnum=upbittick.botcheck(new_df)

    #마켓 생성
    upmarket=UpbitMarket()
    marketss=upmarket.allmarket()
    print(marketss)

    upticks = PyTicks("dd")
    upticks.initailize(marketss)

    # #출력
    # print(f"---- df 의 갯수는 {len(new_df)}, 봇 개수는 {botnum}")
    # percent='%.2f%%'% (botnum/len(new_df) * 100)
    # print(f"---- 봇의 퍼센트는 {percent}")
    # print(f"---- df 처음과 끝의 시간은 {timetr}초")


    # #시간체크
    end = time.time()
    print(f"---- 프로그램 실행 시간은 {round(end-start, 1)}초")




