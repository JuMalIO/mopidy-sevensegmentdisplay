import colorsys
import random
import json
import logging
import time
import RPi.GPIO as GPIO
from .lib_nrf24 import NRF24
from .threader import Threader


class Led(Threader):

    def __init__(self, led_enabled, pipes):
        super(Led, self).__init__()

        self._radio = None
        self._pipes = json.loads(pipes)
        self._size = 8

        if (not led_enabled):
            return

        GPIO.setmode(GPIO.BCM)

        readingPipe = [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]

        import spidev
        spi = spidev.SpiDev()
        spi.open(0, 1)
        spi.cshigh = False
        spi.max_speed_hz = 500000
        spi.mode = 0

        self._radio = NRF24(GPIO, spi)
        self._radio.begin(1, 25)

        self._radio.setPayloadSize(self._size)
        self._radio.setChannel(0x76)
        self._radio.setDataRate(NRF24.BR_1MBPS)
        self._radio.setPALevel(NRF24.PA_MAX)
        self._radio.setAutoAck(True)
        self._radio.openReadingPipe(1, readingPipe)

        self._radio.startListening()

        super(Led, self).start()

    def run(self):
        while (True):
            if (self.stopped()):
                break

            if (self._radio.available()):
                data = []

                self._radio.read(data, self._size)

                logging.info(data)

                if (data[0] == 1):
                    new_pipe = [data[1], data[2], data[3], data[4], data[5]]

                    self._radio.stopListening()
                    self._send(new_pipe, data)
                    self._radio.startListening()

                    if (not self._pipe_exists(new_pipe)):
                        self._pipes.append(new_pipe)

            time.sleep(0.2)

    def stop(self):
        self.set_none_color()
        super(Led, self).stop()

    def set_color(self, red, green, blue):
        try:
            if self._radio is None:
                return

            self._radio.stopListening()

            retry = 5
            success_index = []
            for x in range(retry):
                for index, pipe in enumerate(self._pipes):
                    if (index in success_index):
                        continue
                    if (self._send(pipe, [0, red, green, blue]) > 0):
                        success_index.append(index)

                if (len(success_index) == len(self._pipes)):
                    break

            self._radio.startListening()
        except Exception as inst:
            logging.error(inst)

    def set_color_hsv(self, hue, sat = 1, val = 1):
        c = colorsys.hsv_to_rgb(hue / 360.0, sat, val)

        self.set_color(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))

    def set_random_color(self, seed = None):
        hue = (random.random() if seed is None else random.Random(seed).random()) * 360
        self.set_color_hsv(hue)

    def set_none_color(self):
        self.set_color(0, 0, 0)

    def _pipe_exists(self, new_pipe):
        for pipe in self._pipes:
            if (pipe[0] == new_pipe[0] and
                pipe[1] == new_pipe[1] and
                pipe[2] == new_pipe[2] and
                pipe[3] == new_pipe[3] and
                pipe[4] == new_pipe[4]):
                return True
        return False

    def _send(self, pipe, data):
        self._radio.openWritingPipe(pipe);

        return self._radio.write(data)
