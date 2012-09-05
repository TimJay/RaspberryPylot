'''
Receive joystick input from `JoystickControl` via UDP packets.

:author: TimJay@github
:date: 2012-07-22
:license: Creative Commons BY-NC-SA 3.0 [1]_

[1] http://creativecommons.org/licenses/by-nc-sa/3.0/deed.en_US
'''
from RPyPCA9685 import PCA9685
import socketserver
import struct
from RaspberryPylot.common.Config import remote_config

_controller = PCA9685(0, 0x40)


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


class UDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        tmpPacket = Packet(self.request[0])
        packet = None
        if tmpPacket.msg_id == 0:
            packet = Packet_Heartbeat(tmpPacket)
            print(".")
        elif tmpPacket.msg_id == 70:
            packet = Packet_Servo_Override(tmpPacket)
            for i in range(8):
                _controller.set_position(i, packet.ch[i])
        else:
            print(tmpPacket.buffer)


if __name__ == "__main__":
    ip = remote_config.get("remote_udp", "ip")
    port = int(remote_config.get("remote_udp", "port"))
    server = socketserver.UDPServer((ip, port), UDPHandler)
    server.request_queue_size = 100
    server.max_packet_size = 264
    server.serve_forever()
