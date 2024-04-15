from datetime import datetime, timedelta

class DataProcess:
    
    def __init__(self):
        pass

    def socketdataprocess(self, data):
        total =data.get('trade_volume') * data.get('trade_price')
        pdata={
            "market" : data.get('code'),
            "trade_volume" : data.get('trade_volume', 0),
            "trade_price" :data.get('trade_price', 0),
            "ask_bid" : data.get('ask_bid'),
            "time" : self.utctotime(data.get('trade_time')),
            "total" :  total
        }

        return pdata
    

    def utctotime(self, utctime):
        # 시간값을 ':'를 기준으로 분해하여 시, 분, 초로 나누기
        hour, minute, second = map(int, utctime.split(':'))

        # 9시간을 더하여 24시간 형식으로 변환하기
        result_hour = (hour + 9) % 24

        # 결과를 문자열 형태로 반환
        result_time = f"{result_hour:02d}:{minute:02d}:{second:02d}"

        return result_time
    

    def getnow(self):
        # 현재 시간 구하기
        current_time = datetime.now()

        # 원하는 형식의 문자열로 변환
        formatted_time = current_time.strftime("%H:%M:%S")

        return formatted_time  # 예시 출력: 04:16:36