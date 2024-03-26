import copy
import os
import datetime

class Analyzer:
    """
    거래 요청, 결과 정보를 저장하고 투자 결과를 분석하는 클래스

    Attributes:
        request_list : 거래 요청 데이터 목록
        result_list : 거래 결과 데이터 목록
        info_list : 거래 데이터 목록
        asset_info_list : 특정 시점에 기록된 자산 데이터 목록
        score_ list : 특ㄹ정 시점에 기록된 수익률 데이터 목록
        get_asset_info_func : 자산 정보 업데이트를 요청하기 위한 콜백 함수


    """

    ISO_DATEFORMAT = "%Y-%m-%dT%H:%N:%S"
    OUTPUT_FOLDER ="output/"
    RECORD_INTERVAL=60      #자산 정보를 주기적으로 업데이트하는 최소 시간
    
    def __init__(self):
        self.request_list=[]
        self.result_list=[]
        self.info_list=[]
        self.asset_info_list=[]
        self.score_list=[]
        self.is_simulation = False

        if os.path.isdir("output") is False:
            print("Create output directory")
            os.mkdir("output")

    def initialize(self, get_asset_info_func):
        """
        콜백 함수를 입력 받아 초기화 한다
        
        Args:
            get_asset_info_func: 거래 데이터를 요청하는 함수로 func(arg1)arg1은 정보타임
        """

        self.get_asset_info_func = get_asset_info_func

    def put_trading_info(self, info):
        """
        거래 정보를 저장한다.
        
        kind : 보고서를 위한 데이터 종류
            0: 거래데이터
            1: 매매 요청
            2: 매매 결과
            3: 수익률 정보
        """

        new = copy.deepcopy(info)       #거래 정보를 입력 받으면 복사하고
        new["kind"]=0                   #종류
        self.info_list.append(new)      #종류정보를 추가해서 리스트에 추가
        self.maket_periodic_record()    #주기적인 수익률 생성


    def put_request(self, requests):
        """거래 요청 정보를 저장한다.(strategy 에서 요청할껄?)

        request:
        {
            "id":요청정보 id
            "type": 거래유형 sell, buy, cancel
            "price": 거래 가격
            "amount": 거래 수량
            "date_time":요청 데이터 생성 시간, 시뮬레이션 모드에서는 데이터 시간

        }

        kind : 보고서를 위한 데이터 종류
            0: 거래데이터
            1: 매매 요청
            2: 매매 결과
            3: 수익률 정보
        """

        for request in requests:
            new = copy.deepcopy(request)
            if request["type"]=="cancel":
                new["price"]=0
                new["amount"]=0
            else:
                if float(request["price"]) <= 0 or float(request["amount"]) <= 0:       #가격이나 수량이 0인 경우는 저장하지 않는다.
                    continue
                new["price"]=float(new["price"])
                new["amount"]=float(new["amount"])

            new["kind"]=1
            self.request_list.append(new)






    def putresult(self, result):
        """거래 결과 정보를 저장한다.

        request: 거래 요청 정보
                request : 거래 요청 정보
        result :
        {
            "request": 요청정보
            "type" : 유형
            "price" 거래 가격
            "amount" : 거래 수량
            "msg" : 거래 결과 메세지
            "state" : 거래 상태 requested, done
            "date_time" : 시간
        }
        

        kind : 보고서를 위한 데이터 종류
            0: 거래데이터
            1: 매매 요청
            2: 매매 결과
            3: 수익률 정보

        """
        
        try:        #똑같이 거래 수량이 0인 경우 저장하지 않고
            if float(result["price"]) <= 0 or float(result["amount"]) <= 0:
                return
        except KeyError:
            self.logger.warning("Invalid result")
            return
        
        new = copy.deepcopy(result)     #float 형식으로 데이터 저장하고
        new["price"] = float(new["price"])
        new["amount"] = float(new["amount"])
        new["kind"] = 2
        self.result_list.append(new)
        self.update_asset_info()        #수익률이 업데이트 되게 함.

        
    #수익률 기록하기
    def update_asset_info(self):
        """ 자산 정보를 저장한다.
        
        returns:
        {
            balance : 계좌 현금 잔고
            asset : 자산 목록, 마켓 이름을 키 값으로 갖고 
            quote : 종목별 현재 가격 딕셔너리
        }
        """

        if self.get_asset_info_func is None:
            self.logger.warning("Analyzer   get_asset_info_func is Not set")
            return
        
        asset_info = self.get_asset_info()      #초기화때 전달받은 걸 호출해서 자산 정보를 가져와
        new = copy.deepcopy(asset_info)         #저장하고

        new["balance"] = float(new["balance"])
        if self.is_simulation is True and len(self.info_list) > 0:
            new["date_time"] = self.info_list[-1]["date_time"]
        
        self.asset_info_list.append(new)        #저장
        self.make_score_record(new)             #수익률 기록


    def make_score_record(self, new_info):
        """
        수익률 기록을 생성
        
        new_info
        {
            balance: 계좌 현금 잔고
            asset: 자산 목록 딕셔너리
            quote : 종목별 현재 가격 딕셔너리
        }

        score_record:
            balance: 계좌현금잔고
            cumulative_retun: 기준 시점부터 누적 수익률
            price_change_ratio : 기준 시점부터 보유 종목별 가격 변동 딕셔너리
            asset : 자산 정보 튜플 리스트(종목, 평균가격,현재가격,수량,수익률(소수세자리))
            date_time: 데이터 생성 시간,
            kind:3, 보고서를 위한 데이터 종류
        """

        try:
            start_total =  self.__get_start_property_value()    #시작 시점의 자산 총액과
            start_quote = self.asset_info_list[0]["quote"]      #시작 시점의 시세 정보와
            current_total = float(new_info["balance"])          #현재 시점 자산 총액의 값
            current_quote = new_info["quote"]                   #현재 시점의 시세 정보
            cumulative_return = 0                               #자산 총액의 변동 폭 누적 수익률
            new_asset_list = []
            price_change_ratio = {}                             #가격 변동률
            self.logger.debug(f"Analyzing   make_score_record new_info {new_info}")


            for name, item in new_info["asset"].items():        #딕셔너리 값을 동시에 조회하는 반복문
                #현재 자산 목록을 순회한다.

                item_yield = 0
                amount = float(item[1])
                buy_avg = float(item[0])
                price = float(current_quote[name])
                current_total += amount * price                 #자산의 총액을 모두 합해서
                item_price_diff = price - buy_avg

                if item_price_diff != 0 and buy_avg != 0:
                    item_yield = (price - buy_avg) / buy_avg * 100
                    item_yield = round(item_yield, 3)
                
                self.logger.debug(f"Analyzer    yield record {name}, buy_avg : {buy_avg}, {price}, {amount}, {item_yield}")
                
                new_asset_list.append((name, buy_avg, price, amount, item_yield))       #시세대비 보유한 현재 종목의 수익률을 계산해서 자산 총액을 구한다.

                start_price = start_quote[name]
                price_change_ratio[name] = 0
                price_diff = price - start_price

                if price_diff != 0:
                    price_change_ratio[name] = price_diff / start_price * 100
                    price_change_ratio[name] = round(price_change_ratio[name], 3)       #보유한 자산별 시세 변경률
                
                self.logger.debug(f"Analyzer    price change ratio: {start_price} -> {price}, {price_change_ratio[name]}")


            #누적 수익률 계산
            total_diff = current_total - start_total
            if total_diff != 0:
                cumulative_return = (current_total - start_total) / start_total * 100
                cumulative_return = round(cumulative_return, 3)
            self.logger.info(
                f"Analyzer    cumulative_return {start_total} -> {current_total}, {cumulative_return}%"
            )

            self.score_list.append(         #독스트링에 정의한 형식에 맞게 저장하는 것으로 현재 수익률 기록을 저장하는 것이 완료
                {
                    "balance": float(new_info["balance"]),
                    "cumulative_return": cumulative_return,
                    "price_change_ratio": price_change_ratio,
                    "asset": new_asset_list,
                    "date_time": new_info["date_time"],
                    "kind": 3,
                }
            )
        except (IndexError, AttributeError) as msg:
            self.logger.error(f"making score record fail {msg}")


    def make_periodic_record(self):
        """주기적으로 수익률을 기록한다."""

        now = datetime.now()
        if self.is_simulation:
            now = datetime.strptime(self.info_list[-1]["date_time"], self.ISO_DATEFORMAT)

        last = datetime.strptime(self.asset_info_list[-1]["date_time"], self.ISO_DATEFORMAT)        #마지막 자산 정보 저장 시간

        delta = now - last      #계산

        if delta.total_seconds() > self.RECORD_INTERVAL:        #마지막 자산 정보시간보다 ㅣ일정 시간이 지나야만 동작
            self.update_asset_info


    def get_return_report(self, graph_filename=None, index_info=None):
        """현시점 기준 간단한 수익률 보고서를 제공한다

        index_info: 수익률 구간 정보
            (
                interval: 구간의 길이로 turn의 갯수 예) 180: interval이 60인 경우 180분
                index: 구간의 인덱스 예) -1: 최근 180분, 0: 첫 180분
            )
        Returns:
            (
                start_budget: 시작 자산
                final_balance: 최종 자산
                cumulative_return: 시스템 시작 시점부터 누적 수익률
                price_change_ratio: 시스템 시작 시점부터 보유 종목별 가격 변동률 딕셔너리
                graph: 그래프 파일 패스
                period: 수익률 산출 구간
                return_high: 기간내 최고 수익률
                return_low: 기간내 최저 수익률
                date_info: 시스템 시작 시간, 구간 시작 시간, 구간 종료 시간
            )
        """
        self.update_asset_info()

        try:
            graph = None
            start_value = self.__get_start_property_value()
            last_value = self.__get_last_property_value()
            last_return=self.score_list[-1]["cumulative_return"]
            change_ratio = self.score_list[-1]["price_change_ratio"]

            if graph_filename is not None:
                graph = self.__draw_graph(graph_filename, is_fullpath = True)

            summary = (start_value, last_value, last_return, change_ratio, graph)
            self.logger.info("### Return Report ==========================")
            self.logger.info(f"Property         {start_value:10} -> {last_value:10}")
            self.logger.info(f"Gap         {last_value - start_value:10}")
            self.logger.info(f"Price_change_ratio {change_ratio}")
            return summary
        except (IndexError, AttributeError):
            self.logger.error("get return report FAIL")