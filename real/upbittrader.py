class UpbitTrader:

    def send_request(self, request_list, callback):
        """
        거래를 요청한다.
        
        요청 정보를 기반으로 거래를 요청하고, callback으로 체결 결과 수신

        request list:
        [{
            "id":요청정보
            "type":거래유형
            "price"
            "amount"
            "date_time

        }]

        callback(result):
        {
            "request":요청정보전체
            "type":거래유형
            "price"
            "amount"
            "msg":거래 결과 메세지 success, internnal error
            "balance":거래 후 계좌 현금 잔고
            "state":거랫 상태 requested, done
            "date_time"  거래 체결 시간
        }

        """

    def cancel_request(self, request_id):
        """#request id = 취소하고자 하는 request의 id"""

    def cancel_all_request(self):
        """모든 거래 요청을 취소"""


    def get_account_info(self):
        """계좌 정보를 요청한다.
        현금을 포함한 모든 자산 정보를 제공
        
        
        return:
        {
            balance : 계좌 잔고
            asset : 자산 목록, 마켓 이름으로 키 값으로 갖고 (평균 매입가격, 수량)을 갖는 딕셔너리
            quote : 종목별 현재 가격 딕셔너리
        }"""