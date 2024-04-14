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


    def telegramtest(self):
        self.operator.get_data()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
