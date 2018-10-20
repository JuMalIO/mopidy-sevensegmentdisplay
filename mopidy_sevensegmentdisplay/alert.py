from __future__ import division
from __future__ import unicode_literals

import os
import math
import random
import time
import logging
from subprocess import call
from max7219 import Symbols

class Alert:
    VOL_UP = "VOL+"
    VOL_DOWN = "VOL-"
    BASS_UP = "BASS+"
    BASS_DOWN = "BASS-"
    
    A = Symbols.A
    L = Symbols.L
    E = Symbols.E
    R = Symbols.R
    T1 = Symbols.T1
    T2 = Symbols.T2

    ANIMATION_ALERT = {
        "length": 1,
        "repeat": 1,
        "sleep": 0.05,
        "buffer":
            [[0, 0, 0, 0, 0, 0, 0, A],
            [0, 0, 0, 0, 0, 0, A, 0],
            [0, 0, 0, 0, 0, A, 0, 0],
            [0, 0, 0, 0, A, 0, 0, 0],
            [0, 0, 0, A, 0, 0, 0, 0],
            [0, 0, A, 0, 0, 0, 0, 0],
            [0, A, 0, 0, 0, 0, 0, L],
            [0, A, 0, 0, 0, 0, L, 0],
            [0, A, 0, 0, 0, L, 0, 0],
            [0, A, 0, 0, L, 0, 0, 0],
            [0, A, 0, L, 0, 0, 0, 0],
            [0, A, L, 0, 0, 0, 0, E],
            [0, A, L, 0, 0, 0, E, 0],
            [0, A, L, 0, 0, E, 0, 0],
            [0, A, L, 0, E, 0, 0, 0],
            [0, A, L, E, 0, 0, 0, R],
            [0, A, L, E, 0, 0, R, 0],
            [0, A, L, E, 0, R, 0, 0],
            [0, A, L, E, R, 0, 0, T1],
            [0, A, L, E, R, 0, T1, T2],
            [0, A, L, E, R, T1, T2, 0],
            [0, A, L, E, R, T1, T2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, A, L, E, R, T1, T2, 0],
            [0, A, L, E, R, T1, T2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, A, L, E, R, T1, T2, 0],
            [0, A, L, E, R, T1, T2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, A, L, E, R, T1, T2, 0]]
    }

    def __init__(self, display, gpio, files):
        self.display = display
        self.gpio = gpio
        self.files = files

    def run(self):
        try:
            self.display.draw_animation(self.ANIMATION_ALERT["buffer"], self.ANIMATION_ALERT["repeat"], self.ANIMATION_ALERT["sleep"])

            self.gpio.switch_relay_on()
            time.sleep(10)
            
            file = random.choice(filter(lambda x: x["enabled"], self.files))
            
            self._set_irsend(self.BASS_UP, file["bass"])
            self._set_irsend(self.VOL_UP, file["volume"])
            self._play_file(file["name"])
            self._set_irsend(self.BASS_DOWN, file["bass"])
            self._set_irsend(self.VOL_DOWN, file["volume"])

            time.sleep(2)
            self.gpio.switch_relay_off()
        except Exception as inst:
            logging.error(inst)

    def _set_irsend(self, command, repeat, sleep=0.2):
        for i in range(repeat):
            call(["irsend", "SEND_ONCE", "microlab", command])
            time.sleep(sleep)

    def _play_file(self, file, repeat=1, sleep=0.5):
        for i in range(repeat):
            call(["mpg123", "-q", os.path.join(os.path.dirname(__file__), file)])
            time.sleep(sleep)
