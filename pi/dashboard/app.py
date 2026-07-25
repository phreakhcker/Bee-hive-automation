"""Beehive dashboard — a small Flask app.

- `/`            — SPA that draws recent sensor charts via Chart.js
- `/api/latest`  — most recent single row from every table
- `/api/history` — ?hours=24 -> series
- `/api/tare`    — POST -> issue tare cmd to Pico (via /tmp/pico.cmd fifo)
- `/api/calibrate` — POST scale factor
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import load_config, open_db, setup_logging   # noqa: E402


log = setup_logging("dashboard")
app = Flask(__name__)
CONFIG = None
DB = None
COMMAND_FIFO = "/tmp/beehive.pico.cmd"


def _init(config_path=None):
    global CONFIG, DB
    CONFIG = load_config(config_path)
    DB = open_db(CONFIG["paths"]["db_path"])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/latest")
def latest():
    r = DB.execute(
        "SELECT ts, w_kg, t_in, rh_in, t_out, rh_out, p_hpa, lux, "
        "co2_ppm, voc_raw, bees_in, bees_out, v_pack FROM readings "
        "ORDER BY ts DESC LIMIT 1"
    ).fetchone()
    if not r:
        return jsonify({})
    cols = ["ts", "w_kg", "t_in", "rh_in", "t_out", "rh_out", "p_hpa",
            "lux", "co2_ppm", "voc_raw", "bees_in", "bees_out", "v_pack"]
    result = dict(zip(cols, r))
    # Probes for the same timestamp
    probes = DB.execute(
        "SELECT label, t_c FROM probes WHERE ts = ?", (result["ts"],)
    ).fetchall()
    result["t_probes"] = {label: t for label, t in probes}
    return jsonify(result)


@app.route("/api/history")
def history():
    hours = int(request.args.get("hours", CONFIG["dashboard"]["history_default_hours"]))
    since = int(time.time()) - hours * 3600
    rows = DB.execute(
        "SELECT ts, w_kg, t_in, rh_in, t_out, rh_out, p_hpa, lux, "
        "co2_ppm, bees_in, bees_out, v_pack FROM readings "
        "WHERE ts >= ? ORDER BY ts",
        (since,),
    ).fetchall()
    cols = ["ts", "w_kg", "t_in", "rh_in", "t_out", "rh_out", "p_hpa",
            "lux", "co2_ppm", "bees_in", "bees_out", "v_pack"]
    return jsonify([dict(zip(cols, r)) for r in rows])


def _write_command(obj):
    # Ingest is expected to open a named FIFO and forward commands to Pico.
    if not os.path.exists(COMMAND_FIFO):
        os.mkfifo(COMMAND_FIFO)
    # Non-blocking write in a thread to avoid hanging if reader isn't ready.
    import threading
    def w():
        try:
            with open(COMMAND_FIFO, "w") as f:
                f.write(json.dumps(obj) + "\n")
        except Exception as e:
            log.warning("fifo write failed: %s", e)
    threading.Thread(target=w, daemon=True).start()


@app.route("/api/tare", methods=["POST"])
def tare():
    _write_command({"cmd": "tare"})
    return jsonify({"ok": True})


@app.route("/api/calibrate", methods=["POST"])
def calibrate():
    data = request.get_json(force=True)
    cal = float(data.get("cal"))
    _write_command({"cmd": "calibrate", "cal": cal})
    return jsonify({"ok": True, "cal": cal})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    _init(args.config)
    d = CONFIG["dashboard"]
    log.info("serving on http://%s:%s/", d["host"], d["port"])
    app.run(host=d["host"], port=d["port"])


if __name__ == "__main__":
    main()
