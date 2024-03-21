"""각 모듈을 컨트롤하여 전체 시스템의 운영을 담당하는 Operator 클래스"""

import time
import threading
from datetime import datetime
from work import Worker
from upbittickdataprovider import UpbitTickProvider
from upbittickdataprovider2 import PyTicks
from upbitmarket import UpbitMarket
from concurrent.futures import ThreadPoolExecutor
from killbotstrategy import KILLBOT
import pandas as pd
import inspect


class Operator:
    def __init__(self, on_exception=None):
        self.data_provider = None
        self.strategy = None
        self.trader = None
        self.interval=0
        self.timer_expired_time=None
        self.is_timer_running = False
        self.timer = None
        self.worker = Worker("Operator-Worker")
        self.pyticks=PyTicks()
        self.umakret=UpbitMarket()
        self.strategy=KILLBOT()
        self.state = None
        self.marketlist=[]



    def initialize(self, data_provider, budget=500):
        if self.state is not None:
            print(self.state)
            return  
        self.data_provider = data_provider
        self.state="ready"
    
    def start(self):
        """자동 거래를 시작한다
        자동 거래는 설정된 시간 간격에 맞춰서 Worker를 사용해서 별도의 스레드에서 처리된다.
        """

        if self.state != "ready":
            return False
        
        if self.is_timer_running:
            return False

        self.state="running"

        self.worker.start()
        self.worker.post_task({"runnable": self._execute_trading})

        return True
    
    def _execute_trading(self, task):
        """자동 거래를 실행하고 타이머를 다시 시작한다."""
        del task  # 사용하지 않는 매개변수 삭제
        self.is_timer_running = False
        try:
            # 거래 정보 가져오기
            #self.pyticks.initailize(self.marketlist)

            #새롭게 내가 만드는 거임.
            start = time.time()
            # response_list 초기화
            response_list=[]

            #url 만 만들고
            urls=self.pyticks.makeurls(self.marketlist, count=400)
            #그 만든걸 url 화 시키고
            urldiv=self.pyticks.divideurl(urls)

            # 나뉜 URL 리스트에 대해 반복하여 작업 수행
            for chunk in urldiv:
                #비동기 10개
                
                with ThreadPoolExecutor(max_workers=10) as pool:
                    
                    #response_list.extend(list(pool.map(self.pyticks.get_url,chunk)))
                                        # 각 결과를 DataFrame으로 변환
                    dfs = [pd.DataFrame(result) for result in pool.map(self.pyticks.get_url, chunk)]

                    # DataFrame 결합
                    df_concatenated = pd.concat(dfs, ignore_index=True)
                    new_df=self.pyticks.betterlook(df_concatenated)

                    #self.strategy.manydata(new_df)
                    # for data in datas:
                    #     new_df=self.pyticks.betterlook(data)
                    gostrategy=self.strategy.killbotstrategy2(new_df)
            print(f"한 사이클 돌았음")
            end = time.time()
            print(f"---- 프로그램 실행 시간은 {round(end-start, 1)}초")

                #쉬는시간 좀 주고
                #time.sleep(0.7)


            #이제 데이터를 가공하고 조건문을 붙여야 한다.



        except (AttributeError, TypeError) as msg:
            print(f"실행 실패: {msg}")
        # 타이머 다시 시작
        self._start_timer()
        return True
    
    def _start_timer(self):
        """설정된 간격의 시간이 지난 후 Worker가 자동 거래를 수행하도록 타이머 설정"""

        if self.is_timer_running or self.state != "running":
            return

        # 타이머 만료 시 호출될 함수 정의
        def on_timer_expired():
            self.timer_expired_time = datetime.now()
            self.worker.post_task({"runnable": self._execute_trading})

        # 설정된 간격이 1보다 작을 경우 직접 호출하고 타이머를 종료
        if self.interval < 1:
            self.is_timer_running = True
            on_timer_expired()
            return

        # 타이머 간격 조정
        adjusted_interval = self.interval
        if self.interval > 1 and self.timer_expired_time is not None:
            time_delta = datetime.now() - self.timer_expired_time
            adjusted_interval = self.interval - round(time_delta.total_seconds(), 1)

        # 조정된 간격에 따라 새로운 타이머 생성 및 시작
        self.timer = threading.Timer(adjusted_interval, on_timer_expired)
        self.timer.start()

        # 타이머 실행 상태 플래그 업데이트
        self.is_timer_running = True
        return

    def stop(self):
        """거래를 중단한다"""
        if self.state != "running":
            return
        
        try:
            self.timer.cancel()
        except AttributeError:
            print("stop operation fail")

        self.is_timer_running=False
        self.state=None

        self.worker.stop()
        print("거래중단")

    def setmessage(self):
        textlist = self.strategy.botlist
        if textlist:
            botlistn= '\n'.join(textlist)
            return botlistn

    def setmarket(self):


        #마켓 이름을 싹 다 가져와요,.
        markets=self.umakret.allmarket()

        #마켓 이름을 전송해서 현재정보를 가져와요
        markets=self.umakret.get_changerate(markets)

        #마켓 들을 모두 보기좋게 가공해요
        ret=self.umakret.betterlook(markets)

        #플러스된 마켓들만 가져와요
        gmarkets=self.umakret.plusmarket(ret)
                
        self.marketlist=gmarkets
        
        return gmarkets
    

