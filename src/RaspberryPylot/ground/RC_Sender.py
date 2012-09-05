'''
Short

Long ...

:author: TimJay@github
:date: 2012-09-05
:license: Creative Commons BY-NC-SA 3.0 [1]_

[1] http://creativecommons.org/licenses/by-nc-sa/3.0/deed.en_US
'''
from PyQt4 import QtGui, QtCore
from RaspberryPylot.common.Utils import range_convert
from RaspberryPylot.ground.QJoystick import QJoystick
from RaspberryPylot.ground.UDPSender import UDPSender
from RaspberryPylot.gen_gui.MainWindow import Ui_MainWindow
from pygame import joystick
from RaspberryPylot.common.Config import ground_config, save_ground_config

_safe_list = ['math', 'abs', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'de grees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
_safe_dict = dict([(k, locals().get(k, None)) for k in _safe_list])


class RC_Sender_GUI(QtGui.QMainWindow):

    channels_updated = QtCore.pyqtSignal(int, int, int, int, int, int, int, int)

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.qjoystick = QJoystick()
        self.udpsender = UDPSender()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.restore_state()
        self.connect_signals_slots()
        self.qjoystick.start()
        self.udpsender.start()

    def update_channels(self):
        changed = False
        for j in range(2):
            for a in range(8):
                _safe_dict["j{}a{}".format(j, a)] = self.ui.__getattribute__("verticalSlider_j_{}_a_{}".format(j, a)).value()
                _safe_dict["j{}s{}".format(j, a)] = self.ui.__getattribute__("verticalSlider_j_{}_s_{}".format(j, a)).value()
        for ch in range(8):
            oldVal = self.ui.__getattribute__("verticalSlider_ch_{}".format(ch)).value()
            newVal = self.ui.__getattribute__("verticalSlider_ch_{}".format(ch)).value()
            try:
                newVal = eval(self.ui.__getattribute__("lineEdit_ch_{}".format(ch)).text(), {"__builtins__": None}, _safe_dict)
            except (NameError, SyntaxError, AttributeError):
                pass
            if oldVal != newVal:
                self.ui.__getattribute__("verticalSlider_ch_{}".format(ch)).setValue(newVal)
                changed = True
        if changed:
            ch0 = range_convert(-100, 100, 1000, 2000, self.ui.verticalSlider_ch_0.value())
            ch1 = range_convert(-100, 100, 1000, 2000, self.ui.verticalSlider_ch_1.value())
            ch2 = range_convert(-100, 100, 1000, 2000, self.ui.verticalSlider_ch_2.value())
            ch3 = range_convert(-100, 100, 1000, 2000, self.ui.verticalSlider_ch_3.value())
            ch4 = range_convert(-100, 100, 1000, 2000, self.ui.verticalSlider_ch_4.value())
            ch5 = range_convert(-100, 100, 1000, 2000, self.ui.verticalSlider_ch_5.value())
            ch6 = range_convert(-100, 100, 1000, 2000, self.ui.verticalSlider_ch_6.value())
            ch7 = range_convert(-100, 100, 1000, 2000, self.ui.verticalSlider_ch_7.value())
            self.channels_updated.emit(ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7)

    def save_state(self):
        for j in range(2):
            for s in range(8):
                ground_config.set("steppers_j{}".format(j), "s{}val".format(s), str(self.ui.__getattribute__("verticalSlider_j_{}_s_{}".format(j, s)).value()))
        for i in range(self.ui.comboBox_preset.count()):
            ground_config.set("channel_sets", self.ui.comboBox_preset.itemText(i), str(i))
        for ch in range(8):
            channel_set = self.ui.comboBox_preset.currentText()
            if not ground_config.has_section("channel_set_{}".format(channel_set)):
                ground_config.add_section("channel_set_{}".format(channel_set))
            ground_config.set("channel_set_{}".format(channel_set), "ch{}".format(ch), str(self.ui.__getattribute__("lineEdit_ch_{}".format(ch)).text()))
        save_ground_config()

    def restore_state(self):
        for j in range(2):
            for s in range(8):
                self.ui.__getattribute__("verticalSlider_j_{}_s_{}".format(j, s)).setValue(int(ground_config.get("steppers_j{}".format(j), "s{}val".format(s))))
        for k, v in ground_config.items("channel_sets"):
            self.ui.comboBox_preset.addItem(k)
        self.restore_channels()

    def restore_channels(self):
        for ch in range(8):
            channel_set = self.ui.comboBox_preset.currentText()
            self.ui.__getattribute__("lineEdit_ch_{}".format(ch)).setText(ground_config.get("channel_set_{}".format(channel_set), "ch{}".format(ch)))

    def handle_buttons(self, j, b):
        if j == 0:
            if b == int(ground_config.get("control", "switch_control")):
                if self.ui.comboBox_preset.currentIndex() == 0:
                    self.ui.comboBox_preset.setCurrentIndex(1)
                    return
                elif self.ui.comboBox_preset.currentIndex() != 0:
                    self.ui.comboBox_preset.setCurrentIndex(0)
                    return
        for i in range(8):
            if j < 2 and b == int(ground_config.get("steppers_j{}".format(j), "s{}+".format(i))):
                value = self.ui.__getattribute__("verticalSlider_j_{}_s_{}".format(j, i)).value()
                step = int(ground_config.get("steppers_j{}".format(j), "s{}step".format(i)))
                self.ui.__getattribute__("verticalSlider_j_{}_s_{}".format(j, i)).setValue(value + step)
            elif j <= 1 and b == int(ground_config.get("steppers_j{}".format(j), "s{}-".format(i))):
                value = self.ui.__getattribute__("verticalSlider_j_{}_s_{}".format(j, i)).value()
                step = int(ground_config.get("steppers_j{}".format(j), "s{}step".format(i)))
                self.ui.__getattribute__("verticalSlider_j_{}_s_{}".format(j, i)).setValue(value - step)

    def connect_signals_slots(self):
        # Iterate over all joysticks.
        for j in range(2):
            # Iterate over all axes and emit events.
            for a in range(8):
                self.qjoystick.__getattribute__("axis_update_j_{}_a_{}".format(j, a)).connect(self.ui.__getattribute__("verticalSlider_j_{}_a_{}".format(j, a)).setValue)
                self.ui.__getattribute__("verticalSlider_j_{}_a_{}".format(j, a)).valueChanged.connect(self.update_channels)
            for s in range(8):
                self.ui.__getattribute__("verticalSlider_j_{}_s_{}".format(j, s)).valueChanged.connect(self.update_channels)
            for ch in range(8):
                self.ui.__getattribute__("lineEdit_ch_{}".format(ch)).textChanged.connect(self.update_channels)
        self.ui.pushButton_save.clicked.connect(self.save_state)
        self.ui.comboBox_preset.currentIndexChanged.connect(self.restore_channels)
        self.channels_updated.connect(self.udpsender.send_servo_control)
        self.qjoystick.button_pressed.connect(self.handle_buttons)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = RC_Sender_GUI()
    MainWindow.show()
    sys.exit(app.exec_())
