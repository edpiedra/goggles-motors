from adafruit_servokit import ServoKit
import time 

class ServoHat():
    def __init__(self): 
        print("[INFO] initializing servo hat...")
        hat = ServoKit(channels=16)
        hat.frequency = 50
        
        self.right_pan = hat.servo[2]
        self.right_tilt = hat.servo[3]
        self.right_pan_default = 155
        self.right_tilt_default = 120
        self.right_pan_angle = self.right_pan_default
        self.right_tilt_angle = self.right_tilt_default
        self.right_pan.angle = self.right_pan_angle
        self.right_tilt.angle = self.right_tilt_angle

        self.left_pan = hat.servo[0]
        self.left_tilt = hat.servo[1]
        self.left_pan_default = 25
        self.left_tilt_default = 120
        self.left_pan_angle = self.left_pan_default
        self.left_tilt_angle = self.left_tilt_default
        self.left_pan.angle = self.left_pan_angle
        self.left_tilt.angle = self.left_tilt_angle   
        
        self.pan_tilt_timers = {
            "right": time.time(),
            "left": time.time(),
            }   
        
        self.pan_tilt_limit = 2 

    def _pan_tilt(self, eye, pan, tilt):
        if eye=="right":
            self.right_pan.angle = pan
            self.right_tilt.angle = tilt

        if eye=="left":
            self.left_pan.angle = pan
            self.left_tilt.angle = tilt
                    
    def _pan_tilt_change(self, eye, pan, tilt):
        elapsed_time = time.time() - self.pan_tilt_timers[eye]
        if elapsed_time < .5:
            pan, tilt = 0, 0
            
        else:
            self.pan_tilt_timers[eye] = time.time()

        pan = max(-(self.pan_tilt_limit), min(self.pan_tilt_limit, pan))
        tilt = max(-(self.pan_tilt_limit), min(self.pan_tilt_limit, tilt))
        
        if eye=="right":
            pan = -pan
            self.right_pan_angle = max(10, min(170, self.right_pan_angle + pan))
            self.right_tilt_angle = max(10, min(170, self.right_tilt_angle + tilt))
            self.right_pan.angle = self.right_pan_angle
            self.right_tilt.angle = self.right_tilt_angle

        if eye=="left":
            pan = -pan
            self.left_pan_angle = max(10, min(170, self.left_pan_angle + pan))
            self.left_tilt_angle = max(10, min(170, self.left_tilt_angle + tilt))
            self.left_pan.angle = self.left_pan_angle
            self.left_tilt.angle = self.left_tilt_angle 
            
    def _pan_tilt_center(self, eye):
        if eye=="right":
            self.right_pan_angle = self.right_pan_default
            self.right_tilt_angle = self.right_tilt_default
            self.right_pan.angle = self.right_pan_angle
            self.right_tilt.angle = self.right_tilt_angle

        if eye=="left":
            self.left_pan_angle = self.left_pan_default
            self.left_tilt_angle = self.left_tilt_default
            self.left_pan.angle = self.left_pan_angle
            self.left_tilt.angle = self.left_tilt_angle