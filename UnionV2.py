#!/usr/bin/env python
# -- coding: utf-8 --

import Drone as TD
import LeapFuncV3 as LF
import time
import numpy as np
import zmq
import pickle

class Unite():
    dr = TD.drone()
    dr.recv_thread()
    dr.info_thread()
    listener = LF.SampleListener()
    controller = LF.Leap.Controller()
    controller.add_listener(listener)
    
    is_takeoff = False
    
    state_context = zmq.Context()
    state_socket = state_context.socket(zmq.PUB) 
    state_socket.bind("ipc:///home/chiz/shareF/ipc3")
    
    list_context = zmq.Context()
    list_socket = list_context.socket(zmq.PUB) 
    list_socket.bind("ipc:///home/chiz/shareF/ipc4")

    def control_drone(self):
        val = self.listener.rh_value
        rh_checking = self.listener.rh_check
        lr_val = 0
        ud_val = 0
        fb_val = 0
        turn_val = 0
        to_land_check = 0

        # refine roll value 

        if val[0] < 15 and val[0] > -15:
            lr_val = 0
        elif val[0] > 65: 
            lr_val = -100
        elif val[0] < -65:
            lr_val = 100
        elif val[0] > 15: # right
            lr_val = int( ( (val[0] - 10) / 50 * 90 + 10) * (-1) )
        elif val[0] < -15: # left
            lr_val = int( ( (val[0] + 10) / 50 * 90 + 10) * (-1) )
        
        #refine pitch value
        if val[1] < 20 and val[1] > -15:
            fb_val = 0
        elif val[1] > 50:
            fb_val = 100
        elif val[1] < -45:
            fb_val = -100
        elif val[1] > 20: #back
            fb_val = int((val[1] - 20) / 30 * 90 + 10) * (-1)
        elif val[1] < -15: #forward
            fb_val = int((val[1] + 20) / 30 * 90 - 10) * (-1)
        
        # ud_val = val[2]
        # 80 / 120
        
        if val[2] < 200 and val[2] > 100:
            ud_val = 0
        elif val[2] > 300:
            ud_val = 100
        elif val[2] < 20:
            ud_val = -100
        elif val[2] > 200: #up
            ud_val = int( ( (val[2] - 200) / 100 * 90 + 10 )) 
        elif val[2] < 100: #down
            ud_val = int( ( (-1) * val[2] + 100) /80 * 90 + 10) * (-1)

        # turn_val = val[3]
        
        if val[3] > 35:
            turn_val = 50
        elif val[3] < -35:
            turn_val = -50
        
        to_land_check = round(val[4],4)
        if rh_checking == False:
            ud_val = 0
        ctrl_val = [lr_val, fb_val, ud_val, turn_val, to_land_check]
        ctrl_pik = pickle.dumps(ctrl_val)
        self.list_socket.send(ctrl_pik)


        if np.abs(turn_val) > 0:
            lr_val = 0
            fb_val = 0
            ud_val = 0
        else:
            val = np.array([])
            np.append(val, np.abs(lr_val))
            np.append(val, np.abs(fb_val))
            np.append(val, np.abs(ud_val))
            
            if len(val) > 0:
                val_arg = val.argmax()
                if val_arg == 0:
                    fb_val = 0
                    ud_val = 0
                elif val_arg == 1:
                    lr_val = 0
                    ud_val = 0
                elif val_arg == 2:
                    lr_val = 0
                    fb_val = 0

        state_data = []
        if not self.is_takeoff:
            if to_land_check > 0.9:
                if self.dr.is_ok:
                    self.dr.takeoff()
                    self.dr.is_ok = False
                    self.is_takeoff = True
                    state_data.append("Takeoff")
                    state_data.append(0)
            else:
                if self.dr.is_ok:
                    state_data.append("Stop")
                    state_data.append(0)
        else:
            if self.dr.human_check == True:
                send_value = (0,0,0,0)
                self.dr.remote(send_value)
                state_data.append("Stop")
                state_data.append(0)

            elif to_land_check > 0.9:
                if self.dr.is_ok:
                    self.dr.land()
                    self.is_takeoff = False
                    self.dr.is_ok = False
                    state_data.append("Land")
                    state_data.append(0)
            else:
                if self.dr.is_ok:
                    send_value = (lr_val, fb_val, ud_val, turn_val)
                    if lr_val != 0:
                        if lr_val > 0:
                            state_data.append("Right")
                            state_data.append(lr_val)
                        elif lr_val < 0:
                            state_data.append("Left")
                            state_data.append(lr_val * (-1))
                            
                    elif fb_val != 0:
                        if fb_val > 0:
                            state_data.append("Forward")
                            state_data.append(fb_val)
                        
                        elif fb_val < 0:
                            state_data.append("Back")
                            state_data.append(fb_val * (-1))
                    
                    elif ud_val != 0:
                        if ud_val > 0:
                            state_data.append("Up")
                            state_data.append(ud_val)
                        
                        elif ud_val < 0:
                            state_data.append("Down")
                            state_data.append(ud_val * (-1))

                    elif turn_val != 0:
                        if turn_val > 0:
                            state_data.append("Clockwise")
                            state_data.append(0)
                        
                        elif turn_val < 0:
                            state_data.append("Counterclockwise")
                            state_data.append(0)
                    else:
                        state_data.append("Stop")
                        state_data.append(0)
                    self.dr.remote(send_value)
        state_pik = pickle.dumps(state_data)
        self.state_socket.send(state_pik)            

        
		    

def main():
    
    test = Unite()
    while 1:
        test.control_drone()
        time.sleep(0.1)

if __name__ == "__main__":
    main()

