"""Sensirion SHT41 / SHT45 driver — I2C, address 0x44.

Docs: Sensirion SHT4x datasheet.  Uses the "high precision, no heater"
measurement (command 0xFD).
"""

import time
import struct


ADDR = 0x44
CMD_MEASURE_HIGHPREC = b"\xFD"
CMD_SOFT_RESET = b"\x94"


def _crc8(data):
    # Sensirion polynomial 0x31, init 0xFF.
    crc = 0xFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x31) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


class SHT4x:
    def __init__(self, i2c, addr=ADDR):
        self.i2c = i2c
        self.addr = addr
        # Confirm the device is present.
        if addr not in i2c.scan():
            raise OSError("SHT4x not found at 0x{:02x}".format(addr))
        self._reset()

    def _reset(self):
        self.i2c.writeto(self.addr, CMD_SOFT_RESET)
        time.sleep_ms(2)

    def read(self):
        """Returns (temperature_C, relative_humidity_%)."""
        self.i2c.writeto(self.addr, CMD_MEASURE_HIGHPREC)
        # High-precision conversion time is ~8.3 ms.
        time.sleep_ms(10)
        raw = self.i2c.readfrom(self.addr, 6)
        t_msb, t_lsb, t_crc, rh_msb, rh_lsb, rh_crc = raw
        if _crc8(raw[0:2]) != t_crc or _crc8(raw[3:5]) != rh_crc:
            raise OSError("SHT4x CRC error")
        t_raw = (t_msb << 8) | t_lsb
        rh_raw = (rh_msb << 8) | rh_lsb
        t = -45.0 + 175.0 * t_raw / 65535.0
        rh = -6.0 + 125.0 * rh_raw / 65535.0
        rh = max(0.0, min(100.0, rh))
        return t, rh
