"""Smoke tests — no hardware required.

Verify that:
- Config loads with sensible defaults.
- SQLite schema comes up clean.
- Sensor-ingest can parse a well-formed Pico packet.
"""

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from pi.common import open_db, load_config           # noqa: E402
from pi.services.sensor_ingest import store_packet   # noqa: E402


def test_config_example_loads():
    cfg = load_config(REPO / "config" / "config.example.yaml")
    assert cfg["paths"]["db_path"]
    assert cfg["dashboard"]["port"] == 8080
    assert cfg["battery"]["low_shutdown_v"] < cfg["battery"]["low_warn_v"]


def test_schema_and_insert():
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "hive.db"
        conn = open_db(str(db_path))
        packet = {
            "t": 1721830000, "w_kg": 42.31, "t_in": 34.1, "rh_in": 62.4,
            "t_out": 24.1, "rh_out": 55.0, "p_hpa": 1012.3, "lux": 14300,
            "co2_ppm": 780, "voc_idx": 25123,
            "bees_in": 12, "bees_out": 8, "v_pack": 12.14,
            "t_probes": {"top_cover": 34.2, "above_brood": 35.1},
        }
        store_packet(conn, packet, json.dumps(packet))
        row = conn.execute("SELECT w_kg, bees_in FROM readings").fetchone()
        assert row == (42.31, 12)
        probes = dict(conn.execute("SELECT label, t_c FROM probes").fetchall())
        assert probes == {"top_cover": 34.2, "above_brood": 35.1}


if __name__ == "__main__":
    test_config_example_loads()
    test_schema_and_insert()
    print("smoke tests passed")
