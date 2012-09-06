'''
Created on 06.09.2012

@author: corvix
'''
from RaspberryPylot.common.Utils import range_convert
from RaspberryPylot.common.Config import remote_config
from RPyPCA9685 import PCA9685
import struct
import socket
import time
import select

class Packet():

    def __init__(self, buf):
        self.buffer = buf
        data = struct.unpack("<BBBBBB", buf[:6])
        self.start = data[0]
        self.pl_length = data[1]
        self.seq = data[2]
        self.sys_id = data[3]
        self.comp_id = data[4]
        self.msg_id = data[5]


class Packet_Servo_Override(Packet):

    def __init__(self, packet):
        Packet.__init__(self, packet.buffer)
        data = struct.unpack("<HHHHHHHHBB", packet.buffer[6:6 + self.pl_length])
        self.ch = [data[i] for i in range(8)]
        self.target_sys = data[8]
        self.target_comp = data[9]


class Packet_Heartbeat(Packet):

    def __init__(self, packet):
        Packet.__init__(self, packet.buffer)
        data = struct.unpack("<IBBBBB", packet.buffer[6:6 + self.pl_length])
        self.custom_mode = data[0]
        self.type = data[1]
        self.autopilot = data[2]
        self.base_mode = data[3]
        self.system_status = data[4]
        self.mavlink_version = data[5]

def set_fail_position(controller):
    for i in range(8):
        val = int(remote_config.get("fail", "{}".format(i)))
        controller.set_position(i, int(range_convert(-100, 100, 1000, 2000, val)))

if __name__ == '__main__':
    controller = PCA9685(0, 0x40)
    host = remote_config.get("remote_udp", "ip")
    port = int(remote_config.get("remote_udp", "port"))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2048)
    s.setblocking(False)
    last_heartbeat = 0
    fail = False
    next_run = time.time() + 0.02
    while True:
        if time.time() > next_run:
            next_run += 0.02
            read, write, error = select.select([s], [], [], 0.1)
            if len(read) > 0:
                buffer = read[0].recvfrom(256)
                tmpPacket = Packet(buffer[0])
                packet = None
                if tmpPacket.msg_id == 0:
                    packet = Packet_Heartbeat(tmpPacket)
                    last_heartbeat = time.time()
                elif tmpPacket.msg_id == 70:
                    if not fail:
                        packet = Packet_Servo_Override(tmpPacket)
                        for i in range(8):
                            controller.set_position(i, packet.ch[i])
                else:
                    print(tmpPacket.buffer)
            if not fail and time.time() - last_heartbeat > 1.0:
                set_fail_position(controller)
                fail = True
                print("In failsave mode.")
            elif fail and time.time() - last_heartbeat < 1.0:
                fail = False
                print("In normal mode.")
        time.sleep(0.005)