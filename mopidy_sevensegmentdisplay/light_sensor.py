import time
import logging
from subprocess import call
from .threader import Threader

class LightSensor(Threader):

    _max_value = 32768
    _channel = None
    _value = 0.5

    _lightChangeEvent = False

    def __init__(self, enabled, mqtt_user, mqtt_password):
        super(LightSensor, self).__init__()

        if (not enabled):
            return

        self._mqtt_user = mqtt_user
        self._mqtt_password = mqtt_password

        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn

        # Initialize the I2C interface
        self._i2c = busio.I2C(board.SCL, board.SDA)

        # Create an ADS1115 object
        self._ads = ADS.ADS1115(self._i2c)

        # Define the analog input channel
        self._channel = AnalogIn(self._ads, ADS.P0)

        super(LightSensor, self).start()

    def run(self):
        self._value = self.read_value()

        size = 10
        index = 0
        values = [self._value] * size
        increment = 0.01

        while (True):
            if (self.stopped()):
                break

            self._value = self.read_value()
            index = (index + 1) % size
            values[index] = self._value
            
            increments = [values[(index + i + 1) % size] - values[(index + i) % size] for i in range(size - 1)]
            average_increment = sum(increments) / len(increments)

            if (average_increment < -increment):
                self._lightChangeEvent = True
                self._mqtt_publish("light_off_event")
            if (average_increment > increment):
                self._lightChangeEvent = True
                self._mqtt_publish("light_on_event")
            elif (self._lightChangeEvent):
                self._lightChangeEvent = False
                self._mqtt_publish("none")

            time.sleep(0.05)

        self._i2c.deinit()

    def read_value(self):
        if (self._channel is None):
            return 0.5

        try:
            value = self._channel.value

            if (value > self._max_value):
                return 1

            return value / self._max_value
        except Exception as inst:
            logging.error(inst)

            return self._value

    def get_value(self):
        return self._value

    def get_raw_value(self):
        return self._value * self._max_value

    def _mqtt_publish(self, value):
        call(["mosquitto_pub", "-t", "rpi/0/light", "-m", value, "-u", self._mqtt_user, "-P", self._mqtt_password])
