#!/usr/bin/env python
# -- coding: utf-8 --

################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import Drone as TD

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    order_name = ""
    rh_value = (0,0,0,0,0)
    rh_check = False
    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

	
        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);
        
    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"
        del self.dr

    def on_exit(self, controller):
        print "Exited"
    
    """
    실제로 사용하는 부위는 립모션이 프레임마다 읽어오는 내용을
    분석하는 것이기 때문에
    립모션에서 제공하는 파일에서 이 부분만 수정해서 사용하고있음.
    """
    def on_frame(self, controller):
        frame = controller.frame()
        rh_checking = False
        #오른손만 사용하고 있음.
        for hand in frame.hands:
            if hand.is_right:
                rh_checking = True

                arm = hand.arm
                wrist_height = arm.wrist_position[1]
                normal = hand.palm_normal
                direction = hand.direction

                #오른 손의 pitch, roll, yaw, 팔목의 위치, 쥐는 힘을 묶어서 지정
                pitch_value = direction.pitch * Leap.RAD_TO_DEG
                roll_value = normal.roll * Leap.RAD_TO_DEG
                yaw_value = direction.yaw * Leap.RAD_TO_DEG
                grap_value = hand.grab_strength
                self.rh_value = (roll_value, pitch_value, wrist_height, yaw_value, grap_value)
        #오른손 안나오면 전부 0
        if rh_checking is False:
            self.rh_value = (0,0,0,0,0)
        self.rh_check = rh_checking
        #디버깅용
        """
        print("Pitch : ",self.rh_value[0])
        print("Roll  : ",self.rh_value[1])
        print("Heigth: ",self.rh_value[2])
        print("Yaw   : ",self.rh_value[3])
        print("Grap  : ",self.rh_value[4])
        time.sleep(0.1)
        """
        
    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
