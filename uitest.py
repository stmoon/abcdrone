# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'proto.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from tokenize import String
from xmlrpc.client import boolean
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import pickle
import zmq
import socket

class cap_thread(QtCore.QThread):
    change_pixmap = QtCore.pyqtSignal(QtGui.QImage)

    def run(self):
        frame_context = zmq.Context()
        frame_socket = frame_context.socket(zmq.PUB) 
        frame_socket.bind("ipc:///home/chiz/shareF/ipc1")
        capture = cv2.VideoCapture('udp://0.0.0.0:11111',cv2.CAP_FFMPEG)
        cnt = 0
        if not not capture.isOpened():
            capture.open('udp://0.0.0.0:11111')
        while True:
            ret, frame =capture.read()
            # 제대로 받으면 ret값은 1임, 받았을 때 진행하는 것
            if(ret):
                #opencv를 이용한 화면출력
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                cvt_to_qtformat = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                self.change_pixmap.emit(cvt_to_qtformat)
                if cnt > 4:
                    # 이미지 흑백 변환
                    grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # 이미지 리사이징 640x480
                    resize_frame = cv2.resize(grayframe, dsize=(640, 480), interpolation=cv2.INTER_AREA) 
                    
                    # 이미지 인코딩
                    #encode_result, encode_frame = cv2.imencode('.png', resize_frame)
                    
                    # 객체 직렬화
                    img_pik = pickle.dumps(resize_frame)
                    #발신
                    frame_socket.send(img_pik)
                    cnt = 0
                else:
                    cnt = cnt + 1
            if cv2.waitKey (1)&0xFF == ord ('q'):
                break
        capture.release()

class rcv_thread(QtCore.QThread):
    """
    드론 상태에서 빼와서 배터리만 써먹는 쓰레드
    split으로 드론에서 받은 데이터를 분할하고
    bat부분의 숫자부분만 사용하는 코드.
    """
    bat_val = QtCore.pyqtSignal(int)

    def run(self):
        mypc_address = ("0.0.0.0", 8890)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(mypc_address)
        while True: 
            try:
                data, server = sock.recvfrom(1518)
                recv_data = data.decode(encoding="utf-8")
                split_data = recv_data.split(';')
                value = int(split_data[10][4:])
                self.bat_val.emit(value)
            except Exception:
                print ('\nExit . . .\n')
                break
        

class list_thread(QtCore.QThread):
    list_val = QtCore.pyqtSignal(str)
    list_context = zmq.Context()
    list_socket = list_context.socket(zmq.SUB) 
    list_socket.connect("ipc:///home/chiz/shareF/ipc4")
    list_socket.setsockopt_string(zmq.SUBSCRIBE, '')
    def run(self):
        value = 0
        while True:
            list_pik = self.list_socket.recv()
            list_val = pickle.loads(list_pik, encoding='bytes')
            if len(list_val) > 4:
                list_str = '(' + str(list_val[0]) + ',' + str(list_val[1]) + ',' + \
                    str(list_val[2]) + ',' + str(list_val[3]) + ',' + \
                        str(list_val[4]) + ')'
                self.list_val.emit(list_str)

class state_thread(QtCore.QThread):
    state_val = QtCore.pyqtSignal(int)
    state_context = zmq.Context()
    state_socket = state_context.socket(zmq.SUB) 
    state_socket.connect("ipc:///home/chiz/shareF/ipc3")
    state_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    def run(self):
        #드론에서 상태를 전송 받아서 이를 emit 하는 방식
        #해야할 일
        #- 드론에 상태 보내는 zmq 만들기 
        while True:
            state_pik = self.state_socket.recv()
            state = pickle.loads(state_pik, encoding='bytes')
            state_value = 0
            if len(state) != 0:
                statestring = str(state[0],'utf-8')
                if statestring in "Stop":
                    state_value = 0
                elif statestring in "Forward":
                    state_value = 1
                elif statestring in "Back":
                    state_value = 2
                elif statestring in "Up":
                    state_value = 3
                elif statestring in "Down":
                    state_value = 4
                elif statestring in "Left":
                    state_value = 5
                elif statestring in "Right":
                    state_value = 6
                elif statestring in "Takeoff":
                    state_value = 7
                elif statestring in "Land":
                    state_value = 8
                elif statestring in "Clockwise":
                    state_value = 9
                elif statestring in "Counterclockwise":
                    state_value = 10
                self.state_val.emit(state_value)
            
        

class detection_thread(QtCore.QThread):
    detection_val = QtCore.pyqtSignal(bool)
    detection_context = zmq.Context()
    detection_socket = detection_context.socket(zmq.SUB) 
    detection_socket.connect("ipc:///home/chiz/shareF/ipc2")
    detection_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    def run(self):
        
        #드론에서 처리 결과를 받고 이를 emit 하는 방식
        #해야할 일
        #- 드론에 처리결과 보내는 zmq 만들기
        while True:
            detection_pik = self.detection_socket.recv()
            detection = pickle.loads(detection_pik, encoding='bytes')
            self.detection_val.emit(detection)




class Ui_Dialog(QtWidgets.QWidget):
    check = None

    """
    사용할 QPixmap 미리 선언해두기.
    아마 thread받아서 나온 값에 따라 바꾸도록 하면 댈거같음
    """
    
    def set_frame_image(self,img):
        self.frame_label.setPixmap(QtGui.QPixmap.fromImage(img))

    def set_state_image(self,state):
        if state == 0:
            self.state_label.setPixmap(self.stopsign)
        elif state == 1:
            self.state_label.setPixmap(self.forward)
        elif state == 2:
            self.state_label.setPixmap(self.back)
        elif state == 3:
            self.state_label.setPixmap(self.up)
        elif state == 4:
            self.state_label.setPixmap(self.down)
        elif state == 5:
            self.state_label.setPixmap(self.left)
        elif state == 6:
            self.state_label.setPixmap(self.right)
        elif state == 7:
            self.state_label.setPixmap(self.takeoff)
        elif state == 8:
            self.state_label.setPixmap(self.land)
        elif state == 9:
            self.state_label.setPixmap(self.cw)
        elif state == 10:
            self.state_label.setPixmap(self.ccw)
            

    def set_detection_image(self,detection):
        if detection == True:
            self.detection_label.setPixmap(self.check)
        elif detection == False:
            self.detection_label.setPixmap(self.notcheck)
    
    def set_data_list(self, data):
        self.value_list_view.addItem(data)
        self.value_list_view.scrollToBottom()

    #처음에 실행되는거
    def setupUi(self, Dialog):
        # 위젯 겉에 두르는거
        mystyle = "border-style: solid; border-width: 4px; border-color: #000000; border-radius: 10px;"
        
        #배경 크기 / 스타일 설정
        Dialog.setObjectName("Dialog")
        Dialog.resize(982, 890)
        Dialog.setMinimumSize(QtCore.QSize(982, 890))
        Dialog.setMaximumSize(QtCore.QSize(982, 890))
        Dialog.setStyleSheet("border-style: solid; border-width: 4px; border-color: #000000; border-radius: 10px; background-color:rgb(255, 255, 255);")
        
        # vbox 하나
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # 배터리 위젯, value property이거 실시간으로 고칠 예정
        self.batterybar = QtWidgets.QProgressBar(Dialog)
        self.batterybar.setStyleSheet("")
        self.batterybar.setProperty("value", 50)
        self.batterybar.setTextVisible(False)
        self.batterybar.setObjectName("batterybar")
        
        #battery thread test
        bty = rcv_thread(self)
        bty.start()
        bty.bat_val.connect(self.batterybar.setValue)
        
        self.verticalLayout.addWidget(self.batterybar)
        
        # 프레임 위젯, 영상 실시간으로 받을 예정
        self.frame_label = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_label.sizePolicy().hasHeightForWidth())
        self.frame_label.setSizePolicy(sizePolicy)
        self.frame_label.setMinimumSize(QtCore.QSize(960, 540))
        self.frame_label.setMaximumSize(QtCore.QSize(960, 540))
        self.frame_label.setStyleSheet(mystyle)
        self.frame_label.setObjectName("frame_label")
        self.frame_label.setPixmap(QtGui.QPixmap("wait.png"))
        self.frame_label.setScaledContents(True)
        self.frame_label.setAlignment(QtCore.Qt.AlignCenter)

        self.verticalLayout.addWidget(self.frame_label)
        

        #capture thread test
        
        cpt = cap_thread(self)
        cpt.change_pixmap.connect(self.set_frame_image)
        cpt.start()
        
        # 위젯 / hbox
        self.image_widget = QtWidgets.QWidget(Dialog)
        self.image_widget.setMinimumSize(QtCore.QSize(0, 232))
        self.image_widget.setMaximumSize(QtCore.QSize(960, 232))
    
        self.image_widget.setObjectName("image_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.image_widget)
        self.horizontalLayout.setContentsMargins(0, -1, 0, 0)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")

        #state 값 나오는 리스트 위젯
        self.value_list_view = QtWidgets.QListWidget(self.image_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.value_list_view.sizePolicy().hasHeightForWidth())
        self.value_list_view.setSizePolicy(sizePolicy)
        self.value_list_view.setMinimumSize(QtCore.QSize(0, 210))
        self.value_list_view.setMaximumSize(QtCore.QSize(210, 210))
        self.value_list_view.setStyleSheet(mystyle)
        self.value_list_view.setObjectName("value_list_view")
        self.value_list_view.setAutoScroll(True)
        self.value_list_view.setAutoScrollMargin(20)


        self.horizontalLayout.addWidget(self.value_list_view)
        
        # 드론 상태 알려줄 위젯
        self.state_label = QtWidgets.QLabel(self.image_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.state_label.sizePolicy().hasHeightForWidth())
        self.state_label.setSizePolicy(sizePolicy)
        self.state_label.setMinimumSize(QtCore.QSize(210, 210))
        self.state_label.setMaximumSize(QtCore.QSize(210, 210))
        self.state_label.setStyleSheet(mystyle)
        self.state_label.setText("")
        self.state_label.setScaledContents(True)
        self.state_label.setAlignment(QtCore.Qt.AlignCenter)
        self.state_label.setObjectName("state_label")
        
        self.horizontalLayout.addWidget(self.state_label)

        self.forward = QtGui.QPixmap("icon/forward.png")
        self.back = QtGui.QPixmap("icon/back.png")
        self.up  = QtGui.QPixmap("icon/up.png")
        self.down = QtGui.QPixmap("icon/down.png")
        self.left = QtGui.QPixmap("icon/left.png")
        self.right  = QtGui.QPixmap("icon/right.png")
        self.takeoff = QtGui.QPixmap("icon/takeoff.png")
        self.land = QtGui.QPixmap("icon/land.png")
        self.cw = QtGui.QPixmap("icon/cw.png")
        self.ccw = QtGui.QPixmap("icon/ccw.png")
        self.stopsign = QtGui.QPixmap("icon/stop.png")
        self.state_label.setPixmap(self.stopsign)
        
        #판별 위젯
        self.detection_label = QtWidgets.QLabel(self.image_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.detection_label.sizePolicy().hasHeightForWidth())
        self.detection_label.setSizePolicy(sizePolicy)
        self.detection_label.setMinimumSize(QtCore.QSize(210, 210))
        self.detection_label.setMaximumSize(QtCore.QSize(210, 210))
        self.detection_label.setStyleSheet(mystyle)
        self.detection_label.setText("")

        # 버그체크해봐야할부분
        self.check = QtGui.QPixmap("icon/check.png")
        self.notcheck = QtGui.QPixmap("icon/notcheck.png")
        self.detection_label.setPixmap(self.notcheck)

        self.detection_label.setScaledContents(True)
        self.detection_label.setAlignment(QtCore.Qt.AlignCenter)
        self.detection_label.setObjectName("detection_label")

        det_th = detection_thread(self)
        det_th.start()
        det_th.detection_val.connect(self.set_detection_image)

        self.horizontalLayout.addWidget(self.detection_label)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        
        self.verticalLayout.addWidget(self.image_widget)
        
        #밑에 글 넣을 레이아웃
        self.text_widget = QtWidgets.QWidget(Dialog)
        self.text_widget.setMinimumSize(QtCore.QSize(0, 45))
        self.text_widget.setMaximumSize(QtCore.QSize(16777215, 45))
        self.text_widget.setObjectName("text_widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.text_widget)
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")


        # ctrl text 라벨
        self.control_text_label = QtWidgets.QLabel(self.text_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.control_text_label.sizePolicy().hasHeightForWidth())
        self.control_text_label.setSizePolicy(sizePolicy)
        self.control_text_label.setMinimumSize(QtCore.QSize(0, 30))
        self.control_text_label.setMaximumSize(QtCore.QSize(210, 30))
        self.control_text_label.setSizeIncrement(QtCore.QSize(0, 30))
        self.control_text_label.setBaseSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.control_text_label.setFont(font)
        self.control_text_label.setStyleSheet(mystyle)
        self.control_text_label.setScaledContents(True)
        self.control_text_label.setAlignment(QtCore.Qt.AlignCenter)
        self.control_text_label.setObjectName("control_text_label")

        self.horizontalLayout_2.addWidget(self.control_text_label)
        
        # 상태 이름
        self.state_text_label = QtWidgets.QLabel(self.text_widget)
        self.state_text_label.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.state_text_label.sizePolicy().hasHeightForWidth())
        self.state_text_label.setSizePolicy(sizePolicy)
        self.state_text_label.setMinimumSize(QtCore.QSize(0, 30))
        self.state_text_label.setMaximumSize(QtCore.QSize(210, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.state_text_label.setFont(font)
        self.state_text_label.setStyleSheet(mystyle)
        self.state_text_label.setScaledContents(True)
        self.state_text_label.setAlignment(QtCore.Qt.AlignCenter)
        self.state_text_label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.state_text_label.setObjectName("state_text_label")
        
        self.horizontalLayout_2.addWidget(self.state_text_label)
        
        # 판별 이름
        self.detection_text_label = QtWidgets.QLabel(self.text_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.detection_text_label.sizePolicy().hasHeightForWidth())
        self.detection_text_label.setSizePolicy(sizePolicy)
        self.detection_text_label.setMinimumSize(QtCore.QSize(0, 30))
        self.detection_text_label.setMaximumSize(QtCore.QSize(210, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.detection_text_label.setFont(font)
        self.detection_text_label.setStyleSheet(mystyle)
        self.detection_text_label.setTextFormat(QtCore.Qt.RichText)
        self.detection_text_label.setScaledContents(True)
        self.detection_text_label.setAlignment(QtCore.Qt.AlignCenter)
        self.detection_text_label.setObjectName("detection_text_label")
        
        self.horizontalLayout_2.addWidget(self.detection_text_label)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 1)
        
        self.verticalLayout.addWidget(self.text_widget)

        state_th = state_thread(self)
        state_th.start()
        state_th.state_val.connect(self.set_state_image)

        list_th = list_thread(self)
        list_th.start()
        list_th.list_val.connect(self.set_data_list)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.control_text_label.setText(_translate("Dialog", "Drone Control Value"))
        self.state_text_label.setText(_translate("Dialog", "Drone State"))
        self.detection_text_label.setText(_translate("Dialog", "Human Detection"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

