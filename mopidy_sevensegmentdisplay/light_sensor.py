import time
import logging
from subprocess import call
from .threader import Threader

class LightSensor(Threader):

    _adc = (1 << (16 - 1)) - 1
    _voltage = 3.3
    _resistor = 10000
    _offset = 5

    _channel = None
    _value = 0
    _previous_value = 0
    _raw_value = 0
    _lightChangeEvent = False
    _light_event_threshold = 50
    _light_buffer_size = 10

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
        self._previous_value = self._value

        index = 0
        values = [self._value] * self._light_buffer_size

        while (True):
            if (self.stopped()):
                break

            self._value = self.read_value()

            average_value = sum(values) / self._light_buffer_size

            if abs(self._value - average_value) > self._light_event_threshold:
                if self._value > average_value:
                    self._lightChangeEvent = True
                    self._mqtt_publish("rpi/0/light_event", "light_on")
                else:
                    self._lightChangeEvent = True
                    self._mqtt_publish("rpi/0/light_event", "light_off") 
            elif (self._lightChangeEvent):
                self._lightChangeEvent = False
                self._mqtt_publish("rpi/0/light_event", "none")

            if (self._value <= self._previous_value - self._offset or self._value >= self._previous_value + self._offset):
                self._previous_value = self._value
                self._mqtt_publish("rpi/0/light", self._value)

            index = (index + 1) % self._light_buffer_size
            values[index] = self._value

            time.sleep(0.05)

        self._i2c.deinit()

    def read_value(self):
        try:
            self._raw_value = self._adc / 2 if self._channel is None else self._channel.value
            voltage = self._raw_value * (self._voltage / self._adc)
            resistance = self._resistor * (self._voltage - voltage) / voltage
            lux = 500 / resistance
            return lux
        except Exception as inst:
            logging.error(inst)

            return self._value

    def get_value(self):
        return self._value

    def get_raw_value(self):
        return self._raw_value

    def _mqtt_publish(self, topic, message):
        call(["mosquitto_pub", "-t", topic, "-m", message, "-u", self._mqtt_user, "-P", self._mqtt_password])
