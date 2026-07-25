"""Bit-banged HX711 driver for MicroPython on RP2040/RP2350.

Load-cell amplifier.  Datasheet: Avia Semiconductor HX711.
- 24-bit two's-complement ADC
- Data ready when DOUT goes low
- Clock 25/26/27 pulses select next channel/gain
"""

import time
from machine import Pin

_GAIN_TO_PULSES = {128: 1, 32: 2, 64: 3}   # extra pulses beyond the 24 data bits


class HX711:
    def __init__(self, dout_pin, sck_pin, gain=128):
        self.dout = Pin(dout_pin, Pin.IN)
        self.sck = Pin(sck_pin, Pin.OUT, value=0)
        self._gain_pulses = _GAIN_TO_PULSES[gain]
        self.tare_offset = 0
        self.scale = 1.0
        # Prime once so the gain setting takes effect on next read.
        self._read_raw(timeout_ms=100)

    def _read_raw(self, timeout_ms=200):
        # Wait for DOUT low = data ready.
        deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
        while self.dout.value():
            if time.ticks_diff(deadline, time.ticks_ms()) < 0:
                raise OSError("HX711 not ready")
            time.sleep_us(50)

        value = 0
        # Clock in 24 bits MSB-first.
        for _ in range(24):
            self.sck.value(1)
            time.sleep_us(1)
            value = (value << 1) | self.dout.value()
            self.sck.value(0)
            time.sleep_us(1)

        # Extra pulses to select gain/channel for the *next* conversion.
        for _ in range(self._gain_pulses):
            self.sck.value(1)
            time.sleep_us(1)
            self.sck.value(0)
            time.sleep_us(1)

        # Two's complement sign-extend.
        if value & 0x800000:
            value -= 1 << 24
        return value

    def read_raw_avg(self, samples=5):
        vals = sorted(self._read_raw() for _ in range(samples))
        # Median avoids single-sample spikes without needing float math.
        return vals[len(vals) // 2]

    def tare(self, samples=20):
        self.tare_offset = self.read_raw_avg(samples)
        return self.tare_offset

    def read_kg(self, samples=5):
        raw = self.read_raw_avg(samples)
        return (raw - self.tare_offset) * self.scale

    def power_down(self):
        self.sck.value(1)
        time.sleep_us(70)   # >60 us holds it in power-down

    def power_up(self):
        self.sck.value(0)
