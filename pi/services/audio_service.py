"""I2S microphone capture + spectral analysis for beehive audio.

Reads N-second chunks from the ALSA I2S device, runs an FFT, and computes
band energy for the queenless (~225-250 Hz) and pre-swarm (~400-800 Hz)
ranges.  Elevated queenless-band energy over hours is a queenlessness signal.

Emits an event row per chunk.  Actual queenlessness detection (persistent
elevation over some threshold across hours) is left to a downstream job.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import load_config, open_db, setup_logging   # noqa: E402


log = setup_logging("audio")


def _band_energy(spec_mag, freqs, lo_hz, hi_hz):
    import numpy as np
    mask = (freqs >= lo_hz) & (freqs <= hi_hz)
    if not mask.any():
        return 0.0
    return float(np.mean(spec_mag[mask] ** 2))


def run(cfg: dict) -> None:
    a = cfg["audio"]
    if not a.get("enabled", True):
        log.info("audio disabled")
        return

    try:
        import numpy as np
        import sounddevice as sd
    except Exception as e:
        log.error("audio deps missing: %s", e)
        return

    db = open_db(cfg["paths"]["db_path"])
    sr = a["sample_rate"]
    chunk_s = a["chunk_seconds"]
    chunk_n = sr * chunk_s
    ql_lo, ql_hi = a["fft_bins_of_interest"]["queenless_hz"]
    sw_lo, sw_hi = a["fft_bins_of_interest"]["swarm_hz"]

    log.info("audio: sr=%s device=%s", sr, a["device"])

    while True:
        try:
            rec = sd.rec(chunk_n, samplerate=sr, channels=1, dtype="float32",
                         device=a["device"])
            sd.wait()
        except Exception as e:
            log.error("capture failed: %s -- retrying in 5s", e)
            time.sleep(5)
            continue

        x = rec[:, 0]
        # DC + LF rumble removal
        x = x - x.mean()
        # FFT
        w = np.hanning(len(x))
        spec = np.fft.rfft(x * w)
        mag = np.abs(spec) / len(x)
        freqs = np.fft.rfftfreq(len(x), 1.0 / sr)

        ql_e = _band_energy(mag, freqs, ql_lo, ql_hi)
        sw_e = _band_energy(mag, freqs, sw_lo, sw_hi)
        buzz = float(np.sqrt((x ** 2).mean()))

        ts = int(time.time())
        db.execute("INSERT OR REPLACE INTO audio_events(ts, kind, value) "
                   "VALUES(?, ?, ?)", (ts, "queenless_band", ql_e))
        db.execute("INSERT OR REPLACE INTO audio_events(ts + 1, kind, value) "
                   "VALUES(?, ?, ?)", (ts + 1, "swarm_band", sw_e))
        db.execute("INSERT OR REPLACE INTO audio_events(ts + 2, kind, value) "
                   "VALUES(?, ?, ?)", (ts + 2, "buzz_level", buzz))
        log.info("audio chunk: buzz=%.4f ql=%.6f sw=%.6f", buzz, ql_e, sw_e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    run(cfg)


if __name__ == "__main__":
    main()
