'''
Short

Long ...

:author: TimJay@github
:date: 2012-09-05
:license: Creative Commons BY-NC-SA 3.0 [1]_

[1] http://creativecommons.org/licenses/by-nc-sa/3.0/deed.en_US
'''
from PyQt4 import QtCore
import pygame
from pygame import joystick
import time


class QJoystick(QtCore.QThread):
    '''
    classdocs
    '''
    axis_update_j_0_a_0 = QtCore.pyqtSignal(int)
    axis_update_j_0_a_1 = QtCore.pyqtSignal(int)
    axis_update_j_0_a_2 = QtCore.pyqtSignal(int)
    axis_update_j_0_a_3 = QtCore.pyqtSignal(int)
    axis_update_j_0_a_4 = QtCore.pyqtSignal(int)
    axis_update_j_0_a_5 = QtCore.pyqtSignal(int)
    axis_update_j_0_a_6 = QtCore.pyqtSignal(int)
    axis_update_j_0_a_7 = QtCore.pyqtSignal(int)
    axis_update_j_1_a_0 = QtCore.pyqtSignal(int)
    axis_update_j_1_a_1 = QtCore.pyqtSignal(int)
    axis_update_j_1_a_2 = QtCore.pyqtSignal(int)
    axis_update_j_1_a_3 = QtCore.pyqtSignal(int)
    axis_update_j_1_a_4 = QtCore.pyqtSignal(int)
    axis_update_j_1_a_5 = QtCore.pyqtSignal(int)
    axis_update_j_1_a_6 = QtCore.pyqtSignal(int)
    axis_update_j_1_a_7 = QtCore.pyqtSignal(int)
    button_pressed = QtCore.pyqtSignal(int, int)

    def __init__(self):
        '''
        Constructor
        '''
        pygame.init()
        # Initialise all joysticks.
        for j in range(0, joystick.get_count()):
            stick = joystick.Joystick(j)
            stick.init()
        # Pre-fill _last_button_state with 0
        self._last_button_state = [[False for b in range(joystick.Joystick(j).get_numbuttons())] for j in range(joystick.get_count())]
        self._last_button_time = [[0 for b in range(joystick.Joystick(j).get_numbuttons())] for j in range(joystick.get_count())]
        QtCore.QThread.__init__(self)
        # Are we exiting the loop?
        self._exiting = False

    def __del__(self):
        '''
        We are leaving now ...
        '''
        self.exiting = True
        self.wait()

    def run(self):
        '''
        Main loop running at ~50Hz
        '''
        next_run = time.time() + 0.02
        while not self._exiting:
            if time.time() > next_run:
                # Next runtime for 50Hz
                next_run = time.time() + 0.02
                # Get new pygame events.
                pygame.event.pump()
                # Iterate over all joysticks.
                for j in range(joystick.get_count()):
                    stick = joystick.Joystick(j)
                    # Iterate over all axes and emit events.
                    for a in range(stick.get_numaxes()):
                        self.__getattribute__("axis_update_j_{}_a_{}".format(j, a)).emit(int(100 * stick.get_axis(a)))
                    # Iterate over all buttons and emit events if previous state was False and now is True
                    for b in range(stick.get_numbuttons()):
                        current_state = stick.get_button(b)
                        if self._last_button_state[j][b] == False and current_state == True:
                            self._last_button_state[j][b] = True
                            self.button_pressed.emit(j, b)
                        if self._last_button_state[j][b] == True and current_state == True:
                            if self._last_button_time[j][b] == 0:
                                self._last_button_time[j][b] = time.time()
                            else:
                                if time.time() - self._last_button_time[j][b] > 0.5:
                                    self.button_pressed.emit(j, b)
                                    self._last_button_time[j][b] = 0
                        if self._last_button_state[j][b] == True and current_state == False:
                            self._last_button_state[j][b] = False
                            self._last_button_time[j][b] = 0
            # Give the CPU a bit of rest.
            time.sleep(0.01)
