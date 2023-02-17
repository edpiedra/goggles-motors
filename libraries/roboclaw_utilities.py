import serial 

class RoboClaw():
    def __init__(self):
        self.crc = 0
        self.tries_timeout = 3
        
    def Open(
        self, 
        port="/dev/serial0",
        baudrate=115200,
        timeout=0.1,
        inter_byte_timeout=0.1
    ):
#        try:
        self.port = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            inter_byte_timeout=inter_byte_timeout
        )
        
        self.port.close()
        self.port.open()
        return True
#        except:
#            return False 
        
    def _destroy(self):
        self.port.close()
        
    class Cmd():
        M1Forward   =   0
        M1Backward  =   1
        M2Forward   =   4
        M2Backward  =   5
        MixForward  =   8
        MixBackward =   9
        MixRight    =  10
        MixLeft     =  11
        M1RdEncVal  =  16
        M2RdEncVal  =  17
        M1Speed     =  18
        M2Speed     =  19
        M1RawSpeed  =  30
        M2RawSpeed  =  31
        M1SpeedPos  = 122
        M2SpeedPos  = 123
        
    #basics
    def _to_binary(self, data):
        return data.to_bytes(
            length=1,
            byteorder="big",
            signed=False,
        )
        
    def _from_binary(self, binary):
        return int.from_bytes(
            binary,
            byteorder="big",
            signed=False,
        )
        
    #read/write
    def _read_byte(self):
        binary = self.port.read(1)
        if len(binary) > 0:
            return True, self._from_binary(binary)
        
        return False, 0
    
    def _write_byte(self, data):
        binary = self._to_binary(data)
        ret = self.port.write(binary)
        
        return ret 
    
    def _write_crc_byte(self, data):
        self._crc_update(data)
        ret = self._write_byte(data)
        
        return ret 
      
    def _write_crc_word(self, data):
        if self._write_byte((data >> 8) & 0xFF):
            self._crc_update((data >> 8) & 0xFF)
            
            if self._write_byte(data & 0xFF):
                self._crc_update(data & 0xFF)
                
                return True
            
        return False
            
    #checksums
    def _refresh(self):
        self.crc = 0
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()

    def _crc_update(self, data):
        self.crc = self.crc ^ (data << 8)
        
        for bit in range(0,8):
            if (self.crc & 0x8000)==0x8000:
                self.crc = (self.crc << 1) ^ 0x1021
            else:
                self.crc = self.crc << 1
                
    def _write_checksum(self):
        if self._write_crc_word(self.crc & 0xFFFF):
            ret, valid = self._read_byte()
            
            if ret: #should technically be if valid==0xFF
                return True 
        
        return False
        
    #command formats
    def _send_command(self, address, command):
        self._refresh()
        if self._write_crc_byte(address):
            if self._write_crc_byte(command):
                return True
            
        return False
    
    def _drive_command(self, address, command, value):
        if self._send_command(address, command):
            if self._write_crc_byte(value):
                if self._write_checksum():
                    return True 
                
        return False
    
    #program commands
    def set_direction(self, address, left_speed, right_speed):
        if left_speed >= 0:
            left_command = self.Cmd.M2Forward
            left_speed = int(left_speed * 127)
        else:
            left_command = self.Cmd.M2Backward
            left_speed = int(-left_speed * 127)
            
        if right_speed >= 0:
            right_command = self.Cmd.M1Forward
            right_speed = int(right_speed * 127)
        else:
            right_command = self.Cmd.M1Backward
            right_speed = int(-right_speed * 127)
            
        left_ret = self._drive_command(address, left_command, left_speed)
        right_ret = self._drive_command(address, right_command, right_speed)
        
        return left_ret, right_ret