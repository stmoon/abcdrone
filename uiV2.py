# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'proto.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

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
    드론 상태를 받는 쓰레드
    """
    state_val = QtCore.pyqtSignal(list)

    def run(self):
        mypc_address = ("0.0.0.0", 8890)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(mypc_address)
        while True: 
            try:
                data, server = sock.recvfrom(1518)
                recv_data = data.decode(encoding="utf-8")
                split_data = recv_data.split(';')
                self.state_val.emit(split_data)
            except Exception:
                print ('\nExit . . .\n')
                break
        


class state_thread(QtCore.QThread):
    """
    드론의 움직임을 전송받는 쓰레드
    """
    state_val = QtCore.pyqtSignal(int)
    state_context = zmq.Context()
    state_socket = state_context.socket(zmq.SUB) 
    state_socket.connect("ipc:///home/chiz/shareF/ipc3")
    state_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    def run(self):
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
    """
    판별 결과를 받아오는 쓰레드
    """
    detection_val = QtCore.pyqtSignal(list)
    detection_context = zmq.Context()
    detection_socket = detection_context.socket(zmq.SUB) 
    detection_socket.connect("ipc:///home/chiz/shareF/ipc2")
    detection_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    def run(self):
        while True:
            detection_pik = self.detection_socket.recv()
            detection = pickle.loads(detection_pik, encoding='bytes')
            self.detection_val.emit(detection)

class frame_widget(QtWidgets.QLabel):
    def __init__(self,parent = None):
        self.frame = None
        self.state_list = None
        self.det_list = []
        self.drone_move = 0

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

        super().__init__(parent)
        self.setWidget()

    def set_drone_move(self,value):
        self.drone_move = value

    def set_frame_img(self, img):
        """
        화면 갱신 등의 이벤트가 발생해야 paintEvent를 호출하기 때문에
        setPixmap을 이용하여 화면 갱신 
        """
        self.frame = QtGui.QPixmap.fromImage(img)
        self.setPixmap(self.frame)

    def set_recv_state(self, state):
        self.state_list = state

    def set_det_list(self, det):
        self.det_list = det
    
    def setWidget(self):
        self.setMinimumSize(QtCore.QSize(960, 540))
        self.setMaximumSize(QtCore.QSize(960, 540))
        self.setObjectName("")
        self.setScaledContents(True)
        self.setAlignment(QtCore.Qt.AlignCenter)
        # 사용할 쓰레드들 선언 후 함수에 연결
        cpt = cap_thread(self)
        cpt.change_pixmap.connect(self.set_frame_img)
        cpt.start()
        recv = rcv_thread(self)
        recv.state_val.connect(self.set_recv_state)
        recv.start()
        det = detection_thread(self)
        det.detection_val.connect(self.set_det_list)
        det.start()
        drv = state_thread(self)
        drv.state_val.connect(self.set_drone_move)
        drv.start()

    def paintEvent(self, event):
        """
        통신으로 받아온 데이터는 emit/connect로 연결한 함수를 이용해서 저장을 해둠
        저장한 데이터를 기준으로 paintEvent를 굴리는 것
        저장한 데이터를 기준으로 paintEvent를 사용하는 이유는
        드론의 프레임, 객체 탐지 결과, 드론의 이동 등이 같은 타이밍에 호출되지 않기 때문임.
        """
        qpt = QtGui.QPainter()
        qpt.begin(self)
        if self.frame == None:
            qpt.drawPixmap(0,0,960,540,QtGui.QPixmap("wait.png"))
        else:
            qpt.drawPixmap(0,0,960,540,self.frame)

        
        # 사람에 체크박스 그리는 부분
        qpt.setOpacity(0.8)
        qpt.setPen(QtGui.QPen(QtCore.Qt.red,6))         
        if len(self.det_list) != 0:
            for i in range(len(self.det_list)):
                xmin,ymin = int(self.det_list[i][0] * 1.5), int(self.det_list[i][1] * 1.125)
                xmax,ymax = int(self.det_list[i][2] * 1.5), int(self.det_list[i][3] * 1.125)
                width = xmax - xmin
                height = ymax - ymin
                qpt.drawRect(xmin,ymin,width,height)

        # 드론의 row pitch yaw battery 띄우는 부분
        qpt.setOpacity(1)
        qpt.setPen(QtGui.QColor(250,250,250))
        font = QtGui.QFont('Arial', 20)
        font.setBold(True)
        qpt.setFont(font)

        if self.state_list == None:
            qpt.drawText(event.rect(), QtCore.Qt.AlignLeading|QtCore.Qt.AlignRight|QtCore.Qt.AlignTop,' roll: ?\n pitch: ?\n yaw: ?\n battery: ?')
        else:
            text = self.state_list[1] + '\n' + self.state_list[0] + '\n' + self.state_list[2] + '\n' + 'battery:' + self.state_list[10][4:]
            qpt.drawText(event.rect(), QtCore.Qt.AlignLeading|QtCore.Qt.AlignRight|QtCore.Qt.AlignTop,text)

        # 드론 상태 띄우는 부분
        qpt.setOpacity(0.7)
        if self.drone_move == 0:
            qpt.drawPixmap(405,390,150,150,self.stopsign)
        elif self.drone_move == 1:
            qpt.drawPixmap(405,390,150,150,self.forward)
        elif self.drone_move == 2:
            qpt.drawPixmap(405,390,150,150,self.back)
        elif self.drone_move == 3:
            qpt.drawPixmap(405,390,150,150,self.up)
        elif self.drone_move == 4:
            qpt.drawPixmap(405,390,150,150,self.down)
        elif self.drone_move == 5:
            qpt.drawPixmap(405,390,150,150,self.left)
        elif self.drone_move == 6:
            qpt.drawPixmap(405,390,150,150,self.right)
        elif self.drone_move == 7:
            qpt.drawPixmap(405,390,150,150,self.takeoff)
        elif self.drone_move == 8:
            qpt.drawPixmap(405,390,150,150,self.land)
        elif self.drone_move == 9:
            qpt.drawPixmap(405,390,150,150,self.cw)
        elif self.drone_move == 10:
            qpt.drawPixmap(405,390,150,150,self.ccw)

        qpt.setOpacity(1)
        qpt.end()

    
class Ui_Dialog(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        # 위젯 겉에 두르는거
        mystyle = "border-style: solid; border-width: 4px; border-color: #000000; border-radius: 10px;"
        
        #배경 크기 / 스타일 설정
        
        # vbox 하나
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        #self.verticalLayout.setStyleSheet("border-style: solid; border-width: 4px; border-color: #000000; border-radius: 10px; background-color:rgb(255, 255, 255);")
        
        # 프레임 위젯, 영상 실시간으로 받을 예정
        self.frame_label = frame_widget(self)
        
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_label.sizePolicy().hasHeightForWidth())
        self.frame_label.setSizePolicy(sizePolicy)
        
        self.verticalLayout.addWidget(self.frame_label)
        
        self.setWindowTitle('Drone')
        self.resize(960, 540)
        self.setFixedSize(960, 540)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Dialog()
    ui.show()
    sys.exit(app.exec_())

