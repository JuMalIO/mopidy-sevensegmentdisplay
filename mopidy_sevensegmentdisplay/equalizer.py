import os
import struct
import subprocess
import logging
import configparser
import pathlib
from .max7219 import Symbols


class Equalizer:

    def __init__(self, equalizer_enabled):
        super(Equalizer, self).__init__()

        if (equalizer_enabled):
            self._sample = [
                Symbols.NONE,
                Symbols.NONE,
                Symbols.NONE,
                Symbols.NONE,
                Symbols.NONE,
                Symbols.NONE,
                Symbols.NONE,
                Symbols.NONE
            ]

            config_file_name = str(pathlib.Path(__file__).parent.resolve()) + '/cava.config'
            
            logging.info('cava config: ' + config_file_name)

            config = configparser.RawConfigParser()
            config.read(config_file_name)

            general_bars = int(config.get('general', 'bars'))
            output_raw_target = config.get('output', 'raw_target')
            output_bit_format = config.get('output', 'bit_format')

            bytetype = "H" if output_bit_format == "16bit" else "B"
            bytesize = 2 if output_bit_format == "16bit" else 1
            self._bytenorm = 65535 if output_bit_format == "16bit" else 255

            process = subprocess.Popen(["cava", "-p", config_file_name], stdout=subprocess.PIPE)
            self._chunk = bytesize * general_bars
            self._fmt = bytetype * general_bars

            if (output_raw_target != "/dev/stdout"):
                if (not os.path.exists(output_raw_target)):
                    os.mkfifo(output_raw_target)
                self._source = open(output_raw_target, "rb")
            else:
                self._source = process.stdout

    def get_draw_buffer(self):
        data = self._source.read(self._chunk)
        if (len(data) < self._chunk):
            return self._sample
        self._sample = [self._getSymbol(i / self._bytenorm) for i in struct.unpack(self._fmt, data)]
        return self._sample

    def _getSymbol(self, ratio):
        if (ratio > 0.1):
            return Symbols.TOP
        elif (ratio > 0.4):
            return Symbols.MIDDLE
        elif (ratio > 0.8):
            return Symbols.BOTTOM
        return Symbols.NONE
