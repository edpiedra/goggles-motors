from adafruit_servokit import ServoKit
import time 

kit = ServoKit(channels=16)

min = 10
max = 170

for i in range(min, max, 10):
    print(i)
    kit.servo[0].angle = i
    kit.servo[1].angle = i

    kit.servo[2].angle = i
    kit.servo[3].angle = i
    
    time.sleep(0.5)

kit.servo[0].angle = 90
kit.servo[1].angle = 90
kit.servo[2].angle = 90
kit.servo[3].angle = 90
