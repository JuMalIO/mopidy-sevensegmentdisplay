import time
import logging
from subprocess import call
from .threader import Threader

class LightSensor(Threader):

    _max_value = 32768
    _channel = None
    _value = 0.5

    def __init__(self, enabled):
        super(LightSensor, self).__init__()

        if (not enabled):
            return

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
        min_value = 200 / self._max_value
        max_value = 500 / self._max_value

        while (True):
            if (self.stopped()):
                break

            self._value = self.read_value()

            if (self._value < min_value and max(values) > max_value):
                self._run_sh("run_lights_off_event.sh")
            elif (self._value > max_value and min(values) < min_value):
                self._run_sh("run_lights_on_event.sh")

            index = (index + 1) % size
            values[index] = self._value

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

    def _run_sh(self, name):
        try:
            call(["sh", os.path.join(os.path.dirname(__file__), name)])
        except Exception as inst:
            logging.error(inst)
