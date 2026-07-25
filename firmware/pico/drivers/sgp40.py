"""Sensirion SGP40 VOC sensor — I2C 0x59.

This driver returns the raw signal in ticks.  The proper VOC Index requires
Sensirion's gas-index algorithm (Apache-licensed C library).  For the Pico
we log the raw signal and let the Pi compute the index.
"""

import time


ADDR = 0x59
CMD_MEASURE_RAW = b"\x26\x0f\x80\x00\xa2\x66\x66\x93"   # default T=25, RH=50


def _crc8(data):
    crc = 0xFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


class SGP40:
    def __init__(self, i2c, addr=ADDR):
        self.i2c = i2c
        self.addr = addr
        if addr not in i2c.scan():
            raise OSError("SGP40 not found at 0x{:02x}".format(addr))

    def read_raw(self):
        self.i2c.writeto(self.addr, CMD_MEASURE_RAW)
        time.sleep_ms(35)
        r = self.i2c.readfrom(self.addr, 3)
        if _crc8(r[0:2]) != r[2]:
            raise OSError("SGP40 CRC error")
        return (r[0] << 8) | r[1]

    def read_index(self):
        # Return raw for now; Pi post-processes into VOC Index (0-500).
        return self.read_raw()
