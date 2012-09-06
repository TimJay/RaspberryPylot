'''
Short

Long ...

:author: TimJay@github
:date: 2012-09-05
:license: Creative Commons BY-NC-SA 3.0 [1]_

[1] http://creativecommons.org/licenses/by-nc-sa/3.0/deed.en_US
'''
from RaspberryPylot.common.Config import ground_config
import mavlinkv10 as mavlink
import mavutil
from PyQt4 import QtCore
import time


class UDPSender(QtCore.QThread):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        QtCore.QThread.__init__(self)
        self.exiting = False
        udp_ip = ground_config.get("remote_udp", "ip")
        udp_port = ground_config.get("remote_udp", "port")
        self._link = mavutil.mavlink_connection("udp:{}:{}".format(udp_ip, udp_port), input=False, source_system=1)
        # send initial heartbeat to get things rolling
        self.send_heartbeat()

    def __del__(self):
        '''
        We are leaving now ...
        '''
        self.exiting = True
        self.wait()

    def send_heartbeat(self):
        '''
        Send a heartbeat, so the receiver can check if it's still getting a signal.
        '''
        self._link.mav.srcComponent = 0
        self._link.mav.heartbeat_send(mavlink.MAV_TYPE_GCS, mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavlink.MAV_STATE_ACTIVE, mavlink_version=3)

    def send_servo_control(self, servo_raw_0, servo_raw_1, servo_raw_2, servo_raw_3, servo_raw_4, servo_raw_5, servo_raw_6, servo_raw_7):
        '''
        Send servo override control values for all 8 channels (usual range 1000 .. 2000)
        '''
        self._link.mav.srcComponent = mavlink.MAV_COMP_ID_SYSTEM_CONTROL
        self._link.mav.rc_channels_override_send(1, mavlink.MAV_COMP_ID_SYSTEM_CONTROL, servo_raw_0, servo_raw_1, servo_raw_2, servo_raw_3, servo_raw_4, servo_raw_5, servo_raw_6, servo_raw_7)

    def run(self):
        '''
        Main loop running at ~1Hz sending heartbeats.
        '''
        next4HzRun = time.time() + 0.25
        while not self.exiting:
            if time.time() > next4HzRun:
                # Next runtime for 1Hz
                next4HzRun += 0.25
                self.send_heartbeat()
            # Give the CPU a bit of rest.
            time.sleep(0.01)
