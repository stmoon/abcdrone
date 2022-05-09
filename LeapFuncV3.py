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
    rh_value = (0,0,0,0)
    
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
    
        
    def on_frame(self, controller):
        frame = controller.frame()
        rh_check = False
        for hand in frame.hands:
            if hand.is_right:
                rh_check = True

                arm = hand.arm
                wrist_height = arm.wrist_position[1]
                normal = hand.palm_normal
                direction = hand.direction
                pitch_value = direction.pitch * Leap.RAD_TO_DEG
                roll_value = normal.roll * Leap.RAD_TO_DEG
                grap_value = hand.grab_strength
                self.rh_value = (roll_value, wrist_height, pitch_value, grap_value)
                """
                if grap_value > 0.9:
                    self.order_name = "grip"
                elif pitch_value > 35:
                    self.order_name = "back"
                elif pitch_value < -25:
                    self.order_name = "forward"
                elif wrist_height > 200:
                    self.order_name = "up"
                elif wrist_height < 50:
                    self.order_name = "down"
                elif roll_value > 30:
                    self.order_name = "left"
                elif roll_value < -30:
                    self.order_name = "right" 
                else:
                    self.order_name = ""
                """
        if frame.hands is None or rh_check is False:
            self.rh_value = (0,0,0,0)
        
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
