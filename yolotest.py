import torch
import cv2
import numpy as np
import zmq 
import urllib
import os
import pickle
import time
import datetime
# Model
# class

# 객체 정보 송신을 위한 pub 선언
info_context = zmq.Context()
info_socket = info_context.socket(zmq.PUB) 
info_socket.bind("tcp://172.17.0.2:5555")

#ZMQ SUB 선언
frame_context = zmq.Context() 
frame_socket = frame_context.socket(zmq.SUB) 
frame_socket.connect("ipc:///home/chiz/shareF/ipc1") 
frame_socket.setsockopt_string(zmq.SUBSCRIBE, '')

#로컬 위치 내의 yolov5모델을 불러옴
path = os.getcwd()
model = torch.hub.load(path,'yolov5s', source = 'local')  # or yolov5n - yolov5x6, custom
 
# Images
#while(1):
#img = 'https://ultralytics.com/images/zidane.jpg'  # or file, Path, PIL, OpenCV, numpy, list

while True:
    #zmq로 프레임을 받고 역직렬화를 함.
    img_pik = frame_socket.recv()
    start = datetime.datetime.now()    
    img = pickle.loads(img_pik)
    end1 = datetime.datetime.now()
    #img = cv2.imread('yoloimage.jpg', 0)
    # 받은 프레임을 yolov5모델로 분석
    results = model(img)
    end = datetime.datetime.now()
    val = end-end1
    val2 = end1 - start
    print('end delay = ', val2.microseconds/1000, 'ms')
    print('sec delay = ', val.microseconds/1000, 'ms')
    # 결과값 정제과정
    df = results.pandas()  # or .show(), .save(), .crop(), .pandas(), etc.
    
    # 결과값의 dataframe
    df1 = df.xyxy[0]
    print(df1)

    # dataframe을 리스트로 변환
    df2list = df1.values
    print(df2list)
    info_pik = pickle.dumps(df2list,protocol=2)
    info_socket.send(info_pik)
    """
    # 별도의 정제과정, 여기선 사용하지 않을 것 같음.
    arealist = []
    ava = []
    bva = []

    dfhuman = df1[df1['class'] == 0]

    if len(dfhuman.index) != 0:
        length = len(dfhuman.index)
        dfhuman_xmax = dfhuman['xmax'].values
        dfhuman_xmix = dfhuman['xmin'].values
        dfhuman_ymax = dfhuman['ymax'].values
        dfhuman_ymin = dfhuman['ymin'].values
        for i in range(length):

            xval = dfhuman_xmax[i] - dfhuman_xmix[i]
            yval = dfhuman_ymax[i] - dfhuman_ymin[i]
            area = xval * yval
            ava.append(xval)
            bva.append(yval)
            arealist.append(int(area))
    print(arealist)
    """
