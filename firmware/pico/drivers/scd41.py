"""Sensirion SCD41 photoacoustic NDIR CO2 sensor — I2C 0x62.

Uses low-power periodic measurement (every 30 s) which keeps average power
under 0.5 mA average.  Reads return None if data isn't ready yet.
"""

import time


ADDR = 0x62
CMD_START_LOW_POWER = b"\x21\xac"
CMD_STOP = b"\x3f\x86"
CMD_GET_DATA_READY = b"\xe4\xb8"
CMD_READ = b"\xec\x05"


def _crc8(data):
    crc = 0xFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


class SCD41:
    def __init__(self, i2c, addr=ADDR):
        self.i2c = i2c
        self.addr = addr
        if addr not in i2c.scan():
            raise OSError("SCD41 not found at 0x{:02x}".format(addr))
        try:
            self.i2c.writeto(self.addr, CMD_STOP)
            time.sleep_ms(500)
        except Exception:
            pass
        self.i2c.writeto(self.addr, CMD_START_LOW_POWER)
        time.sleep_ms(20)

    def _data_ready(self):
        self.i2c.writeto(self.addr, CMD_GET_DATA_READY)
        time.sleep_ms(2)
        r = self.i2c.readfrom(self.addr, 3)
        # Least significant 11 bits nonzero == data ready.
        return ((r[0] & 0x07) << 8 | r[1]) != 0

    def read(self):
        """Returns (co2_ppm, t_c, rh) or None if not ready yet."""
        if not self._data_ready():
            return None
        self.i2c.writeto(self.addr, CMD_READ)
        time.sleep_ms(2)
        r = self.i2c.readfrom(self.addr, 9)
        if _crc8(r[0:2]) != r[2] or _crc8(r[3:5]) != r[5] or _crc8(r[6:8]) != r[8]:
            raise OSError("SCD41 CRC error")
        co2 = (r[0] << 8) | r[1]
        t_raw = (r[3] << 8) | r[4]
        rh_raw = (r[6] << 8) | r[7]
        t = -45.0 + 175.0 * t_raw / 65535.0
        rh = 100.0 * rh_raw / 65535.0
        return co2, round(t, 2), round(rh, 1)
