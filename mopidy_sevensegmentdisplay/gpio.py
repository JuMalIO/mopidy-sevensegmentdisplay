from __future__ import division
from __future__ import unicode_literals

import RPi.GPIO as GPIO
import threading
import time
import logging
from threading import Timer
from subprocess import call

class Gpio:

    def __init__(self, on_power, on_input, on_down, on_up, ir_sender):
        GPIO.setmode(GPIO.BCM)

        self.RELAY_PIN = 4
        GPIO.setup(self.RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
        self.is_relay_on = False

        self.KEY_1_PIN = 5   #Play/Pause
        self.KEY_2_PIN = 6   #Stop
        self.KEY_3_PIN = 13  #Open/Close
        self.KEY_4_PIN = 19  #StandBy-On
        GPIO.setup(self.KEY_1_PIN, GPIO.IN)
        GPIO.setup(self.KEY_2_PIN, GPIO.IN)
        GPIO.setup(self.KEY_3_PIN, GPIO.IN)
        GPIO.setup(self.KEY_4_PIN, GPIO.IN)

        self.on_power = on_power
        self.on_input = on_input
        self.on_down = on_down
        self.on_up = on_up
        
        self.ir_sender = ir_sender

        GPIO.add_event_detect(self.KEY_1_PIN, GPIO.RISING, callback=self._on_button, bouncetime=300)
        GPIO.add_event_detect(self.KEY_2_PIN, GPIO.RISING, callback=self._on_button, bouncetime=300)
        GPIO.add_event_detect(self.KEY_3_PIN, GPIO.RISING, callback=self._on_button, bouncetime=300)
        GPIO.add_event_detect(self.KEY_4_PIN, GPIO.RISING, callback=self._on_button, bouncetime=300)

        self.lock = threading.Lock()

    def _on_button(self, gpio):
        if not self.lock.locked():
            if (gpio == self.KEY_1_PIN):
                self.on_down()
            elif (gpio == self.KEY_2_PIN):
                self.on_up()
            elif (gpio == self.KEY_3_PIN):
                self.on_input()
            elif (gpio == self.KEY_4_PIN):
                self.on_power()

    def switch_relay_on(self):
        self._switch_relay(True)

    def switch_relay_off(self):
        self._switch_relay(False)

    def _switch_relay(self, is_relay_on):
        if self.lock.acquire(False):
            try:
                if (is_relay_on and not self.is_relay_on):
                    GPIO.output(self.RELAY_PIN, GPIO.LOW)
                    self.is_relay_on = True
                    time.sleep(0.5)     
                    self.timer = Timer(1.0, self.ir_sender.power)
                    self.timer.start()
                elif (not is_relay_on and self.is_relay_on):
                    GPIO.output(self.RELAY_PIN, GPIO.HIGH)
                    self.is_relay_on = False
                    time.sleep(0.5)
                    self.timer = Timer(1.0, self.ir_sender.power)
                    self.timer.start()
                return True
            except Exception as inst:
                logging.error(inst)
            finally:
                self.lock.release()
        return False

    def cleanup(self):
        GPIO.cleanup()
