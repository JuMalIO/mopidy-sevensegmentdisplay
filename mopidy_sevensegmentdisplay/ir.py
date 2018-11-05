from __future__ import division
from __future__ import unicode_literals

import time
import lirc
import logging
from subprocess import call
from threader import Threader


class IrReceiver(Threader):

    def __init__(self, on_power, on_input, on_down, on_up, on_vol_down, on_vol_up, on_mute, on_preset):
        super(IrReceiver, self).__init__()
        lirc.init("myprogram", blocking=False)

        self.on_power = on_power
        self.on_input = on_input
        self.on_down = on_down
        self.on_up = on_up
        self.on_vol_down = on_vol_down
        self.on_vol_up = on_vol_up
        self.on_mute = on_mute
        self.on_preset = on_preset

    def run(self):
        try:
            while (True):
                list = lirc.nextcode()
                if len(list) != 0:
                    if list[0] == "power":
                        self.on_power()
                    elif list[0] == "input":
                        self.on_input()
                    elif list[0] == "treble-":
                        self.on_down()
                    elif list[0] == "treble+":
                        self.on_up()
                    elif list[0] == "vol-":
                        self.on_vol_down()
                    elif list[0] == "vol+":
                        self.on_vol_up()
                    elif list[0] == "mute":
                        self.on_mute()
                    elif list[0] == "bass-":
                        self.on_preset("nobass")
                    elif list[0] == "bass+":
                        self.on_preset("flat")
                if (self.stopped()):
                    break
                time.sleep(0.1)
        except Exception as inst:
            logging.error(inst)
        lirc.deinit()


class IrSender:
    MICROLAB = "microlab"
    EDIFIER = "edifier"

    POWER = "POWER"

    def power(self):
        self._send(self.MICROLAB, self.POWER)
        self._send(self.EDIFIER, self.POWER)

    def _send(self, remote, button):
        try:
            call(["irsend", "SEND_ONCE", remote, button])
        except Exception as inst:
            logging.error(inst)
