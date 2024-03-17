"""각 모듈을 컨트롤하여 전체 시스템의 운영을 담당하는 Operator 클래스"""

import time
import threading
from datetime import datetime
from work import Worker
from upbittickdataprovider import UpbitTickProvider
from upbittickdataprovider2 import PyTicks
from upbitmarket import UpbitMarket


class Operator:
    def __init__(self, on_exception=None):
        self.data_provider = None
        self.strategy = None
        self.trader = None
        self.interval=2
        self.timer_expired_time=None
        self.is_timer_running = False
        self.timer = None
        self.worker = Worker("Operator-Worker")
        self.pyticks=PyTicks()
        self.state = None
        self.marketlist=[]

        
        print("Operator 입장")

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
        print("거래시작")

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
        print("거래가 시작되었습니다. #####################")
        self.is_timer_running = False
        try:
            # 거래 정보 가져오기
            self.pyticks.initailize(self.marketlist)
        except (AttributeError, TypeError) as msg:
            print(f"실행 실패: {msg}")
        print("거래가 완료되었습니다. #####################")
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
            print("타이머 만료")
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



    def setmarket(self):
        umakret=UpbitMarket()

        #마켓 이름을 싹 다 가져와요,.
        markets=umakret.allmarket()

        #마켓 이름을 전송해서 현재정보를 가져와요
        markets=umakret.get_changerate(markets)

        #마켓 들을 모두 보기좋게 가공해요
        ret=umakret.betterlook(markets)

        #플러스된 마켓들만 가져와요
        plusmarket=umakret.plusmarket(ret)

        #마켓리스트에 저장~
        self.marketlist=plusmarket

        return plusmarket
    

