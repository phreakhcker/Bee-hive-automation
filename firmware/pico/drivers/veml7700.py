"""Vishay VEML7700 ambient light sensor — I2C 0x10.

Simple auto-gain not implemented — using ALS_GAIN 1x and IT 100 ms which
covers ~0..30 000 lux at ~1.8 lux/count.  Fine for outdoor daylight sensing.
"""

import time


ADDR = 0x10
REG_CONF = 0x00
REG_ALS = 0x04


class VEML7700:
    def __init__(self, i2c, addr=ADDR):
        self.i2c = i2c
        self.addr = addr
        if addr not in i2c.scan():
            raise OSError("VEML7700 not found at 0x{:02x}".format(addr))
        # Config: gain 1x, IT 100 ms, persistence 1, ALS enabled.
        self._write16(REG_CONF, 0x0000)
        time.sleep_ms(5)

    def _write16(self, reg, val):
        buf = bytes([reg, val & 0xFF, (val >> 8) & 0xFF])
        self.i2c.writeto(self.addr, buf)

    def _read16(self, reg):
        self.i2c.writeto(self.addr, bytes([reg]))
        b = self.i2c.readfrom(self.addr, 2)
        return b[0] | (b[1] << 8)

    def read_lux(self):
        raw = self._read16(REG_ALS)
        # Resolution table: gain 1x, IT 100 ms -> 0.0576 lux/count.
        return raw * 0.0576
