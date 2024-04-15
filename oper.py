from threading import Thread
from upbitwebsocket import Upbitwebsocket
from data_process import DataProcess
from market.upbitmarket import UpbitMarket
from strategy.strategy_canlong import StrategyCL
from trader.upbittrader import UpbitTrader

class Operator:
    def __init__(self, budget=10000, strategy=StrategyCL):
        self.budget = budget

        self.websocket = Upbitwebsocket()
        self.dataprocessor = DataProcess()
        self.upbitmarket=UpbitMarket()
        self.strategy = strategy
        self.trader=UpbitTrader()


    def initialize(self, info=None, budget=100000, min_price=5000):
        self.budget = budget
        self.min_price = min_price

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

        try:
            if data.get('type') == 'trade':
                pdata=self.dataprocessor.socketdataprocess(data)
                self.strategys(pdata)
            elif data.get('type') == 'myTrade':
                pass
                #self.update_order(data)

        except Exception as e:
            print(f"에러 발생: {e}")


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
        self.strategy.checkdata(data)
        fianllist=self.strategy.updateprocess()

        if fianllist:
            self.trader.send_request(request_list=fianllist, callback=self.strategy.update_result)

            #trader로 전송해서 성공시 self.strategy.finallist[market][progress]=1 로 바꿔줘서 진행되게


    def getaccounts(self):
        info=self.trader.get_account_info()
        return info