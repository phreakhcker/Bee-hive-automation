"""Pack voltage monitor via ADC + resistive divider.

Divider: pack+ -- 100k -- ADC -- 22k -- GND
Ratio = (100 + 22) / 22 = 5.545x.  Tune BATT_DIVIDER_RATIO in config after
comparing readings to a DMM.

Reads are median-of-5 to suppress ADC noise.
"""

from machine import ADC, Pin


class BatteryMonitor:
    def __init__(self, adc_pin, divider_ratio, adc_vref=3.30):
        self.adc = ADC(Pin(adc_pin))
        self.ratio = divider_ratio
        self.vref = adc_vref

    def read_v(self, samples=5):
        vals = sorted(self.adc.read_u16() for _ in range(samples))
        raw = vals[len(vals) // 2]
        v_at_adc = raw * self.vref / 65535.0
        return v_at_adc * self.ratio
