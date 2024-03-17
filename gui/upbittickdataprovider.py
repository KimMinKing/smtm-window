import requests

class UpbitTickProvider():

    URL="https://api.upbit.com/v1/trades/ticks"

    def __init__(self, currency="MASK", ticks=100, interval=10):
        self.currency=currency
        self.ticks=str(ticks)
        self.interval=interval
        print("upbit 입장")
        if self.interval==10:
            self.query_string = {"market": currency, "count": 100}


    def get_info(self):
        url=self.URL
        try:
            
            response = requests.get(url, params=self.query_string)
            return response
        except ValueError as error:
            print(f"Invalid data from server: {error}")
            raise UserWarning("Fail get data from sever") from error
        except requests.exceptions.HTTPError as error:
            print(error)
            raise UserWarning("Fail get data from sever") from error
        except requests.exceptions.RequestException as error:
            print(error)
            raise UserWarning("Fail get data from sever") from error



    def __create_candle_info(self, data):
        try:
            return {
                "type": "primary_candle",
                "market": self.market,
                "date_time": data["candle_date_time_kst"],
                "opening_price": float(data["opening_price"]),
                "high_price": float(data["high_price"]),
                "low_price": float(data["low_price"]),
                "closing_price": float(data["trade_price"]),
                "acc_price": float(data["candle_acc_trade_price"]),
                "acc_volume": float(data["candle_acc_trade_volume"]),
            }
        except KeyError as err:
            print(f"invalid data for candle info: {err}")
            return None
