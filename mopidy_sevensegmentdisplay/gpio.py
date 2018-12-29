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

        self.LIGHT_SENSOR_PIN = 27
        self.lightSensor = LightSensor(self.LIGHT_SENSOR_PIN, on_light)
        if (light_sensor_enabled):
            GPIO.setup(self.LIGHT_SENSOR_PIN, GPIO.IN)
            self.lightSensor.start()

        if (relay_enabled):
            self.is_relay_on = False
            self.RELAY_PIN = 4
            GPIO.setup(self.RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)

        self.relay_enabled = relay_enabled

    def switch_relay(self, value):
        if (self.relay_enabled and self.lock.acquire()):
            try:
                if (value != self.is_relay_on):
                    GPIO.output(self.RELAY_PIN, GPIO.LOW if value else GPIO.HIGH)
                    self.is_relay_on = value
                    time.sleep(1)
                    return True
            except Exception as inst:
                logging.error(inst)
            finally:
                threading.Timer(1, self.lock.release).start()
        return False

    def cleanup(self):
        self.lightSensor.stop()
        GPIO.cleanup()


class LightSensor(Threader):

    def __init__(self, gpio, callback):
        super(LightSensor, self).__init__()
        self.gpio = gpio
        self.callback = callback
        self.value = 0

    def run(self):
        counter = 0
        while (True):
            if (self.stopped()):
                break
            value = GPIO.input(self.gpio)
            if (self.value != value):
                if (counter < 50):
                    counter += 1
                else:
                    counter = 0
                    self.value = value
                    self.callback(True if value == 1 else False)
            else:
                counter = 0
            time.sleep(0.2)
