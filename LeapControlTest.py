import LeapFuncV3 as LF
import time

class Unite():
    listener = LF.SampleListener()
    controller = LF.Leap.Controller()
    controller.add_listener(listener)
    
    is_takeoff = False
    is_ok = True
    
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
        lr_name = 'N'
        fb_name = 'N'
        ud_name = 'N'


        # refine roll value 

        if val[0] < 15 and val[0] > -15:
            lr_val = 0
        elif val[0] > 70: 
            lr_name = 'Right '
            lr_val = -100
        elif val[0] < -70:
            lr_name = 'Left '
            lr_val = 100
        elif val[0] > 15: # right
            lr_name = 'Right '
            lr_val = int( ( (val[0] - 15) / 50 * 90 + 10) * (-1) )
        elif val[0] < -15: # left
            lr_name = 'Left '
            lr_val = int( ( (val[0] + 15) / 50 * 90 + 10) * (-1) )
        
        #refine pitch value
        if val[1] < 20 and val[1] > -15:
            fb_val = 0
        elif val[1] > 50:
            fb_name = 'Back '
            fb_val = 100
        elif val[1] < -45:
            fb_name = 'Forward '
            fb_val = -100
        elif val[1] > 20: #back
            fb_name = 'Back '
            fb_val = int((val[1] - 20) / 30 * 90 + 10) 
        elif val[1] < -15: #forward
            fb_name = 'Forward '
            fb_val = int((val[1] + 15) / 30 * 90 - 10) 
        
        # ud_val = val[2]
        # 80 / 120
        
        if val[2] < 200 and val[2] > 100:
            ud_val = 0
        elif val[2] > 300:
            ud_name = 'Up '
            ud_val = 100
        elif val[2] < 20:
            ud_name = 'Down '
            ud_val = -100
        elif val[2] > 200: #up
            ud_name = 'Up '
            ud_val = int( ( (val[2] - 200) / 100 * 90 + 10 )) 
        elif val[2] < 100: #down
            ud_name = 'Down '
            ud_val = int( ( (-1) * val[2] + 100) /80 * 90 + 10) * (-1)

        # turn_val = val[3]
        
        if val[3] > 35:
            turn_val = 50
        elif val[3] < -35:
            turn_val = -50
        
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
                    print ("takeoff")
                    self.is_takeoff = True
        else:
            if to_land_check > 0.8:
                if self.is_ok:
                    print ("land")
                    self.is_takeoff = False
            else:
                if self.is_ok:
                    lr = lr_name + str(lr_val)
                    fb = fb_name + str(fb_val)
                    ud = ud_name + str(ud_val)
                    send_value = (lr, fb, ud, turn_val)
                    print(send_value)

		    

def main():
    print "test"
    test = Unite()
    while 1:
        test.control_drone()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
