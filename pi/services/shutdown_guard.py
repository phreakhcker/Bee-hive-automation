"""Low-battery graceful shutdown.

Polls the most recent `v_pack` reading from SQLite.  Below the configured
threshold, initiates a clean shutdown so the SD card isn't corrupted when
the BMS eventually opens the P- FET at ~9.0 V.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import load_config, open_db, setup_logging   # noqa: E402


log = setup_logging("shutdown_guard")


def latest_v_pack(db) -> float | None:
    row = db.execute(
        "SELECT v_pack FROM readings ORDER BY ts DESC LIMIT 1"
    ).fetchone()
    if not row or row[0] is None:
        return None
    return float(row[0])


def run(cfg: dict, dry_run: bool = False) -> None:
    db = open_db(cfg["paths"]["db_path"])
    warn = cfg["battery"]["low_warn_v"]
    shut = cfg["battery"]["low_shutdown_v"]

    # Require N consecutive low readings before acting -- protects against
    # a single noisy sample.
    low_streak = 0
    STREAK_REQUIRED = 10   # 10 samples at 1 Hz = 10 s

    while True:
        v = latest_v_pack(db)
        if v is None:
            time.sleep(5)
            continue

        if v <= shut:
            low_streak += 1
            log.warning("v_pack=%.2f below shutdown threshold %.2f (streak %d/%d)",
                        v, shut, low_streak, STREAK_REQUIRED)
            if low_streak >= STREAK_REQUIRED:
                log.error("initiating shutdown")
                if not dry_run:
                    subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)
                return
        elif v <= warn:
            low_streak = 0
            log.info("v_pack=%.2f (warn threshold %.2f)", v, warn)
        else:
            low_streak = 0

        time.sleep(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = load_config(args.config)
    run(cfg, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
