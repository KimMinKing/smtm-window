from threading import Thread
from upbitwebsocket import Upbitwebsocket
from data_process import DataProcess
from market.upbitmarket import UpbitMarket
from strategy.strategy_canlong import StrategyCL
from strategy.strategy_canl import StrategyCanL
from trader.upbittrader import UpbitTrader

class Operator:
    def __init__(self, budget=10000, strategy=StrategyCanL):
        self.budget = budget

        self.websocket = Upbitwebsocket()
        self.dataprocessor = DataProcess()
        self.upbitmarket=UpbitMarket()
        self.strategy = strategy
        self.trader=UpbitTrader()
        self.only="allonly"


    def initialize(self, info=None, budget=100000, min_price=5000):
        if info:
            self.only=info['only']
            profit=info['profit']
            stoploss=info['stoploss']

            self.strategy.profit=profit
            self.strategy.stoploss=stoploss
        self.budget = budget
        self.min_price = min_price
        print("적용")

        ##info 정리
        # self.entry = info["entry"]



    def get_data(self):

        print("Starting Qt")
        markets=self.upbitmarket.getmarketname()
        request = '[{"ticket":"test"},{"type":"trade","codes":' + markets + '},{"type":"myTrade"}]'    #웹소켓 리퀘스트 체결거래 가져오는거임
        self.websocket.initalize(request, callback=self.get_data_callback)
        self.run_thread = Thread(target=self.websocket.start)
        self.run_thread.daemon = True

        self.run_thread.start()
        self.strategy.initialize(budget=10000)


    def get_data_callback(self, data):


        if data.get('type') == 'trade':
            pdata=self.dataprocessor.socketdataprocess(data)
            self.strategys(pdata)
        elif data.get('type') == 'myTrade':
            self.strategy.update_result(data)



    # def update_order(self, data):
    #     result={
    #         "market":data.get('market'),
    #         "ask_bid":data.get('ask_bid'),
    #         "price":data.get('price'),
    #         "volume":data.get('volume'),
    #         "order_type":data.get('order_type')
    #     }
    #     print(f"result: {result}")
    #     self.strategy.update_result(result)



    def strategys(self, data):
        fianllist=None

        try:
            self.strategy.checkdata2(data)

            if self.only=="onlyall" or self.only=="onlyin":
                fianllist=self.strategy.updateprocess(data)
    
        except IndexError as e:
            print(f"에러 발생id: {e}")
        except IndentationError as e:
            print(f"에러 발생it: {e}")
        except ZeroDivisionError as e:
            print(f"에러 발생zd: {e}")
        except ValueError as e:
            print(f"에러 발생ve: {e}")

        if fianllist:
            self.trader.send_request(request_list=fianllist, callback=self.strategy.update_result)

            #trader로 전송해서 성공시 self.strategy.finallist[market][progress]=1 로 바꿔줘서 진행되게


    def getaccounts(self):
        info=self.trader.get_account_info()
        return info