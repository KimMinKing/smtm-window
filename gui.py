import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from threading import Thread
import winsound as sd
import os
import pprint
from oper import Operator
from strategy.strategy_canlong import StrategyCL
from strategy.strategy_canl import StrategyCanL

form_class = uic.loadUiType("main.ui")[0]

class MyWindow(QMainWindow, form_class):


    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #self.strategy= StrategyCL()
        self.strategy= StrategyCanL()
        self.operator= Operator(strategy=self.strategy)
        

        #widget event
        self.telegrambtn.clicked.connect(self.telegramtest)
        self.testbtn.clicked.connect(self.testdef)
        self.getfinalbtn.clicked.connect(self.getfinal)
        self.getaccountbtn.clicked.connect(self.getaccount)
        self.applybtn.clicked.connect(self.applywidget)
        self.consoleclearbtn.clicked.connect(self.consoleclear)


        self.showradio.clicked.connect(self.on_showradio)
        # 버튼 클릭 이벤트 핸들러 연결
        self.onlyinradio.clicked.connect(self.on_radio_clicked)
        self.onlyallradio.clicked.connect(self.on_radio_clicked)
        self.onlyalarmradio.clicked.connect(self.on_radio_clicked)


    def on_showradio(self):
        sender = self.sender()  # 이벤트를 발생시킨 위젯 객체 가져오기
        if sender.isChecked():
            self.strategy.showprocess=True
            print("change")
        else:
            self.strategy.showprocess=False

    def consoleclear(self):
        os.system('cls')


    def applywidget(self):
        widget={
            "strategy":self.getstrategys(),
            "only": self.on_radio_clicked(),
            "profit": self.profitperspin.value(),
            "stoploss": self.stoplossperspin.value(),
        }
        self.operator.initialize(widget)
    
    def getstrategys(self):
        lists=[]
        return lists

    def getaccount(self):
        info=self.operator.getaccounts()
        print(f"balance:{info['balance']}")
        print(f"asset:{info['asset']}")
        print(f"date_time:{info['date_time']}")


    def getfinal(self):
        print(self.strategy.finallist)

    def testdef(self):
        self.strategy.testbuy()



    # 라디오 버튼 클릭 이벤트 핸들러
    def on_radio_clicked(self):
        if self.onlyinradio.isChecked():
            only="onlyin"
            print("operator의 entry를 only in 으로 변경했습니다.")
        elif self.onlyallradio.isChecked():
            only="onlyall"
            print("operator의 entry를 all in 으로 변경했습니다.")
        elif self.onlyalarmradio.isChecked():
            only="onlyalarm"
            print("operator의 entry를 only alarm 으로 변경했습니다.")

        self.perfect()
        return only

    def perfect(self):
        if self.telegrambtn.isEnabled():  # 버튼이 활성화되어 있는지 확인
            pass
        else:
            self.telegrambtn.setEnabled(True)  # 버튼을 활성화 상태로 설정
            




    def telegramtest(self):
        self.operator.initialize()
        self.operator.get_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
