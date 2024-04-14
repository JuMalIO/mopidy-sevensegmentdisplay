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

                if (data[0] != 1):
                    return

                newPipe = [data[1], data[2], data[3], data[4], data[5]]

                self._radio.stopListening()
                self._send(newPipe, data)
                self._radio.startListening()

                for pipe in self._pipes:
                    if (pipe[0] == newPipe[1] and
                        pipe[1] == newPipe[2] and
                        pipe[2] == newPipe[3] and
                        pipe[3] == newPipe[4] and
                        pipe[4] == newPipe[5]):
                        return

                self._pipes.append(newPipe)

            time.sleep(0.2)

    def stop(self):
        self.set_none_color()
        super(Led, self).stop()

    def set_color(self, red, green, blue):
        try:
            if self._radio is None:
                return

            self._radio.stopListening()

            for pipe in self._pipes:
                self._send(pipe, [0, red, green, blue])

            self._radio.startListening()
        except Exception as inst:
            logging.error(inst)

    def set_color_hsv(self, hue, sat = 1, val = 1):
        c = colorsys.hsv_to_rgb(hue / 360.0, sat, val)

        self.set_color(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))

    def set_random_color(self):
        self.set_color_hsv(random.random() * 360)

    def set_none_color(self):
        self.set_color(0, 0, 0)

    def _send(self, pipe, data):
        self._radio.openWritingPipe(pipe);

        self._radio.write(data)

        if self._radio.isAckPayloadAvailable():
            buffer = []
            self._radio.read(buffer, self._radio.getDynamicPayloadSize())
            logging.info("NRF24 ACK Received:"),
            logging.info(buffer)
        else:
            logging.info("Received: Ack only, no payload")
