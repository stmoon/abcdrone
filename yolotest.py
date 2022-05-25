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

context = zmq.Context() 
path = os.getcwd()
socket = context.socket(zmq.SUB) 
socket.connect("tcp://192.168.10.2:5555") 
socket.subscribe("")


model = torch.hub.load(path,'yolov5s', source = 'local')  # or yolov5n - yolov5x6, custom
 
# Images
#while(1):
#img = 'https://ultralytics.com/images/zidane.jpg'  # or file, Path, PIL, OpenCV, numpy, list
# 여기서부터 실시간으로 받는거임
# zmq로 numpy를 받으면
# 이게 돌아가기 시작하는거임
#이거어케함?
while True:
    start = time.time()
    img_pik = socket.recv()
    img = pickle.loads(img_pik,encoding='bytes')
    #img = cv2.imread('yoloimage.jpg', 0)

    # Inference
    results = model(img)
    val = time.time() - start
    print('delay = ', datetime.timedelta(val))
    # Results
    results.save()
    df = results.pandas()  # or .show(), .save(), .crop(), .pandas(), etc.
    df1 = df.xyxy[0]
    print(df1)
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
