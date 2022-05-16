import threading 
import socket
import cv2
import zmq 
import time
"""
This is commit test
"""
#Drone Class to use Drone
class drone:


    """
    mypc_address : PC address to communicate PC and Drone
    tello_address : Drone address to communicate PC and Drone
    sock : TCP socket to use UDP (PC-Drone)
    frame : It will save frame from drone
    recv_data = data
    """

    mypc_address = ("0.0.0.0", 8889)
    tello_address = ('192.168.10.1', 8889)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    frame = None
    recv_data = ""

    
    context = zmq.Context()
    zmq_sock = context.socket(zmq.PUB) 
    zmq_sock.bind("tcp://*:5555")
    
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
    print data frome drone
    almost "OK" or battery
    it will be use thread
    """
    def receive(self):
        while True: 
            try:
                data, server = self.sock.recvfrom(1518)
                self.recv_data = data.decode(encoding="utf-8")
                print(data.decode(encoding="utf-8"))
            except Exception:
                print ('\nExit . . .\n')
                break

    def recv_thread(self):
        Th = threading.Thread(target = self.receive)
        Th.start()

    """
    capturecv / cap_thread
    Used openCV's VideoCapture
    it will be used thread too.
    
    """
    def capturecv(self):
        capture = cv2.VideoCapture('udp://0.0.0.0:11111',cv2.CAP_FFMPEG)
        if not not capture.isOpened():
            capture.open('udp://0.0.0.0:11111')
        while True:
            ret, self.frame =capture.read()
            if(ret):
                cv2.imshow('frame', self.frame)
                self.zmq_sock.send(b"f")
            if cv2.waitKey (1)&0xFF == ord ('q'):
                break
        capture.release()
        cv2.destroyAllWindows ()
        self.sock.sendto ('streamoff'.encode (' utf-8 '), self.tello_address)
    
    def cap_thread(self):
        Th = threading.Thread(target = self.capturecv)
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
        lr = str(lr)
        fb = str(fb)
        ud = str(ud)
        yaw = str(yaw)

        encode = ("rc "+ lr+
        " "+ fb+
        " "+ ud+
        " "+ yaw).encode(encoding="utf-8")
        self.sock.sendto(encode, self.tello_address)
        
      
"""
#Test Function
dr = drone()


dr.recv_thread()

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


