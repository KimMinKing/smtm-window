import sys
from PyQt5 import uic, QtWidgets, QtCore
import winsound as sd
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import pprint
from upsocket import Upbitwebsocket
from market import UpbitMarket
from cbstrategy import CBstrategy
from uptrader import uptradertest

form_class = uic.loadUiType("untitled.ui")[0]

class MyWindow(QMainWindow, form_class):


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.upmarket = UpbitMarket()
        self.websocket = Upbitwebsocket()
        self.strategy = CBstrategy()
        self.trader=uptradertest()

        #####  Class 설정  #######

        

        #####  Qt events  ######
        self.startbtn.clicked.connect(self.start)
        
        self.stopbtn.clicked.connect(self.stop)
        self.stopbtn.setEnabled(False)
        self.conclear.clicked.connect(self.consoleclear)
        self.addblackbtn.clicked.connect(self.addblacklistmarket)

        self.testbtn.clicked.connect(self.test)
        self.showradiobtn.toggled.connect(self.on_showradio)
        self.getaccountbtn.clicked.connect(self.getaccount)
        self.bot15btn.clicked.connect(self.bot15test)
        self.bot15endbtn.clicked.connect(self.bot15endtest)
        self.bot20btn.clicked.connect(self.bot20test)



    def start(self):
        print("Starting Qt")
        markets=self.upmarket.getmarketname()   #마켓 이름들 모두 가져오기 문자열임
        request = '[{"ticket":"test"},{"type":"trade","codes":' + markets + '},{"type":"myTrade"}]'    #웹소켓 리퀘스트 체결거래 가져오는거임
        self.websocket.initalize(request, callback=self.socketmsg, strategy=self.strategy)
        self.run_thread = Thread(target=self.websocket.start)
        self.run_thread.daemon = True

        self.run_thread.start()


        #버튼의 활성화 비활성화를 설정
        self.startbtn.setEnabled(False)
        self.stopbtn.setEnabled(True)




    def bot15test(self):
        # self.websocket.on_message(ws=None,)
        params =[{
            "market":'KRW-MTL',
            "id": self.strategy.timestamp_id(),     #진입 id
            "type": "sell",                          #진입 buy
            "price": 2961,
            "amount":9                #총액
            
            }]
        self.websocket.on_message2(params)

    def bot15endtest(self):
        pass
    

    def bot20test(self):
        pass


    def getaccount(self):
        account = self.trader.get_account_info()
        

    def test(self):
        targetreqeust=[{
                "market":'KRW-BTC',
                "id": self.strategy.timestamp_id(),     #진입 id
                "type": "buy",                          #진입 buy
                "price": str(10000),
                "amount":0                #총액
                
            }]

        self.trader.send_request(targetreqeust, self.websocket.send_request_callback)

    def addblacklistmarket(self):
        blackmarket=self.blacklistadd.toPlainText()
        if len(blackmarket) <6:
            blackmarket="KRW-"+blackmarket
        
        print(f"{blackmarket} 블랙리스트 추가")

        self.strategy.blacklist.append(blackmarket)

    def consoleclear(self):
        os.system('cls')


    def on_showradio(self):
        sender = self.sender()  # 이벤트를 발생시킨 위젯 객체 가져오기
        if sender.isChecked():
            self.strategy.showprocess=True
            print("change")
        else:
            self.strategy.showprocess=False



    def socketmsg(self, msg):
        print(msg)


    def stop(self):

        #버튼의 활성화 비활성화를 설정
        self.startbtn.setEnabled(True)
        self.stopbtn.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
