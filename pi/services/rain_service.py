"""Hydreon RG-9 rain sensor reader.

The RG-9 speaks a simple ASCII protocol on serial: it emits `R <mm/hr>` lines
in "polled" or "continuous" mode.  Default config here uses continuous mode
which sends a line whenever intensity changes.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import serial

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import load_config, open_db, setup_logging   # noqa: E402


log = setup_logging("rain")


def run(cfg: dict) -> None:
    r = cfg["rain"]
    if not r.get("enabled", True):
        log.info("rain disabled")
        return

    db = open_db(cfg["paths"]["db_path"])
    port = r["serial_port"]
    log.info("opening %s", port)
    ser = serial.Serial(port, baudrate=9600, timeout=2)

    # Put RG-9 into continuous mode + metric.  Reset & configure:
    ser.write(b"K\n")   # reset accumulator
    ser.write(b"M\n")   # metric mm/hr
    ser.write(b"P\n")   # continuous output

    accum = 0.0
    last_ts = time.time()

    while True:
        line = ser.readline().decode("ascii", errors="replace").strip()
        if not line:
            continue
        # Expected: "R nnn.nnn" (mm/hr)
        if not line.startswith("R "):
            log.debug("rg9: %s", line)
            continue
        try:
            intensity = float(line.split()[1])
        except (IndexError, ValueError):
            continue

        now = time.time()
        dt_h = (now - last_ts) / 3600.0
        accum += intensity * dt_h
        last_ts = now

        db.execute(
            "INSERT OR REPLACE INTO rain(ts, intensity, accum_mm) VALUES (?,?,?)",
            (int(now), intensity, round(accum, 3)),
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    run(cfg)


if __name__ == "__main__":
    main()
