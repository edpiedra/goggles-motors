import libraries.adafruit_servohat_utilities as su
import libraries.network_utilities as nu 
import libraries.roboclaw_utilities as ru
import time, os 
from threading import Thread 

os.system("pkill -o -u pi sshd")
time.sleep(0.5)

net = nu.NetworkUtilities()
pc_c = net._create_client("Eddy-Linux.local", 8086)

global program_mode 
program_mode = pc_c.recv(1024).decode("utf-8")

servo = su.ServoHat()
servo._pan_tilt_center("right")
servo._pan_tilt_center("left")

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

class PC():
    def __init__(self):
        self.running = True 
        
    def _destroy(self):
        self.running = False 
        
    def _run(self):
        global program_mode 

        while program_mode!="QUIT":
            pc_c.sendall(b"ok")
            commands = net._receive_list(pc_c)
            
            camera, pan, tilt = commands 
            
            if program_mode=="AUTO":
                servo._pan_tilt_change(camera, pan, tilt)

pc = PC()
pc_thread = Thread(target=pc._run)
pc_thread.start()

class Joystick():
    def __init__(self):
        self.running = True 
        
    def _destroy(self):
        self.running = False 
        
    def _run(self):
        global program_mode 
        
        joy_c = net._create_client("joystick.local", 8089)
        start_time = time.time()
        
        while self.running:
            message = net._receive_list(joy_c)
            
            program_mode, left_speed, right_speed, pan_step, tilt_step, pan_tilt_mode = message 
            
            if program_mode=="DRIVE":
                rc.set_direction(drive_address, left_speed, right_speed)
                servo._pan_tilt_change(pan_tilt_mode, pan_step, tilt_step)

            lps = (1.0 / (time.time() - start_time))
            start_time = time.time()
            
            message = [
                program_mode, left_speed, right_speed, lps
            ]
            
            net._send_list(joy_c, message)
        
joy = Joystick()
joy_thread = Thread(target=joy._run)
joy_thread.start()

i=0

while program_mode!="QUIT":
    i+=1
    
servo._pan_tilt_center("right")
servo._pan_tilt_center("left")
rc._set_direction(drive_address, 0, 0)
joy._destroy()
pc._destroy()