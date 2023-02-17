import libraries.roboclaw_utilities as ru 
import time 

serial_port = "/dev/ttyS0"
baudrate = 115200
timeout = 0.1
inter_byte_timeout = 0.1

rc = ru.RoboClaw()

ret = rc.Open(
    serial_port, baudrate, timeout, 
    inter_byte_timeout
)

drive_address = 0x80

for speed in range(-90, 90, 10):
    left_ret, right_ret = rc.set_direction(
        drive_address, speed/100, speed/100
    )

    print(left_ret, right_ret)
    time.sleep(1)

left_ret, right_ret = rc.set_direction(
    drive_address, 0.0, 0.0
)
