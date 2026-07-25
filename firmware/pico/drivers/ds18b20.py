"""Multi-probe DS18B20 driver on the built-in MicroPython onewire/ds18x20."""

import time
import binascii
import onewire
import ds18x20
from machine import Pin


class DS18B20Array:
    def __init__(self, pin, labels=None):
        """`labels` maps 8-byte ROM address (bytes) -> human name."""
        self._ow = onewire.OneWire(Pin(pin))
        self._ds = ds18x20.DS18X20(self._ow)
        self.roms = self._ds.scan()
        if not self.roms:
            raise OSError("no DS18B20 probes on bus")
        self.labels = labels or {}
        # Set resolution to 12-bit (default) for +/- 0.0625 C.

    def _label(self, rom):
        name = self.labels.get(rom)
        if name:
            return name
        # Fall back to a stable short hex ID.
        return binascii.hexlify(rom).decode()

    def read_all(self):
        """Trigger conversion on all probes, wait, then read.

        Returns a dict keyed by probe label -> temperature in degrees C.
        Takes about 800 ms because of the 12-bit conversion time.
        """
        self._ds.convert_temp()
        time.sleep_ms(800)
        out = {}
        for rom in self.roms:
            try:
                t = self._ds.read_temp(rom)
                # Sensor returns 85.0 on read-before-first-convert; treat as None.
                if abs(t - 85.0) < 0.01:
                    out[self._label(rom)] = None
                else:
                    out[self._label(rom)] = round(t, 3)
            except Exception:
                out[self._label(rom)] = None
        return out

    def rom_list(self):
        """Handy during setup — print addresses so you can populate config."""
        return [binascii.hexlify(r).decode() for r in self.roms]
