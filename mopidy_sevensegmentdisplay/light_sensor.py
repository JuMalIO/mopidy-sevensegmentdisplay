import time
import logging
from .threader import Threader

class LightSensor(Threader):

    ADC = (1 << (16 - 1)) - 1
    OFFSET = 5

    _channel = None
    _value = 0
    _previous_value = 0
    _raw_value = 0

    def __init__(self, enabled, mqtt):
        super(LightSensor, self).__init__()

        if (not enabled):
            return

        self._mqtt = mqtt

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
        while (True):
            if (self.stopped()):
                break

            self._value = self.read_value()


            if (self._value <= self._previous_value - self.OFFSET or self._value >= self._previous_value + self.OFFSET):
                self._previous_value = self._value
                self._mqtt.publish("light", str(self._value))

            time.sleep(0.05)

        self._i2c.deinit()

    def read_value(self):
        try:
            self._raw_value = self.ADC / 2 if self._channel is None else self._channel.value
            return self._raw_value >> 4
        except Exception as inst:
            logging.error(inst)

            return self._value

    def get_value(self):
        return self._value

    def get_raw_value(self):
        return self._raw_value

    def get_ratio_value(self):
        return self._raw_value / self.ADC if self._raw_value > 0 else 0
