import libraries.adafruit_servohat_utilities as su
import libraries.network_utilities as nu 
import libraries.roboclaw_utilities as ru
import time, os 
import multiprocessing as mp 

os.system("pkill -o -u pi sshd")
time.sleep(0.5)

net = nu.NetworkUtilities()

pan_tilt_map = {
    "left"  : 0,
    "right" : 1,
}

pan_tilt_code_map = {
    0   : "left",
    1   : "right",
}

def PC(
    pc_pan_step, pc_tilt_step, pc_pan_tilt_code
):
    pc_c = net._create_client("Eddy-Linux.local", 8086)
    pc_c.recv(1024) 
    
    camera_map = {
        0   : "left",
        1   : "right",
    }
    
    while program_code.value!=2:
        pc_c.sendall(b"ok")
        commands = net._receive_list(pc_c)
        
        camera, pc_pan_step.value, pc_tilt_step.value = commands
        pc_pan_tilt_code.value = pan_tilt_map[camera]
        
    net._destroy(pc_c)
        
def Joystick(
    program_code, joy_pan_tilt_code, joy_left_speed, 
    joy_right_speed, joy_pan_step, joy_tilt_step
):
    joy_c = net._create_client("joystick.local", 8089)
    
    program_map = {
        "DRIVE" : 0,
        "AUTO"  : 1,
        "QUIT"  : 2,
    }
    
    
    
    start_time = time.time()
    
    while program_code.value!=2:
        message = net._receive_list(joy_c)
        
        program_mode, joy_left_speed.value, joy_right_speed.value, joy_pan_step.value, joy_tilt_step.value, pan_tilt_mode = message 
        
        program_code.value = program_map[program_mode]
        joy_pan_tilt_code.value = pan_tilt_map[pan_tilt_mode]
        
        message = [
            program_mode
        ]
        
        net._send_list(joy_c, message)
        
    net._destroy(joy_c)

if __name__=="__main__":
    event = mp.Event()
    
    program_code = mp.Value("i", 0)
    pc_pan_tilt_code = mp.Value("i", 0)
    joy_pan_tilt_code = mp.Value("i", 0)
    
    joy_left_speed = mp.Value("d", 0.0)
    joy_right_speed = mp.Value("d", 0.0)
    joy_pan_step = mp.Value("d", 0.0)
    joy_tilt_step = mp.Value("d", 0.0)
    
    pc_pan_step = mp.Value("d", 0.0)
    pc_tilt_step = mp.Value("d", 0.0)
    
    pc = mp.Process(
        target=PC,
        args=[
            pc_pan_step, pc_tilt_step, pc_pan_tilt_code
        ]
    )
    
    pc.start()
    
    joystick = mp.Process(
        target=Joystick,
        args=[
            program_code, joy_pan_tilt_code, joy_left_speed,
            joy_right_speed, joy_pan_step, joy_tilt_step,
        ]
    )
    
    joystick.start()
    
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

    while program_code.value!=2:
        if program_code.value==0:
            rc.set_direction(
                drive_address, joy_left_speed.value, 
                joy_right_speed.value
            )
            
            servo._pan_tilt_change(
                pan_tilt_code_map[joy_pan_tilt_code.value],
                joy_pan_step.value, joy_tilt_step.value,
            )
            
        elif program_code.value==1:
            servo._pan_tilt_change(
                pan_tilt_code_map[pc_pan_tilt_code.value],
                pc_pan_step.value, pc_tilt_step.value
            )
            
    servo._pan_tilt_center("left")
    servo._pan_tilt_center("right")
    rc.set_direction(drive_address, 0, 0)
    
    pc.join()
    joystick.join()