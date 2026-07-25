"""Shared helpers: config loading, SQLite schema, logging."""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path

import yaml


DEFAULT_CONFIG_PATHS = [
    Path("config/config.yaml"),
    Path("/etc/beehive/config.yaml"),
]


def load_config(path: str | os.PathLike | None = None) -> dict:
    if path:
        candidates = [Path(path)]
    else:
        candidates = DEFAULT_CONFIG_PATHS
    for p in candidates:
        if p.exists():
            with p.open("r") as f:
                return yaml.safe_load(f)
    raise FileNotFoundError(
        f"No config found. Tried: {[str(p) for p in candidates]}. "
        f"Copy config/config.example.yaml to config/config.yaml first."
    )


SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    ts        INTEGER PRIMARY KEY,   -- unix seconds
    w_kg      REAL,
    t_in      REAL,
    rh_in     REAL,
    t_out     REAL,
    rh_out    REAL,
    p_hpa     REAL,
    lux       REAL,
    co2_ppm   INTEGER,
    voc_raw   INTEGER,
    bees_in   INTEGER,
    bees_out  INTEGER,
    v_pack    REAL,
    raw_json  TEXT              -- full packet for future re-processing
);

CREATE TABLE IF NOT EXISTS probes (
    ts        INTEGER,
    label     TEXT,
    t_c       REAL,
    PRIMARY KEY (ts, label)
);

CREATE TABLE IF NOT EXISTS rain (
    ts        INTEGER PRIMARY KEY,
    intensity REAL,      -- mm/hr
    accum_mm  REAL
);

CREATE TABLE IF NOT EXISTS audio_events (
    ts        INTEGER PRIMARY KEY,
    kind      TEXT,      -- "queenless" | "swarm" | "buzz_level"
    value     REAL
);

CREATE TABLE IF NOT EXISTS pollen_events (
    ts        INTEGER PRIMARY KEY,
    bee_count INTEGER,
    with_pollen INTEGER,
    frame_path TEXT
);

CREATE INDEX IF NOT EXISTS idx_readings_ts ON readings(ts);
CREATE INDEX IF NOT EXISTS idx_probes_ts ON probes(ts);
"""


def open_db(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.executescript(SCHEMA)
    return conn


def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
    )
    return logging.getLogger(name)
