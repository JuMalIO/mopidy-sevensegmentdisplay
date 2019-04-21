from __future__ import division
from __future__ import unicode_literals

import os
import random
import time
import logging
import json
from subprocess import call
from max7219 import Symbols


class Alert:
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
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, A],
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
            [0, A, L, E, R, T1, T2, 0]
        ]
    }

    def __init__(self, music, display, ir_sender, files):
        self._music = music
        self._display = display
        self._ir_sender = ir_sender
        self._files = json.loads(files)

    def run(self):
        try:
            self._display.set_power_on()
            self._display.draw_animation(self.ANIMATION_ALERT["buffer"], self.ANIMATION_ALERT["repeat"], self.ANIMATION_ALERT["sleep"])

            if (not self._music.is_playing()):
                self._ir_sender.power(True)
                time.sleep(10)

            file = random.choice(filter(lambda x: x["enabled"], self._files))

            self._ir_sender.bass(file["bass"])
            self._ir_sender.volume(file["volume"])
            self._play_file(file["name"])
            self._ir_sender.volume(- file["volume"])

            if (not self._music.is_playing()):
                time.sleep(5)
                self._ir_sender.power(False)
        except Exception as inst:
            logging.error(inst)

    def _play_file(self, file, repeat=1, sleep=0.5):
        for i in range(repeat):
            call(["mpg123", "-q", os.path.join(os.path.dirname(__file__), file)])
            time.sleep(sleep)
