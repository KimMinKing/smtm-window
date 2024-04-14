from threading import Thread
from upbitwebsocket import Upbitwebsocket
from data_process import DataProcess

from strategy.strategy_canlong import StrategyCL

class Operator:
    def __init__(self, budget=10000, strategy=StrategyCL):
        self.budget = budget

        self.websocket = Upbitwebsocket()
        self.dataprocessor = DataProcess()
        self.strategy = strategy

    def get_data(self):

        print("Starting Qt")
        markets='[KRW-BTC]'
        request = '[{"ticket":"test"},{"type":"trade","codes":' + markets + '},{"type":"myTrade"}]'    #웹소켓 리퀘스트 체결거래 가져오는거임
        self.websocket.initalize(request, callback=self.get_data_callback)
        self.run_thread = Thread(target=self.websocket.start)
        self.run_thread.daemon = True

        self.run_thread.start()


    def get_data_callback(self, data):

        try:
                
            pdata=self.dataprocessor.socketdataprocess(data)
            self.strategys(pdata)
            

        except Exception as e:
            print(f"에러 발생: {e}")



    def strategys(self, data):
        self.strategy.checkdata(data)
        self.strategy.updateprocess()