import colorsys
import random
import json
import logging


class Led:

    def __init__(self, led_enabled, ips):
        self._led_enabled = led_enabled
        self._ips = json.loads(ips)

    def stop(self):
        self.set_none_color()

    def set_color(self, red, green, blue):
        if not self._led_enabled:
            return

        #try:
        #except Exception as inst:
        #    logging.error(inst)

    def set_color_hsv(self, hue, sat = 1, val = 1):
        c = colorsys.hsv_to_rgb(hue / 360.0, sat, val)

        self.set_color(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))

    def set_random_color(self, seed = None):
        hue = (random.random() if seed is None else random.Random(seed).random()) * 360
        self.set_color_hsv(hue)

    def set_none_color(self):
        self.set_color(0, 0, 0)
