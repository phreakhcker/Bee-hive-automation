# System Architecture

## Two-tier design

```
┌────────────────────────────────────────────────────────────┐
│                       Solar / Power                        │
│                                                            │
│   [100 W panel]──▶[Victron MPPT]──▶[BMS]──▶[3S4P pack]     │
│                                             │              │
│                                             ▼              │
│                                     [Pololu 12→5 V buck]   │
└─────────────────────────────────────────────┬──────────────┘
                                              │ 5 V
                                              ▼
    ┌────────────────────────────────────────────────────────┐
    │                     Raspberry Pi 5                     │
    │                                                        │
    │   ┌──────────────┐  CSI  ┌────────────────────────┐   │
    │   │ Camera Mod 3 │◀─────▶│ camera_entrance.py     │   │
    │   │  (entrance)  │       │  (pollen inference)    │   │
    │   └──────────────┘       └───────────┬────────────┘   │
    │                                      │                 │
    │   ┌──────────────┐  CSI  ┌───────────▼────────────┐   │
    │   │ Cam 3 NoIR   │◀─────▶│ camera_inside.py       │   │
    │   │ (in-hive)    │       │  (timelapse recorder)  │   │
    │   └──────────────┘       └───────────┬────────────┘   │
    │                                      │                 │
    │   ┌──────────────┐  I²S  ┌───────────▼────────────┐   │
    │   │ SPH0645 mic  │◀─────▶│ audio_service.py       │   │
    │   └──────────────┘       │  (FFT, queen detector) │   │
    │                          └───────────┬────────────┘   │
    │                                      │                 │
    │   ┌──────────────┐  UART ┌───────────▼────────────┐   │
    │   │ Hydreon RG-9 │◀─────▶│ rain_service.py        │   │
    │   └──────────────┘       └───────────┬────────────┘   │
    │                                      │                 │
    │   ┌──────────────────────────────────▼──────────────┐  │
    │   │              sensor_ingest.py                   │  │
    │   │  reads JSON from Pico USB-CDC, normalises,      │  │
    │   │  writes to SQLite; broadcasts on internal bus   │  │
    │   └──────────────────────────────────┬──────────────┘  │
    │                                      │                 │
    │   ┌──────────────────────────────────▼──────────────┐  │
    │   │           dashboard/app.py (Flask)              │  │
    │   │  /api/latest, /api/history, / (SPA)             │  │
    │   └─────────────────────────────────────────────────┘  │
    └─────────────────────▲──────────────────────────────────┘
                          │ USB-CDC (JSON packets)
                          │
    ┌─────────────────────┴──────────────────────────────────┐
    │                    Raspberry Pi Pico 2                 │
    │                                                        │
    │  main.py — orchestrator, 1 Hz publish loop             │
    │                                                        │
    │  drivers/                                              │
    │    hx711.py           ─── HX711 (load cells)           │
    │    ds18b20.py         ─── DS18B20 array (1-Wire)       │
    │    sht4x.py           ─── SHT41 (I²C0)                 │
    │    bme280.py          ─── BME280 (I²C0)                │
    │    veml7700.py        ─── VEML7700 (I²C1)              │
    │    scd41.py           ─── SCD41 (I²C1)                 │
    │    sgp40.py           ─── SGP40 (I²C1)                 │
    │    battery_monitor.py ─── ADC voltage divider          │
    │    bee_gate.py        ─── PIO-based IR-beam gate       │
    └────────────────────────────────────────────────────────┘
```

## Why two boards?

The Pico does one thing well: read sensors on a strict, predictable schedule and count IR-gate events without missing any. It runs a single MicroPython script, has no OS, no filesystem to corrupt, and boots in ~200 ms. If it wedges (rare), the Pi power-cycles it via a GPIO line.

The Pi does everything that needs storage, ML, or a network. It runs Debian, has an SD card that *will* eventually corrupt if power is yanked, but its systemd services restart on crash, and the sensor pipeline stays lossless because the Pico buffers packets during outages.

## Data flow

1. **Pico** samples each sensor on its natural cadence (weight: 1 Hz; DS18B20: 0.2 Hz; BME280: 1 Hz; IR gate: interrupt-driven, aggregated at 1 Hz; SCD41: 0.2 Hz).
2. Once per second, Pico emits a JSON packet on USB-CDC:
   ```json
   {"t": 1721830000, "w_kg": 42.31, "t_in": [34.1, 35.2, 34.8, 33.9],
    "rh_in": 62.4, "t_out": 24.1, "rh_out": 55.0, "p_hpa": 1012.3,
    "lux": 14300, "co2_ppm": 780, "voc_idx": 145,
    "bees_in": 12, "bees_out": 8, "v_pack": 12.14}
   ```
3. **Pi `sensor_ingest.py`** reads the serial stream, validates the JSON, inserts a row into SQLite (`data/hive.db`, table `readings`), and publishes to an in-process pub/sub queue.
4. **Camera services** capture on their own schedule (entrance: continuous 15 fps, ring-buffered; inside: timelapse every 10 min + on-demand). Frames are annotated with sensor context from the pub/sub bus.
5. **Dashboard** serves the latest snapshot + historical charts (7 d / 30 d / all).
6. **Shutdown guard** monitors `v_pack`; below 10.8 V it initiates `sudo shutdown -h now`. Hard cutoff at 9.9 V via BMS UVP.

## Serial protocol

- **Physical:** Pi USB → Pico USB (USB-CDC / `/dev/ttyACM0`)
- **Baud:** N/A (USB-CDC), effectively line-rate.
- **Framing:** newline-delimited JSON. One packet per line.
- **Direction:** primarily Pico → Pi. Pi → Pico is reserved for commands: `{"cmd":"tare"}` (reset weight zero), `{"cmd":"calibrate","cal":428.5}` (set HX711 scale factor), `{"cmd":"ping"}`.
- **Loss handling:** Pico buffers up to 60 s of packets in RAM if USB is disconnected; older packets are dropped.

## Storage

- **SQLite** at `/var/lib/beehive/hive.db` — one row per second, ~86,400/day, ~30 MB/month. Cheap to keep years.
- Optional **InfluxDB + Grafana** for prettier charts — see `docs/optional-influx.md` (not included initially).
- **Camera captures** land in `/var/lib/beehive/captures/YYYY/MM/DD/`. Configurable retention (default: 7 days full, 30 days downsampled).

## Failure modes & recoveries

| Failure | Detection | Recovery |
|---|---|---|
| Pico crashes | `sensor_ingest.py` no packet > 30 s | Pi drives Pico RUN pin low for 200 ms (via GPIO) |
| USB comms bad | Framing / JSON parse errors > 10/min | Log + Pi USB power-cycle via `uhubctl` |
| Pi loses power (dirty) | Boot detects SQLite journal | SQLite WAL replays; last <1 s of data may be lost |
| Salvaged cell fails | Daly BMS trips → pack disconnects | Systemd cleans up; on next boot, dashboard shows outage |
| Sensor detached | Reading is NaN or driver exception | Driver returns `null`; ingest records null; dashboard shows gap |
| Full disk | Camera write fails | Retention job runs early; older captures deleted first |
