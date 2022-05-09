import Drone as TD
import LeapFuncV3 as LF
import time

class Unite():
    dr = TD.drone()
    dr.cap_thread()
    dr.recv_thread()
    listener = LF.SampleListener()
    controller = LF.Leap.Controller()
    controller.add_listener(listener)
    
    is_takeoff = False
    is_ok = True
    # list to avoid order overlap
    movement_list = [False, False, False, False, False, False] 

    def list_clean(self):
        for list_val in self.movement_list:
            if list_val:
                list_val = False
    
    def before_move(self):
        self.list_clean()
        self.is_ok = False
    
    def control_drone(self):
        val = self.listener.rh_value

        lr_val = 0
        ud_val = 0
        fb_val = 0
        turn_val = 0
        to_land_check = 0
        # refine roll value 
        if val[0] < 10 and val[0] > -10:
            lr_val = 0
        elif val[0] > 60: 
            lr_val = -100
        elif val[0] < -60:
            lr_val = 100
        elif val[0] > 10:
            lr_val = int( ( (val[0] - 10) / 50 * 90 + 10) * (-1) )
        elif val[0] < -10:
            lr_val = int( ( (val[0] + 10) / 50 * 90 + 10) * (-1) )

        #refine pitch value
        if val[1] < 10 and val[1] > -10:
            fb_val = 0
        elif val[1] > 40:
            fb_val = 100
        elif val[1] < -60:
            fb_val = -100
        elif val[1] > 10:
            fb_val = int((val[1] - 10) / 30 * 90 + 10)
        elif val[1] < -10:
            fb_val = int((val[1] + 10) / 50 * 90 - 10)
        
        # ud_val = val[2]
        # turn_val = val[3]
        to_land_check = val[4]
        """
        we must normalize lr ud fb value
        plz normalize lr ud fb value before use this function.
        roll : max : -60 / 60, min : -10 / 10
        pitch : max : -60 / 40, min :- 10 / 10
        height : ?
        turn : ?
        """
        if not self.is_takeoff:
            if to_land_check > 0.8:
                if self.is_ok:
                    self.dr.takeoff()
                    self.is_ok = False
                    self.is_takeoff = True
        else:
            if to_land_check > 0.8:
                if self.is_ok:
                    self.dr.land()
                    self.is_takeoff = False
                    self.is_ok = False
            else:
                if lr_val == 0 and ud_val == 0 and fb_val == 0:
                    send_value = (0,0,0,0)
                    self.dr.remote(send_value)
                else:
                    send_value = (lr_val, ud_val, fb_val, turn_val)
                    self.dr.remote(send_value)
        print(self.is_ok)

        if "ok" in self.dr.recv_data:
            self.is_ok = True
            self.dr.recv_data = ""
		    

def main():
    
    test = Unite()
    while 1:
        test.control_drone()
        time.sleep(0.1)

if __name__ == "__main__":
    main()

