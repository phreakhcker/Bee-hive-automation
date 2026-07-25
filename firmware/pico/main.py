"""Beehive Pico firmware — sensor aggregator.

Reads all configured sensors on their natural cadences and publishes a JSON
packet on USB-CDC once per second.  Accepts commands (tare, calibrate, ping)
on the same channel.  Runs on MicroPython 1.22+ on a Pi Pico or Pico 2.
"""

import gc
import json
import sys
import time
import select
from machine import I2C, Pin, ADC

import config as cfg


def _now_ms():
    return time.ticks_ms()


def _now_s():
    return time.time()


def _log(msg):
    # Structured log lines are prefixed with "#" so the Pi ingest ignores them
    # while a human can still read them on a serial monitor.
    print("# " + msg)


class SensorHub:
    def __init__(self):
        self.i2c0 = I2C(0, sda=Pin(cfg.I2C0_SDA), scl=Pin(cfg.I2C0_SCL),
                        freq=cfg.I2C0_FREQ)
        self.i2c1 = I2C(1, sda=Pin(cfg.I2C1_SDA), scl=Pin(cfg.I2C1_SCL),
                        freq=cfg.I2C1_FREQ)

        self.hx711 = None
        self.ds18b20 = None
        self.sht41 = None
        self.bme280 = None
        self.veml7700 = None
        self.scd41 = None
        self.sgp40 = None
        self.gate = None
        self.battery = None

        self._init_drivers()

        # Slow-sensor cadence bookkeeping
        self._last_slow_read = 0
        self._cache = {}

    def _init_drivers(self):
        if cfg.ENABLE_HX711:
            try:
                from drivers.hx711 import HX711
                self.hx711 = HX711(cfg.HX711_DOUT, cfg.HX711_SCK, cfg.HX711_GAIN)
                self.hx711.tare_offset = cfg.HX711_TARE_OFFSET
                self.hx711.scale = cfg.HX711_SCALE
                _log("hx711 ready")
            except Exception as e:
                _log("hx711 init failed: {}".format(e))

        if cfg.ENABLE_DS18B20:
            try:
                from drivers.ds18b20 import DS18B20Array
                self.ds18b20 = DS18B20Array(cfg.ONEWIRE_PIN, cfg.DS18B20_LABELS)
                _log("ds18b20: {} probes".format(len(self.ds18b20.roms)))
            except Exception as e:
                _log("ds18b20 init failed: {}".format(e))

        if cfg.ENABLE_SHT41:
            try:
                from drivers.sht4x import SHT4x
                self.sht41 = SHT4x(self.i2c0)
                _log("sht41 ready")
            except Exception as e:
                _log("sht41 init failed: {}".format(e))

        if cfg.ENABLE_BME280:
            try:
                from drivers.bme280 import BME280
                self.bme280 = BME280(self.i2c0)
                _log("bme280 ready")
            except Exception as e:
                _log("bme280 init failed: {}".format(e))

        if cfg.ENABLE_VEML7700:
            try:
                from drivers.veml7700 import VEML7700
                self.veml7700 = VEML7700(self.i2c1)
                _log("veml7700 ready")
            except Exception as e:
                _log("veml7700 init failed: {}".format(e))

        if cfg.ENABLE_SCD41:
            try:
                from drivers.scd41 import SCD41
                self.scd41 = SCD41(self.i2c1)
                _log("scd41 ready")
            except Exception as e:
                _log("scd41 init failed: {}".format(e))

        if cfg.ENABLE_SGP40:
            try:
                from drivers.sgp40 import SGP40
                self.sgp40 = SGP40(self.i2c1)
                _log("sgp40 ready")
            except Exception as e:
                _log("sgp40 init failed: {}".format(e))

        if cfg.ENABLE_BEE_GATE:
            try:
                from drivers.bee_gate import BeeGate
                self.gate = BeeGate(cfg.BEE_GATE_BEAM_A_PINS,
                                    cfg.BEE_GATE_BEAM_B_PINS,
                                    cfg.BEE_GATE_DIRECTION_WINDOW_MS,
                                    cfg.BEE_GATE_DEBOUNCE_MS)
                _log("bee_gate ready ({} channels)".format(
                    len(cfg.BEE_GATE_BEAM_A_PINS)))
            except Exception as e:
                _log("bee_gate init failed: {}".format(e))

        if cfg.ENABLE_BATTERY_MONITOR:
            try:
                from drivers.battery_monitor import BatteryMonitor
                self.battery = BatteryMonitor(cfg.BATT_ADC_PIN,
                                              cfg.BATT_DIVIDER_RATIO,
                                              cfg.BATT_ADC_VREF)
                _log("battery monitor ready")
            except Exception as e:
                _log("battery init failed: {}".format(e))

    def read_all(self):
        """Assemble one packet.  Slow sensors are read every SLOW_INTERVAL_S."""
        now_ms = _now_ms()
        do_slow = (time.ticks_diff(now_ms, self._last_slow_read) >=
                   cfg.SLOW_INTERVAL_S * 1000)
        if do_slow:
            self._last_slow_read = now_ms

        pkt = {"t": _now_s()}

        # Fast sensors
        if self.hx711:
            try:
                pkt["w_kg"] = round(self.hx711.read_kg(cfg.HX711_SAMPLES), 3)
            except Exception as e:
                pkt["w_kg"] = None
                _log("hx711 read err: {}".format(e))

        if self.sht41:
            try:
                t, rh = self.sht41.read()
                pkt["t_in"] = round(t, 2)
                pkt["rh_in"] = round(rh, 1)
            except Exception as e:
                pkt["t_in"] = pkt["rh_in"] = None
                _log("sht41 read err: {}".format(e))

        if self.bme280:
            try:
                t, rh, p = self.bme280.read()
                pkt["t_out"] = round(t, 2)
                pkt["rh_out"] = round(rh, 1)
                pkt["p_hpa"] = round(p, 2)
            except Exception as e:
                pkt["t_out"] = pkt["rh_out"] = pkt["p_hpa"] = None
                _log("bme280 read err: {}".format(e))

        if self.gate:
            counts = self.gate.consume_counts()
            pkt["bees_in"] = counts["in"]
            pkt["bees_out"] = counts["out"]
            pkt["bees_ambiguous"] = counts["ambiguous"]

        if self.battery:
            try:
                pkt["v_pack"] = round(self.battery.read_v(), 3)
            except Exception as e:
                pkt["v_pack"] = None
                _log("battery read err: {}".format(e))

        # Slow sensors — read on cadence, cache in between
        if do_slow:
            if self.ds18b20:
                try:
                    self._cache["t_probes"] = self.ds18b20.read_all()
                except Exception as e:
                    self._cache["t_probes"] = None
                    _log("ds18b20 read err: {}".format(e))
            if self.veml7700:
                try:
                    self._cache["lux"] = round(self.veml7700.read_lux(), 1)
                except Exception as e:
                    self._cache["lux"] = None
                    _log("veml7700 read err: {}".format(e))
            if self.scd41:
                try:
                    r = self.scd41.read()
                    if r:
                        self._cache["co2_ppm"] = r[0]
                except Exception as e:
                    _log("scd41 read err: {}".format(e))
            if self.sgp40:
                try:
                    self._cache["voc_idx"] = self.sgp40.read_index()
                except Exception as e:
                    self._cache["voc_idx"] = None
                    _log("sgp40 read err: {}".format(e))

        # Merge cached slow-sensor values into every packet.
        for k, v in self._cache.items():
            pkt[k] = v

        return pkt


class CommandHandler:
    """Line-buffered command reader on USB-CDC stdin.  Non-blocking."""

    def __init__(self, hub):
        self.hub = hub
        self.buf = b""
        self.poller = select.poll()
        self.poller.register(sys.stdin, select.POLLIN)

    def poll(self):
        events = self.poller.poll(0)
        if not events:
            return
        try:
            chunk = sys.stdin.buffer.read(64)
        except Exception:
            return
        if not chunk:
            return
        self.buf += chunk
        while b"\n" in self.buf:
            line, self.buf = self.buf.split(b"\n", 1)
            self._handle(line.strip())

    def _handle(self, line):
        if not line:
            return
        try:
            cmd = json.loads(line)
        except Exception as e:
            _log("bad cmd: {}".format(e))
            return
        action = cmd.get("cmd")
        if action == "ping":
            _log("pong v={}".format(cfg.FIRMWARE_VERSION))
        elif action == "tare" and self.hub.hx711:
            self.hub.hx711.tare(cfg.HX711_SAMPLES * 4)
            _log("tare set to {}".format(self.hub.hx711.tare_offset))
        elif action == "calibrate" and self.hub.hx711:
            self.hub.hx711.scale = float(cmd.get("cal", 1.0))
            _log("scale set to {}".format(self.hub.hx711.scale))
        else:
            _log("unknown cmd: {}".format(action))


def main():
    _log("beehive firmware {} starting".format(cfg.FIRMWARE_VERSION))
    hub = SensorHub()
    cmdr = CommandHandler(hub)

    next_publish = _now_ms()
    interval_ms = cfg.PUBLISH_INTERVAL_S * 1000

    while True:
        now = _now_ms()
        if time.ticks_diff(now, next_publish) >= 0:
            next_publish = time.ticks_add(next_publish, interval_ms)
            pkt = hub.read_all()
            # Compact JSON on one line.
            print(json.dumps(pkt))
            gc.collect()

        cmdr.poll()
        time.sleep_ms(10)


if __name__ == "__main__":
    main()
