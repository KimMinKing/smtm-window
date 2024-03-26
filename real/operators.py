class Operator:
    
    """전체 시스템의 운영을 담당하는 클래스
    
    Attributes:
        data_provider 
        strategy
        trader
        analyzer
        interval : 매매 프로세스가 수행되는 간격 # default 10 second

    """
    ISO_DATEFORMAT = "%Y-%m-%dT%H:%N:%S"
    OUTPUT_FOLDER ="output/"


    def __init__(self):
        self.logger = LogManager.get_logger(__class__.__name__)
        self.data_provider = None
        self.strategy = None
        self.trader = None
        self.interval = 10  # default 10 second
        self.is_timer_running = False
        self.timer = None
        self.analyzer = None
        self.worker = Worker("Operator-Worker")
        self.state = None
        self.is_trading_activated = False
        self.tag = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.timer_expired_time = None
        self.last_report = None
        self.last_periodic_time = datetime.now()
        self.on_exception = on_exception

    def initialize(self, data_provider, strategy, trader, analyzer, budget=500):
        """
        운영에 필요한 모듈과 정보를 설정 및 각 모듈 초기화 수행

        data_provider: 운영에 사용될 DataProvider 객체
        strategy: 운영에 사용될 Strategy 객체
        trader: 운영에 사용될 Trader 객체
        analyzer: 운영에 사용될 Analyzer 객체
        """
        if self.state is not None:
            return

        self.data_provider = data_provider
        self.strategy = strategy
        self.trader = trader
        self.analyzer = analyzer
        self.state = "ready"
        self.strategy.initialize(budget)
        self.analyzer.initialize(trader.get_account_info)


    
    def start(self):
        """자동 거래를 시작한다

        자동 거래는 설정된 시간 간격에 맞춰서 Worker를 사용해서 별도의 스레드에서 처리된다.
        """
        if self.state != "ready":
            return False

        if self.is_timer_running:
            return False

        self.logger.info("===== Start operating =====")
        self.state = "running"
        self.analyzer.make_start_point()
        self.worker.start()
        self.worker.post_task({"runnable": self._execute_trading})
        return True




    def _start_timer(self):
        """설정된 간격의 시간이 지난 후 Worker가 자동 거래를 수행하도록 타이머 설정"""
        self.logger.debug(
            f"start timer {self.is_timer_running} : {self.state} : {threading.get_ident()}"
        )
        if self.is_timer_running or self.state != "running":
            return

        def on_timer_expired():
            self.timer_expired_time = datetime.now()
            self.worker.post_task({"runnable": self._execute_trading})

        if self.interval < 1:
            # call the handler directly to enhance performance. Timer create new thread always.
            self.is_timer_running = True
            on_timer_expired()
            return

        adjusted_interval = self.interval
        if self.interval > 1 and self.timer_expired_time is not None:
            time_delta = datetime.now() - self.timer_expired_time
            adjusted_interval = self.interval - round(time_delta.total_seconds(), 1)

        self.timer = threading.Timer(adjusted_interval, on_timer_expired)
        self.timer.start()

        self.is_timer_running = True
        return
    


    def stop(self):
        """거래를 중단한다
        analyzer.create_report을 실행하고 반환값을 반환한다.
        """
        if self.state != "running":
            return None

        self.logger.info("cancel timer first")
        if self.timer is not None:
            self.timer.cancel()
        self.is_timer_running = False

        self.trader.cancel_all_requests()
        trading_info = self.data_provider.get_info()
        self.analyzer.put_trading_info(trading_info)
        self.last_report = self.analyzer.create_report(tag=self.tag)
        self.logger.info("===== Stop operating =====")
        self.state = "terminating"

        def on_terminated():
            self.state = "ready"

        self.worker.register_on_terminated(on_terminated)
        self.worker.stop()

        return self.last_report
    


    def _execute_trading(self, task):
        """자동 거래를 실행 후 타이머를 실행한다"""
        del task
        self.logger.debug("trading is started #####################")
        self.is_timer_running = False
        try:
            trading_info = self.data_provider.get_info()
            self.strategy.update_trading_info(trading_info)
            self.analyzer.put_trading_info(trading_info)
            self.logger.debug(f"trading_info {trading_info}")

            def send_request_callback(result):
                self.logger.debug("send_request_callback is called")
                if result == "error!":
                    self.logger.error("request fail")
                    return
                self.strategy.update_result(result)

                if "state" in result and result["state"] != "requested":
                    self.analyzer.put_result(result)

            target_request = self.strategy.get_request()
            self.logger.debug(f"target_request {target_request}")
            if target_request is not None:
                self.trader.send_request(target_request, send_request_callback)
                self.analyzer.put_requests(target_request)
        except (AttributeError, TypeError) as msg:
            self.logger.error(f"excuting fail {msg}")
        except Exception as exc:
            if self.on_exception is not None:
                self.on_exception("Something bad happened during trading")
            raise RuntimeError("Something bad happened during trading") from exc

        if self.PERIODIC_RECORD is True:
            self._periodic_internal_get_score()

        self.logger.debug("trading is completed #####################")
        self._start_timer()

