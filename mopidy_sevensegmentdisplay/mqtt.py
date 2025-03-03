import logging
from subprocess import call


class Mqtt:

    def __init__(self, mqtt_user, mqtt_password):
        self._mqtt_user = mqtt_user
        self._mqtt_password = mqtt_password
        self._serial = self._getSerial()

    def publish(self, topic, message):
        if (self._mqtt_user and self._mqtt_password):
            call(["mosquitto_pub", "-t", "rpi/" + self._serial + "/" + topic, "-m", message, "-u", self._mqtt_user, "-P", self._mqtt_password])

    def _getSerial(self):
        serial = "0000000000000000"

        try:
            with open("/proc/cpuinfo", "r") as file:
                for line in file:
                    if line.startswith("Serial"):
                        serial = line.split(":")[1].strip()
        except Exception as inst:
            logging.error(inst)
 
        return serial
