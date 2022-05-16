import time 
import zmq 

context = zmq.Context() 

socket = context.socket(zmq.SUB) 
socket.connect("tcp://localhost:5555") 
t0 = time.time()
socket.subscribe("")

while True: # Wait for next request from client 
    message = socket.recv()
    # print("Received request: %s" % message) # Do some 'work' 
    time.sleep(1) # Send reply back to client 
    print(message)