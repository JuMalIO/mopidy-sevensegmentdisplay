from __future__ import division
from __future__ import unicode_literals

import RPi.GPIO as GPIO
import threading
import time
import logging
from threader import Threader


class Gpio:

    def __init__(self, buttons_enabled, on_power, on_menu, on_left, on_right, light_sensor_enabled, on_light, relay_enabled):
        self.lock = threading.Lock()

        GPIO.setmode(GPIO.BCM)

        if (buttons_enabled):
            self.POWER_BUTTON_PIN = 19  # StandBy-On
            self.MENU_BUTTON_PIN = 13   # Open/Close
            self.LEFT_BUTTON_PIN = 5    # Play/Pause
            self.RIGHT_BUTTON_PIN = 6   # Stop

            GPIO.setup(self.POWER_BUTTON_PIN, GPIO.IN)
            GPIO.setup(self.MENU_BUTTON_PIN, GPIO.IN)
            GPIO.setup(self.LEFT_BUTTON_PIN, GPIO.IN)
            GPIO.setup(self.RIGHT_BUTTON_PIN, GPIO.IN)

            GPIO.add_event_detect(self.POWER_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_power() if not self.lock.locked() else None)
            GPIO.add_event_detect(self.MENU_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_menu() if not self.lock.locked() else None)
            GPIO.add_event_detect(self.LEFT_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_left() if not self.lock.locked() else None)
            GPIO.add_event_detect(self.RIGHT_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_right() if not self.lock.locked() else None)

        if (light_sensor_enabled):
            self.LIGHT_SENSOR_PIN = 27
            self.thread = LightSensor(self.LIGHT_SENSOR_PIN, on_light)
            GPIO.setup(self.LIGHT_SENSOR_PIN, GPIO.IN)
            GPIO.add_event_detect(self.LIGHT_SENSOR_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: (self.thread.stop(), self.thread.start()))

        if (relay_enabled):
            self.is_relay_on = False
            self.RELAY_PIN = 4
            GPIO.setup(self.RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)

        self.relay_enabled = relay_enabled

    def switch_relay(self, value):
        if (self.relay_enabled and self.lock.acquire(False)):
            try:
                if (value != self.is_relay_on):
                    GPIO.output(self.RELAY_PIN, GPIO.LOW if value else GPIO.HIGH)
                    self.is_relay_on = value
                    time.sleep(0.7)
                    return True
            except Exception as inst:
                logging.error(inst)
            finally:
                self.lock.release()
        return False

    def cleanup(self):
        GPIO.cleanup()


class LightSensor(Threader):

    def __init__(self, gpio, callback):
        super(LightSensor, self).__init__()
        self.gpio = gpio
        self.callback = callback

    def run(self):
        value = GPIO.input(self.gpio)
        checked_times = 0
        while (checked_times < 50):
            if (self.stopped()):
                return
            if (GPIO.input(self.gpio) != value):
                return
            checked_times += 1
            time.sleep(0.1)
        if (checked_times == 50):
            self.callback(True if value == 1 else False)
