"""In-hive camera timelapse.

Captures a still every `timelapse_interval_s` and writes to date-organized
folders.  Optionally toggles an IR LED GPIO before each capture.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import load_config, setup_logging   # noqa: E402


log = setup_logging("cam_inside")


def run(cfg: dict) -> None:
    cam_cfg = cfg["cameras"]["inside"]
    if not cam_cfg.get("enabled", True):
        log.info("inside camera disabled")
        return

    try:
        from picamera2 import Picamera2
    except Exception as e:
        log.error("picamera2 unavailable: %s", e)
        return

    picam = Picamera2(cam_cfg["camera_index"])
    still_cfg = picam.create_still_configuration(
        main={"size": tuple(cam_cfg["resolution"])},
    )
    picam.configure(still_cfg)

    ir_gpio_num = cam_cfg.get("ir_led_gpio")
    ir_led = None
    if ir_gpio_num is not None:
        try:
            from gpiozero import DigitalOutputDevice
            ir_led = DigitalOutputDevice(ir_gpio_num, initial_value=False)
        except Exception as e:
            log.warning("gpio unavailable for IR LED: %s", e)

    captures_root = Path(cfg["paths"]["captures_dir"]) / "inside"
    captures_root.mkdir(parents=True, exist_ok=True)

    interval = cam_cfg["timelapse_interval_s"]
    log.info("timelapse every %ss", interval)

    try:
        while True:
            now = datetime.now()
            day_dir = captures_root / now.strftime("%Y/%m/%d")
            day_dir.mkdir(parents=True, exist_ok=True)
            fname = day_dir / (now.strftime("%H%M%S") + ".jpg")

            if ir_led:
                ir_led.on()
                time.sleep(0.2)   # let sensor auto-exposure adjust

            picam.start()
            try:
                picam.capture_file(str(fname))
            finally:
                picam.stop()

            if ir_led:
                ir_led.off()

            log.info("captured %s", fname)
            time.sleep(interval)
    except KeyboardInterrupt:
        log.info("shutting down")
        if ir_led:
            ir_led.off()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    run(cfg)


if __name__ == "__main__":
    main()
