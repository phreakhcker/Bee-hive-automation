"""Bosch BME280 driver — I2C, address 0x76 (or 0x77).

Minimal implementation for one-shot forced-mode reads suitable for our slow
publish cadence.  Adapted from Bosch's reference calibration math.  Returns
temperature (deg C), humidity (%RH), pressure (hPa).
"""

import time


ADDR = 0x76
REG_CALIB00 = 0x88
REG_ID = 0xD0
REG_RESET = 0xE0
REG_CTRL_HUM = 0xF2
REG_STATUS = 0xF3
REG_CTRL_MEAS = 0xF4
REG_CONFIG = 0xF5
REG_DATA = 0xF7


class BME280:
    def __init__(self, i2c, addr=ADDR):
        self.i2c = i2c
        self.addr = addr
        if addr not in i2c.scan():
            # try the alternate address once
            alt = 0x77
            if alt in i2c.scan():
                self.addr = alt
            else:
                raise OSError("BME280 not found on I2C")
        chip_id = self.i2c.readfrom_mem(self.addr, REG_ID, 1)[0]
        if chip_id not in (0x60, 0x58):
            raise OSError("BME280 unexpected chip id 0x{:02x}".format(chip_id))
        self._read_calib()
        # Configure: humidity oversampling ×1, temp ×1, pressure ×1.
        # Forced-mode measurement issued per read.
        self.i2c.writeto_mem(self.addr, REG_CTRL_HUM, b"\x01")
        # Standby 500 ms, filter off (we're not in normal mode anyway).
        self.i2c.writeto_mem(self.addr, REG_CONFIG, b"\x80")

    def _read_calib(self):
        c = self.i2c.readfrom_mem(self.addr, REG_CALIB00, 26)
        h = self.i2c.readfrom_mem(self.addr, 0xE1, 7)

        def u16(a, b): return c[b] << 8 | c[a]
        def s16(a, b):
            v = u16(a, b)
            return v - 65536 if v > 32767 else v

        self.dig_T1 = u16(0, 1)
        self.dig_T2 = s16(2, 3)
        self.dig_T3 = s16(4, 5)
        self.dig_P1 = u16(6, 7)
        self.dig_P2 = s16(8, 9)
        self.dig_P3 = s16(10, 11)
        self.dig_P4 = s16(12, 13)
        self.dig_P5 = s16(14, 15)
        self.dig_P6 = s16(16, 17)
        self.dig_P7 = s16(18, 19)
        self.dig_P8 = s16(20, 21)
        self.dig_P9 = s16(22, 23)
        self.dig_H1 = c[25]
        self.dig_H2 = (h[1] << 8 | h[0])
        if self.dig_H2 > 32767:
            self.dig_H2 -= 65536
        self.dig_H3 = h[2]
        self.dig_H4 = (h[3] << 4) | (h[4] & 0x0F)
        if self.dig_H4 > 2047:
            self.dig_H4 -= 4096
        self.dig_H5 = (h[5] << 4) | (h[4] >> 4)
        if self.dig_H5 > 2047:
            self.dig_H5 -= 4096
        self.dig_H6 = h[6] if h[6] < 128 else h[6] - 256

    def read(self):
        # Trigger forced-mode measurement (T×1, P×1, mode=forced).
        self.i2c.writeto_mem(self.addr, REG_CTRL_MEAS, b"\x25")
        # Wait for conversion (~8 ms worst case for these settings).
        for _ in range(20):
            time.sleep_ms(2)
            if not (self.i2c.readfrom_mem(self.addr, REG_STATUS, 1)[0] & 0x08):
                break

        d = self.i2c.readfrom_mem(self.addr, REG_DATA, 8)
        adc_P = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        adc_T = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)
        adc_H = (d[6] << 8) | d[7]

        # Temperature — Bosch integer/float mixed formula, kept as floats
        # for clarity because we have plenty of RAM on RP2040/RP2350.
        var1 = (adc_T / 16384.0 - self.dig_T1 / 1024.0) * self.dig_T2
        var2 = ((adc_T / 131072.0 - self.dig_T1 / 8192.0) ** 2) * self.dig_T3
        t_fine = var1 + var2
        T = t_fine / 5120.0

        # Pressure
        v1 = t_fine / 2.0 - 64000.0
        v2 = v1 * v1 * self.dig_P6 / 32768.0
        v2 = v2 + v1 * self.dig_P5 * 2.0
        v2 = v2 / 4.0 + self.dig_P4 * 65536.0
        v1 = (self.dig_P3 * v1 * v1 / 524288.0 + self.dig_P2 * v1) / 524288.0
        v1 = (1.0 + v1 / 32768.0) * self.dig_P1
        if v1 == 0:
            P = 0
        else:
            p = 1048576.0 - adc_P
            p = (p - v2 / 4096.0) * 6250.0 / v1
            v1 = self.dig_P9 * p * p / 2147483648.0
            v2 = p * self.dig_P8 / 32768.0
            P = (p + (v1 + v2 + self.dig_P7) / 16.0) / 100.0  # hPa

        # Humidity
        h = t_fine - 76800.0
        h = ((adc_H - (self.dig_H4 * 64.0 + self.dig_H5 / 16384.0 * h)) *
             (self.dig_H2 / 65536.0 *
              (1.0 + self.dig_H6 / 67108864.0 * h *
               (1.0 + self.dig_H3 / 67108864.0 * h))))
        h = h * (1.0 - self.dig_H1 * h / 524288.0)
        H = max(0.0, min(100.0, h))
        return T, H, P
