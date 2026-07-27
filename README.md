# Bee Hive Automation

An open, off-grid monitoring & automation system for a Langstroth beehive, built around a Raspberry Pi 5 and a Raspberry Pi Pico. Powered by salvaged 18650 cells (from disposable vapes) with a smart BMS and solar charging.

> **Safety note up front:** this project handles Li-ion cells outdoors and off-grid. Read [`docs/safety.md`](docs/safety.md) before you assemble the power system. Salvaged vape cells are viable but non-trivial — they must be individually tested, matched, and monitored.

---

## What it measures

| Metric | Sensor | Where |
|---|---|---|
| Hive weight | 4× 50 kg load cells → HX711 | Under the hive stand |
| Internal temp (multi-point) | 4× DS18B20 waterproof probes | Top cover, above brood, brood side, entrance |
| Internal humidity & temp | Sensirion SHT41 (or SHT31-DIS-F w/ PTFE membrane) | Inside, near brood |
| External weather (T/RH/Pressure) | Bosch BME280 | In a radiation shield, ~1 m from hive |
| Hive audio | SPH0645LM4H I²S MEMS mic | Inside, top of hive |
| Entrance activity (in/out count, direction) | 8× paired ITR9606 slotted opto sensors | Custom bee-gate replacing entrance reducer |
| Returning pollen loads | Pi Camera Module 3 (autofocus) + CV | Downward, over landing board |
| Inside-hive view | Pi Camera Module 3 NoIR + 850 nm IR strip | Recessed behind acrylic |
| Ambient light | VEML7700 | At entrance |
| Rain | Hydreon RG-9 optical | On post above hive |
| Optional: CO₂ | Sensirion SCD41 (I²C, NDIR) | Inside hive |
| Optional: VOC | Sensirion SGP40 | Inside hive |
| Pack voltage & battery temp | Voltage divider → Pico ADC, 10 k NTC → MPPT | Battery box |

## Architecture

```
   ┌──────────────┐    UART/USB-CDC     ┌──────────────┐
   │   Pi Pico    │◀───JSON packets────▶│   Pi 5 (4)   │
   │ (real-time   │  every 1–10 s       │  (compute,   │
   │  sensor      │                     │   ML, store, │
   │  aggregator) │                     │   dashboard) │
   └───────┬──────┘                     └──────┬───────┘
           │                                    │
   ┌───────┴────────────────────────┐    ┌──────┴────────────┐
   │ HX711, DS18B20, SHT41, BME280, │    │ Pi Cam 3 (entrance│
   │ ITR9606 IR gate, VEML7700,     │    │ pollen), Pi Cam 3 │
   │ SCD41, SGP40, pack V           │    │ NoIR (in-hive),   │
   └────────────────────────────────┘    │ SPH0645 I²S mic,  │
                                          │ Hydreon RG-9 UART │
                                          └───────────────────┘
```

**Why split the workload:** the Pico handles anything that needs deterministic timing (HX711's bit-banged protocol, IR-gate interrupts at bee-crossing speed, environmental polling). The Pi handles anything that needs storage, ML, or a network (camera, audio, dashboards, alerts).

Full details in [`docs/architecture.md`](docs/architecture.md).

## Power

| | |
|---|---|
| Cells | 12× matched salvaged 18650 (**3S4P**, ~11.1 V nominal) |
| BMS | Daly 3S 20 A smart BMS (Bluetooth telemetry) |
| Panel | Renogy 100 W 12 V monocrystalline |
| Charge controller | Victron SmartSolar MPPT 75/15 (Li-ion profile, absorption capped at **12.30 V = 4.10 V/cell** for cycle life) |
| Buck | Pololu D36V50F5 → 5 V @ 5 A → Pi 5 |
| Protection | ANL 15 A pack fuse, ATO 10 A load fuse, 10 k NTC on battery temp → charger disable below 0 °C |

Full BOM in [`hardware/BOM.md`](hardware/BOM.md); power system detail in [`docs/power-system.md`](docs/power-system.md); wiring in [`diagrams/`](diagrams/).

## Repository layout

```
.
├── README.md                     ← you are here
├── LICENSE
├── docs/
│   ├── architecture.md           system-level design & data flow
│   ├── hardware.md               Pico pinouts, sensor wiring
│   ├── power-system.md           solar/battery/BMS detail
│   ├── assembly.md               step-by-step build guide
│   └── safety.md                 Li-ion & outdoor-electrical safety
├── hardware/
│   └── BOM.md                    complete parts list w/ prices & sources
├── diagrams/                     SVG wiring diagrams (open in browser)
│   ├── system-overview.svg
│   ├── pico-wiring.svg
│   ├── power-system.svg
│   └── bee-gate.svg
├── firmware/pico/                MicroPython firmware for Pico
│   ├── main.py                   entry point, main loop, packet emitter
│   ├── config.py                 pin assignments, calibration constants
│   └── drivers/                  one module per sensor
│       ├── hx711.py
│       ├── ds18b20.py
│       ├── sht4x.py
│       ├── bme280.py
│       ├── veml7700.py
│       ├── scd41.py
│       ├── sgp40.py
│       ├── bee_gate.py           PIO-driven IR gate counter
│       └── battery_monitor.py
├── pi/
│   ├── requirements.txt
│   ├── services/
│   │   ├── sensor_ingest.py      reads Pico JSON, writes SQLite
│   │   ├── camera_entrance.py    entrance camera capture + optional pollen inference
│   │   ├── camera_inside.py      in-hive camera capture (timelapse + on-demand)
│   │   ├── audio_service.py      I²S mic capture, FFT, queenlessness detector
│   │   ├── rain_service.py       Hydreon RG-9 UART reader
│   │   └── shutdown_guard.py     graceful shutdown on low pack voltage
│   ├── dashboard/
│   │   ├── app.py                Flask dashboard, /api endpoints, / SPA
│   │   └── templates/index.html
│   └── models/                   place trained pollen/audio models here
├── config/
│   └── config.example.yaml       copy to config.yaml and edit
├── scripts/
│   ├── setup_pi.sh               provisions a fresh Pi OS install
│   ├── flash_pico.md             MicroPython flashing instructions
│   └── systemd/                  unit files for each Pi service
└── tests/                        smoke tests & sensor sanity checks
```

## Quick start

1. **Read the safety doc.** [`docs/safety.md`](docs/safety.md).
2. **Build & test the power system first, on a bench, for two weeks.** [`docs/power-system.md`](docs/power-system.md).
3. **Order the BOM.** [`hardware/BOM.md`](hardware/BOM.md).
4. **Flash the Pico** with MicroPython, then copy `firmware/pico/` to it. [`scripts/flash_pico.md`](scripts/flash_pico.md).
5. **Provision the Pi**: `bash scripts/setup_pi.sh` on a fresh Pi OS install.
6. **Wire per the diagrams**: [`diagrams/`](diagrams/).
7. **Deploy** — install systemd units from `scripts/systemd/`, plug the Pico into the Pi's USB, and browse to `http://<pi>:8080/`.

## Development roadmap

- **Phase 1** (this repo): sensor acquisition, weight/T/RH/gate logging, cameras record raw video, dashboard.
- **Phase 2**: pollen classifier (train on collected entrance footage), audio queenlessness alerts, MQTT/HTTP alerting.
- **Phase 3**: pollen-source colour matching, hive-strength trend model, multi-hive apiary aggregation.

## License

MIT — see [`LICENSE`](LICENSE). Do what you like, no warranty, don't blame me if a salvaged cell vents in your face.

## Prior art & references

We audited the beehive-monitoring landscape before starting; the licensing picture matters because a commercial kit build is planned (see [`docs/dataset-permissions.md`](docs/dataset-permissions.md) for outreach in progress).

### Cleared to build on

| Project | License | Use |
|---|---|---|
| [BeeCam-AprilTag (Zenodo 13227905)](https://zenodo.org/records/13227905) | CC-BY-4.0 | Pi-side imaging pipeline reference — commercial OK with attribution |
| [Ratnayake Polytrack2.0](https://github.com/malikaratnayake/Polytrack2.0) | MIT | Pollinator tracking code — permissive, safe to fork |

### Reference only — NOT bundled (license blocks it)

| Project | License | Why not |
|---|---|---|
| [Hiveeyes (kotori, terkin)](https://github.com/hiveeyes) | AGPL-3.0 | Network-triggered copyleft — would force our whole stack open |
| [HoneyPi](https://github.com/Honey-Pi) | CC-BY-NC-SA / NC-ND | Non-commercial only |
| [hydronics2 easy-bee-counter](https://github.com/hydronics2/2019-easy-bee-counter) | CERN-OHL v1.2 (HW) / no license (FW) | Firmware has no rights grant; hardware is copyleft |
| [Mjrovai/Bee-Counting](https://github.com/Mjrovai/Bee-Counting) | GPL-3.0 | Viral copyleft; useful only if we go fully OSS |
| Sensor selection informed by [OSBeehives](https://opensourcebeehives.org/), [HiveTool](https://hivetool.org/), [HiveEyes community](https://community.hiveeyes.org/) | — | Community docs — cited, no code reused |

### Datasets

| Dataset | License | Status |
|---|---|---|
| [Kaggle Honey Bee Pollen](https://www.kaggle.com/datasets/ivanfel/honey-bee-pollen) | CC-BY-SA-4.0 | R&D only — ShareAlike arguably viral on trained weights |
| [PollenBee (HUST)](https://comvis-hust.github.io/datasets/pollenbee.html) | Not stated | Permission requested — see [`docs/dataset-permissions.md`](docs/dataset-permissions.md) |
| [VnPollenBee (Nguyen et al. 2024)](https://www.sciencedirect.com/science/article/pii/S1574954124002863) | Not stated | Permission requested — same email |
| [Bee Detection + Direction Dataset (Mendeley 8gb9r2yhfc)](https://data.mendeley.com/datasets/8gb9r2yhfc/5) | CC-BY-NC-ND-4.0 | Benchmarking only, cannot train shipping model |

Long-term plan: collect our own labelled dataset from the prototype hive so the shipping pollen model has clean IP.
