"""Read newline-JSON packets from the Pico over USB-CDC and store them.

Also handles Pico liveness — if no packet arrives for `packet_timeout_s`,
we pulse the reset GPIO to reboot the Pico.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import serial

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import load_config, open_db, setup_logging   # noqa: E402


log = setup_logging("ingest")


def _try_import_gpio():
    """Optional — only needed if we're going to reset the Pico via GPIO."""
    try:
        from gpiozero import DigitalOutputDevice
        return DigitalOutputDevice
    except Exception as e:
        log.warning("gpiozero not available (%s); Pico reset disabled", e)
        return None


def reset_pico(reset_pin):
    if not reset_pin:
        return
    log.warning("Resetting Pico via GPIO")
    reset_pin.on()
    time.sleep(0.2)
    reset_pin.off()


def store_packet(conn, packet: dict, raw: str) -> None:
    ts = int(packet.get("t") or time.time())
    conn.execute(
        """INSERT OR REPLACE INTO readings
           (ts, w_kg, t_in, rh_in, t_out, rh_out, p_hpa, lux, co2_ppm,
            voc_raw, bees_in, bees_out, v_pack, raw_json)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            ts,
            packet.get("w_kg"),
            packet.get("t_in"),
            packet.get("rh_in"),
            packet.get("t_out"),
            packet.get("rh_out"),
            packet.get("p_hpa"),
            packet.get("lux"),
            packet.get("co2_ppm"),
            packet.get("voc_idx"),
            packet.get("bees_in"),
            packet.get("bees_out"),
            packet.get("v_pack"),
            raw,
        ),
    )
    for label, t_c in (packet.get("t_probes") or {}).items():
        conn.execute(
            "INSERT OR REPLACE INTO probes(ts, label, t_c) VALUES (?,?,?)",
            (ts, label, t_c),
        )


def run(cfg: dict, debug: bool = False) -> None:
    db = open_db(cfg["paths"]["db_path"])
    port = cfg["pico"]["serial_port"]
    timeout = cfg["pico"]["packet_timeout_s"]
    reset_gpio_num = cfg["pico"].get("reset_gpio")

    DigitalOutputDevice = _try_import_gpio()
    reset_pin = (DigitalOutputDevice(reset_gpio_num)
                 if DigitalOutputDevice and reset_gpio_num else None)

    log.info("Opening %s at %s baud (USB-CDC ignores baud)", port, 115200)
    ser = serial.Serial(port, baudrate=115200, timeout=1)
    ser.reset_input_buffer()

    last_packet = time.time()

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="replace").strip()
        except serial.SerialException as e:
            log.error("serial error: %s -- reopening in 2s", e)
            time.sleep(2)
            try:
                ser.close()
            except Exception:
                pass
            ser = serial.Serial(port, baudrate=115200, timeout=1)
            continue

        if not line:
            if time.time() - last_packet > timeout:
                log.error("no packets for %ss", timeout)
                reset_pico(reset_pin)
                last_packet = time.time() + 5   # give Pico time to recover
            continue

        if line.startswith("#"):
            if debug:
                log.debug("pico: %s", line)
            continue

        try:
            packet = json.loads(line)
        except json.JSONDecodeError:
            log.warning("bad JSON: %r", line[:120])
            continue

        try:
            store_packet(db, packet, line)
            last_packet = time.time()
            if debug:
                log.info("stored %s", packet)
        except Exception as e:
            log.exception("store failed: %s", e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.config)
    run(cfg, debug=args.debug)


if __name__ == "__main__":
    main()
