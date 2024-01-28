import os
import struct
import subprocess
import tempfile
import logging
from .max7219 import Symbols


class Equalizer:

    def __init__(self, equalizer_enabled, equalizer_bars_number, equalizer_output_bit_format, equalizer_raw_target):
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

            conpat = """
            [general]
            bars = %d
            [output]
            method = raw
            raw_target = %s
            bit_format = %s
            """

            config = conpat % (equalizer_bars_number, equalizer_raw_target, equalizer_output_bit_format)
            bytetype = "H" if equalizer_output_bit_format == "16bit" else "B"
            bytesize = 2 if equalizer_output_bit_format == "16bit" else 1
            self._bytenorm = 65535 if equalizer_output_bit_format == "16bit" else 255

            with tempfile.NamedTemporaryFile() as config_file:
                config_file.write(config.encode())
                config_file.flush()

                process = subprocess.Popen(["cava", "-p", config_file.name], stdout=subprocess.PIPE)
                self._chunk = bytesize * equalizer_bars_number
                self._fmt = bytetype * equalizer_bars_number

                if (equalizer_raw_target != "/dev/stdout"):
                    if (not os.path.exists(equalizer_raw_target)):
                        os.mkfifo(equalizer_raw_target)
                    self._source = open(equalizer_raw_target, "rb")
                else:
                    self._source = process.stdout

    def get_draw_buffer(self):
        data = self._source.read(self._chunk)
        if (len(data) < self._chunk):
            return self._sample
        #self._sample = [i for i in struct.unpack(fmt, data)]  # raw values without norming
        self._sample = [self._getSymbol(i / self._bytenorm) for i in struct.unpack(self._fmt, data)]
        
        logging.error(self._sample)

        return self._sample

    def _getSymbol(self, ratio):
        if (ratio > 0.1):
            return Symbols.TOP
        elif (ratio > 0.4):
            return Symbols.MIDDLE
        elif (ratio > 0.8):
            return Symbols.BOTTOM
        return Symbols.NONE
