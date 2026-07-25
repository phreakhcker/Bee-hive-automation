"""Entrance camera capture service.

Records continuously into a rolling ring buffer.  On motion (or on demand),
saves a clip.  Also periodically runs the (optional) pollen classifier on
sampled frames when a model is present at pi/models/pollen.onnx.
"""

from __future__ import annotations

import argparse
import collections
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import load_config, open_db, setup_logging   # noqa: E402


log = setup_logging("cam_entrance")


def _import_camera():
    try:
        from picamera2 import Picamera2
        return Picamera2
    except Exception as e:
        log.error("picamera2 unavailable: %s -- install with apt install python3-picamera2", e)
        return None


def _load_pollen_model():
    """Optional — returns callable(frame_bgr) -> dict or None if unavailable."""
    model_path = Path("pi/models/pollen.onnx")
    if not model_path.exists():
        log.info("no pollen model at %s; skipping classifier", model_path)
        return None
    try:
        import onnxruntime as ort
    except Exception:
        log.warning("onnxruntime not installed; skipping classifier")
        return None
    sess = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    input_name = sess.get_inputs()[0].name
    log.info("pollen model loaded: %s", model_path)

    def infer(frame_bgr):
        # Placeholder pipeline; real model needs proper preprocessing.
        import numpy as np
        img = frame_bgr[..., ::-1].astype("float32") / 255.0
        img = np.expand_dims(img.transpose(2, 0, 1), 0)
        out = sess.run(None, {input_name: img})
        return {"with_pollen": int(out[0].argmax() == 1)}

    return infer


def run(cfg: dict) -> None:
    cam_cfg = cfg["cameras"]["entrance"]
    if not cam_cfg.get("enabled", True):
        log.info("entrance camera disabled in config")
        return

    Picamera2 = _import_camera()
    if not Picamera2 is None:
        picam = Picamera2(cam_cfg["camera_index"])
        vid_cfg = picam.create_video_configuration(
            main={"size": tuple(cam_cfg["resolution"]), "format": "RGB888"},
            controls={"FrameRate": cam_cfg["fps"]},
        )
        picam.configure(vid_cfg)
        picam.start()
        log.info("entrance camera started at %s @ %s fps",
                 cam_cfg["resolution"], cam_cfg["fps"])
    else:
        log.error("cannot start camera; exiting")
        return

    ring_len = cam_cfg["ring_buffer_seconds"] * cam_cfg["fps"]
    ring = collections.deque(maxlen=ring_len)

    db = open_db(cfg["paths"]["db_path"])
    infer = _load_pollen_model()
    captures_root = Path(cfg["paths"]["captures_dir"]) / "entrance"
    captures_root.mkdir(parents=True, exist_ok=True)

    frame_i = 0
    infer_every = max(1, cam_cfg["fps"] // 2)   # ~2 Hz classifier max

    try:
        while True:
            frame = picam.capture_array()
            ring.append((time.time(), frame))
            frame_i += 1

            # Sample the classifier occasionally
            if infer and (frame_i % infer_every == 0):
                try:
                    result = infer(frame)
                except Exception as e:
                    log.warning("classifier failed: %s", e)
                    continue
                if result.get("with_pollen"):
                    day_dir = captures_root / datetime.now().strftime("%Y/%m/%d")
                    day_dir.mkdir(parents=True, exist_ok=True)
                    path = day_dir / f"{int(time.time())}_pollen.jpg"
                    _save_frame(frame, path)
                    db.execute(
                        "INSERT OR REPLACE INTO pollen_events(ts, bee_count, "
                        "with_pollen, frame_path) VALUES (?,?,?,?)",
                        (int(time.time()), 1, 1, str(path)),
                    )
    except KeyboardInterrupt:
        log.info("shutting down")
    finally:
        picam.stop()


def _save_frame(frame, path: Path) -> None:
    try:
        from PIL import Image
    except Exception:
        log.warning("Pillow missing; can't save frame")
        return
    Image.fromarray(frame).save(path, quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    run(cfg)


if __name__ == "__main__":
    main()
