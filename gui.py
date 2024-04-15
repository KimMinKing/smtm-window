import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from threading import Thread
import winsound as sd
import os
import pprint
from oper import Operator
from strategy.strategy_canlong import StrategyCL

form_class = uic.loadUiType("main.ui")[0]

class MyWindow(QMainWindow, form_class):


    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.strategy= StrategyCL()
        self.operator= Operator(strategy=self.strategy)
        

        #widget event
        self.telegrambtn.clicked.connect(self.telegramtest)
        self.testbtn.clicked.connect(self.testdef)
        self.getfinalbtn.clicked.connect(self.getfinal)
        self.getaccountbtn.clicked.connect(self.getaccount)

        # 버튼 클릭 이벤트 핸들러 연결
        self.onlyinradio.clicked.connect(self.on_radio_clicked)
        self.allradio.clicked.connect(self.on_radio_clicked)
        self.onlyalarmradio.clicked.connect(self.on_radio_clicked)


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
            self.operator.entry="onlyin"
            print("operator의 entry를 only in 으로 변경했습니다.")
        elif self.allradio.isChecked():
            self.operator.entry="allin"
            print("operator의 entry를 all in 으로 변경했습니다.")
        elif self.onlyalarmradio.isChecked():
            self.operator.entry="onlyalarm"
            print("operator의 entry를 only alarm 으로 변경했습니다.")

        self.perfect()

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
