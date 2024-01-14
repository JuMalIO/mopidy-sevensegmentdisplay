import RPi.GPIO as GPIO
import threading
import time
import logging
from datetime import datetime
from .max7219 import Symbols
from .threader import Threader


class Gpio:
    POWER_BUTTON_PIN = 19  # StandBy-On
    MENU_BUTTON_PIN = 13   # Open/Close
    LEFT_BUTTON_PIN = 5    # Play/Pause
    RIGHT_BUTTON_PIN = 6   # Stop
    LIGHT_SENSOR_PIN = 27
    RELAY_PIN = 4

    def __init__(self, buttons_enabled, on_power, on_menu, on_left, on_right, light_sensor_enabled, on_light, relay_enabled):
        self._lock = threading.Lock()

        GPIO.setmode(GPIO.BCM)

        if (buttons_enabled):
            GPIO.setup(self.POWER_BUTTON_PIN, GPIO.IN)
            GPIO.setup(self.MENU_BUTTON_PIN, GPIO.IN)
            GPIO.setup(self.LEFT_BUTTON_PIN, GPIO.IN)
            GPIO.setup(self.RIGHT_BUTTON_PIN, GPIO.IN)

            GPIO.add_event_detect(self.POWER_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_power() if not self._lock.locked() else None)
            GPIO.add_event_detect(self.MENU_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_menu() if not self._lock.locked() else None)
            GPIO.add_event_detect(self.LEFT_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_left() if not self._lock.locked() else None)
            GPIO.add_event_detect(self.RIGHT_BUTTON_PIN, GPIO.RISING, bouncetime=300,
                                  callback=lambda gpio: on_right() if not self._lock.locked() else None)

        self._light_sensor = LightSensor(self.LIGHT_SENSOR_PIN, on_light)
        if (light_sensor_enabled):
            GPIO.setup(self.LIGHT_SENSOR_PIN, GPIO.IN)
            self._light_sensor.start()

        if (relay_enabled):
            self._is_relay_on = False
            GPIO.setup(self.RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)

        self._relay_enabled = relay_enabled

    def get_draw_sleep_animation(self):
        return self._light_sensor.ANIMATION_SLEEP

    def switch_relay(self, value):
        if (self._relay_enabled and self._lock.acquire()):
            try:
                if (value != self._is_relay_on):
                    GPIO.output(self.RELAY_PIN, GPIO.LOW if value else GPIO.HIGH)
                    self._is_relay_on = value
                    time.sleep(1)
                    return True
            except Exception as inst:
                logging.error(inst)
            finally:
                threading.Timer(1, self._lock.release).start()
        return False

    def cleanup(self):
        self._light_sensor.stop()
        GPIO.cleanup()


class LightSensor(Threader):
    S = Symbols.S
    L = Symbols.L
    E = Symbols.E
    P = Symbols.P

    ANIMATION_SLEEP = {
        "length": 2,
        "repeat": 1,
        "sleep": 0.05,
        "buffer": [
            [0, 0, 0, 0, 0, 0, 0, S],
            [0, 0, 0, 0, 0, 0, S, 0],
            [0, 0, 0, 0, 0, S, 0, 0],
            [0, 0, 0, 0, S, 0, 0, 0],
            [0, 0, 0, S, 0, 0, 0, 0],
            [0, 0, S, 0, 0, 0, 0, L],
            [0, 0, S, 0, 0, 0, L, 0],
            [0, 0, S, 0, 0, L, 0, 0],
            [0, 0, S, 0, L, 0, 0, 0],
            [0, 0, S, L, 0, 0, 0, E],
            [0, 0, S, L, 0, 0, E, 0],
            [0, 0, S, L, 0, E, 0, 0],
            [0, 0, S, L, E, 0, 0, E],
            [0, 0, S, L, E, 0, E, 0],
            [0, 0, S, L, E, E, 0, 0],
            [0, 0, S, L, E, E, 0, P],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, S, L, E, E, P, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, S, L, E, E, P, 0]
        ]
    }

    def __init__(self, gpio, callback):
        super(LightSensor, self).__init__()
        self._gpio = gpio
        self._callback = callback
        self._value = 0

    def run(self):
        counter = 0
        while (True):
            if (self.stopped()):
                break
            value = GPIO.input(self._gpio)
            if (self._value != value):
                if (counter < 50):
                    counter += 1
                else:
                    counter = 0
                    self._value = value
                    self._callback(datetime.now(), True if value == 1 else False)
            else:
                counter = 0
            time.sleep(0.2)
