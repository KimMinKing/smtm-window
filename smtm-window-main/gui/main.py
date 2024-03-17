import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from oper import Operator
from upbittickdataprovider import UpbitTickProvider
from os import environ       # environ 를 import 해야 아래 suppress_qt_warnings 가 정상 동작하니다

form_class = uic.loadUiType("mywindow.ui")[0]

class MyWindow(QMainWindow, form_class):

    def suppress_qt_warnings(self): # 해상도별 글자크기 강제 고정하는 함수
        environ["QT_DEVICE_PIXEL_RATIO"] = "0"
        environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        environ["QT_SCREEN_SCALE_FACTORS"] = "1"
        environ["QT_SCALE_FACTOR"] = "1"

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #var
        self.coinexchange=None

        self.operator=Operator()

        #timer
        self.timer= QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.cycle)        


        #Qt Widget connect event
        self.startbtn.clicked.connect(self.start)
        self.stopbtn.clicked.connect(self.stop)
        self.marketcheckbtn.clicked.connect(self.marketcheck)

    #종목이 뜨게 하는거임.
    def marketcheck(self):
        marketcount=self.operator.setmarket()
        self.marketconsole.append(f"현재 업비트에서 상승을 보이고 있는 마켓의 갯수는 {len(marketcount)} 개 입니다.")
        self.marketconsole.append(f"시작하시려면 시작 버튼을 눌러주십시오.")
        
    def alert(self, msg):
        self.marketconsole.append(f"{msg}")

    def cycle(self):
        cur_time=QTime.currentTime()
        str_time=cur_time.toString("hh:mm:ss")
        self.statusBar().showMessage(str_time)
        

    def stop(self):
        print("스탑")
        self.operator.stop()

    def start(self):
        self.currency="KRW-MASK"
        self.coinexchange=self.coinexchangecombobox.currentText()


        data_provider = UpbitTickProvider(currency=self.currency)
        
        self.operator.initialize(data_provider)
        self.operator.start()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.suppress_qt_warnings()
    myWindow.show()
    app.exec_()
