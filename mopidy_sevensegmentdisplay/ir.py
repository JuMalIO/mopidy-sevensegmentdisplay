from __future__ import division
from __future__ import unicode_literals

import time
import lirc
import logging
from subprocess import call
from threader import Threader


class IrReceiver(Threader):

    def __init__(self, ir_receiver_enabled, on_power, on_menu, on_left, on_right, on_vol_down, on_vol_up, on_mute, on_preset):
        super(IrReceiver, self).__init__()
        lirc.init("myprogram", blocking=False)

        self._on_power = on_power
        self._on_menu = on_menu
        self._on_left = on_left
        self._on_right = on_right
        self._on_vol_down = on_vol_down
        self._on_vol_up = on_vol_up
        self._on_mute = on_mute
        self._on_preset = on_preset

        if (ir_receiver_enabled):
            super(IrReceiver, self).start()

    def run(self):
        try:
            while (True):
                if (self.stopped()):
                    break
                list = lirc.nextcode()
                if len(list) != 0:
                    if list[0] == "power":
                        self._on_power()
                    elif list[0] == "input":
                        self._on_menu()
                    elif list[0] == "treble-":
                        self._on_left()
                    elif list[0] == "treble+":
                        self._on_right()
                    elif list[0] == "vol-":
                        self._on_vol_down()
                    elif list[0] == "vol+":
                        self._on_vol_up()
                    elif list[0] == "mute":
                        self._on_mute()
                    elif list[0] == "bass-":
                        self._on_preset(-1)
                    elif list[0] == "bass+":
                        self._on_preset(1)
                else:
                    time.sleep(0.1)
        except Exception as inst:
            logging.error(inst)
        lirc.deinit()


class IrSender:
    MICROLAB = "microlab"
    EDIFIER = "edifier"

    POWER = "POWER"
    VOL_UP = "VOL+"
    VOL_DOWN = "VOL-"
    BASS_UP = "BASS+"
    BASS_DOWN = "BASS-"

    def __init__(self, on_power):
        self._on_power = on_power
        self._is_power_on = False

    def stop(self):
        self.power(False)

    def power(self, value=None):
        if (value is None or value != self._is_power_on):
            self._on_power(value)
            self._send(self.MICROLAB, self.POWER)
            self._send(self.EDIFIER, self.POWER)
            self._is_power_on = value

    def volume(self, value, sleep=0.2):
        command = self.VOL_UP if value > 0 else self.VOL_DOWN
        for i in range(abs(value)):
            self._send(self.MICROLAB, command)
            time.sleep(sleep)

    def bass(self, value, sleep=0.2):
        command = self.BASS_UP if value > 0 else self.BASS_DOWN
        for i in range(abs(value)):
            self._send(self.MICROLAB, command)
            time.sleep(sleep)

    def _send(self, remote, command):
        try:
            call(["irsend", "SEND_ONCE", remote, command])
        except Exception as inst:
            logging.error(inst)
