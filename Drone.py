#!/usr/bin/env python
# -- coding: utf-8 --

import threading 
import socket
import cv2
import zmq 
import numpy as np
import pickle
import time
import datetime
"""
한글로 가능한지 확인하는 용도
"""
#Drone Class to use Drone
class drone:


    """
    mypc_address : PC - Drone 통신 간 사용할 PC 주소
    tello_address : PC - Drone 통신 간 사용할 Drone 주소
    sock : PC - Drone UDP 통신 간 사용할 TCP 소켓
    frame : 프레임 저장용 변수 (사용안하는 중)
    recv_data = 드론에게서 받은 데이터 (Ok, Error 등)
    human_check = 사람 유무를 체크할 때 사용할 변수
    """

    mypc_address = ("0.0.0.0", 8889)
    tello_address = ('192.168.10.1', 8889)
    state_address = ("0.0.0.0", 8890)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    frame = None
    recv_data = ""
    human_check = False
    is_ok = True

    # 프레임 전송을 위한 소켓 선언, zmq의 pub로 선언
    frame_context = zmq.Context()
    frame_socket = frame_context.socket(zmq.PUB) 
    frame_socket.bind("ipc:///home/chiz/shareF/ipc1")
    
    
    # 객체 정보를 수신받기 위한 소켓 선언, zmq의 sub로 선언
    info_context = zmq.Context() 
    info_socket = info_context.socket(zmq.SUB) 
    info_socket.connect("tcp://172.17.0.2:5555") 
    info_socket.setsockopt(zmq.SUBSCRIBE, '')

    # Binding PC to Drone
    sock.bind(mypc_address)

    # We must send "command" to send order.
    # and send "streamon" to get video
    cmd = "command".encode(encoding="utf-8")
    sock.sendto(cmd, tello_address)
    so = "streamon".encode(encoding="utf-8")
    sock.sendto(so, tello_address)

    """
    receive / recv_thread
    Drone에게서 받은 데이터 출력
    Ok, Error, 배터리 퍼센티지 등
    명령어 입력 후 반환하는 데이터를 출력하는 내용
    """
    def receive(self):
        while True: 
            try:
                data, server = self.sock.recvfrom(1518)
                self.recv_data = data.decode(encoding="utf-8")
                print(data.decode(encoding="utf-8"))
                if "ok" in self.recv_data:
                    self.is_ok = True
                    self.recv_data = "" 
            except Exception:
                print ('\nExit . . .\n')
                break

    def recv_thread(self):
        Th = threading.Thread(target = self.receive)
        Th.start()

    """
    capturecv / cap_thread
    openCV의 VideoCapture를 이용해서 화면을 캡쳐함.
    캡쳐를 받은 것을 frame에 저장하고
    cv2.imshow를 이용해서 화면을 띄우고 있습니다. (이 부분은 UI만들면 지워야 할 것)
    이후 frame에 흑백처리를 하고
    pickle로 직렬화를 한 뒤에
    zmq를 이용해서 보냅니다.
    """
    def capturecv(self):
        capture = cv2.VideoCapture('udp://0.0.0.0:11111',cv2.CAP_FFMPEG)
        cnt = 0
        if not not capture.isOpened():
            capture.open('udp://0.0.0.0:11111')
        while True:
            ret, frame =capture.read()
            # 제대로 받으면 ret값은 1임, 받았을 때 진행하는 것
            if(ret):
                #opencv를 이용한 화면출력
                cv2.imshow('frame', frame)
                if cnt > 4:
                    start = datetime.datetime.now()

                    # 이미지 흑백 변환
                    grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # 이미지 리사이징 640x480
                    resize_frame = cv2.resize(grayframe, dsize=(640, 480), interpolation=cv2.INTER_AREA) 
                    """
                    # 이미지 인코딩
                    encode_result, encode_frame = cv2.imencode('.png', resize_frame)
                    """
                    # 객체 직렬화
                    img_pik = pickle.dumps(resize_frame)
                    #발신
                    self.frame_socket.send(img_pik)
                    end = datetime.datetime.now()

                    val = end - start
                    #print(val)
                    cnt = 0
                else:
                    cnt = cnt + 1
            if cv2.waitKey (1)&0xFF == ord ('q'):
                break
        capture.release()
        cv2.destroyAllWindows ()
        self.sock.sendto ('streamoff'.encode (' utf-8 '), self.tello_address)
    
    def cap_thread(self):
        Th = threading.Thread(target = self.capturecv)
        Th.start()
    
    def infoget(self):
        while True:
            info_pik = self.info_socket.recv()
            info = pickle.loads(info_pik)
            print(info)
            if len(info) == 0:
                self.human_check = False
                print('nothing in here')
            else:
                human_list = []
                for i in range(len(info)):
                    if info[i][5] == 0:
                        if info[i][2] < 215 or info[i][0] > 430:
                            pass
                        else:
                            size = info[i][2] - info[i][0]
                            if size > 160:
                                human_list.append(info[i])
                
                if len(human_list) != 0:
                    print('human appear')
                    self.human_check = True
                else:
                    print('no one')
                    self.human_check = False
    
    def info_thread(self):
        Th = threading.Thread(target= self.infoget)
        Th.start()

    """
    up / down / forward / back / left / right
    default = 50(cm)
    it will send order to drone
    """
    def up(self, distance = 50):
        encode = ("up " + str(distance)).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    def down(self, distance = 50):
        encode = ("down " + str(distance)).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    def forward(self, distance = 50):
        encode = ("forward " + str(distance)).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    def back(self, distance = 50):
        encode = ("back " + str(distance)).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    def left(self, distance = 50):
        encode = ("left " + str(distance)).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    def right(self, distance = 50):
        encode = ("right " + str(distance)).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    """
    cw / ccw
    Turn
    """
    def cw(self, range = 50):
        encode = ("cw " + str(range)).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    def ccw(self, range = 50):
        encode = ("ccw " + str(range)).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)

    """
    takeoff / land / battery
    takeoff / land / battery.
    """
    def takeoff(self):
        encode = ("takeoff").encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
        
    def land(self):
        encode = ("land").encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
        
    def battery(self):
        encode = ("battery?").encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    def command(self):
        encode = ("command").encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)

    def speed(self, sp = 100):
        encode = ("speed " + str(sp)).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    def stop(self):
        encode = ("stop").encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
    
    def remote(self, val = (0,0,0,100)):

        lr, fb, ud,  yaw = val
        # 좌우 이동 값
        lr = str(lr)
        # 앞뒤 이동 값
        fb = str(fb)
        # 위 아래 이동 값
        ud = str(ud)
        yaw = str(yaw)

        encode = ("rc "+ lr+
        " "+ fb+
        " "+ ud+
        " "+ yaw).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
        
      
"""
#드론 테스트용 코드
dr = drone()


dr.recv_thread()
dr.cap_thread()
dr.info_thread()
while True: 

    try:
        msg = raw_input("")

        if not msg:
            break  

        if 'end' in msg:
            print ('...')
            dr.sock.close()  
            break

        if msg == "u":
            dr.up()
        elif msg =="d":
            dr.down()
        elif msg == "f":
            dr.forward()
        elif msg == "b":
            dr.back()
        elif msg == "l":
            dr.left()
        elif msg == "r":
            dr.right()
        elif msg == "la":
            dr.land()
        elif msg == "t":
            dr.takeoff()
        elif msg == "c":
            dr.command()
        elif msg == "s":
            dr.speed()
        elif msg == "stop":
            dr.stop()
        elif msg == "rc":
            dr.remote()
        elif msg == "bt":
            dr.battery()

    except KeyboardInterrupt:
        print ('\n . . .\n')
        dr.sock.close()  
        break
"""



