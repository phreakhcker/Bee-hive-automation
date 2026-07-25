# Bill of Materials

All prices approximate (USD, late-2025 street prices). Sources listed are what I've found reliable — substitute equivalents freely.

## Compute

| Item | Part | Qty | ~Price | Source | Notes |
|---|---|---:|---:|---|---|
| Main compute | Raspberry Pi 5 (4 GB) | 1 | $60 | Official Pi vendors | Pi 4 works if you already have one, ~30% slower ML |
| Pi 5 PSU (bench only) | Official Pi 5 27 W USB-C PSU | 1 | $12 | Same | For initial bench setup; deployment uses solar |
| microSD | SanDisk High Endurance 64 GB | 1 | $12 | Amazon | Endurance grade matters for 24/7 logging |
| Sensor MCU | Raspberry Pi Pico 2 (or Pico W / Pico H) | 1 | $5–7 | Same | Pico 2 preferred — more RAM for PIO/SPI/I²C in parallel |
| Optional accelerator | Hailo-8L HAT (Pi 5 M.2 or PoE HAT variant) | 1 | $70 | Pi vendors | Only if you plan multiple ML streams simultaneously |

## Sensors

| Item | Part | Qty | ~Price | Source |
|---|---|---:|---:|---|
| Weight — load cells | 50 kg half-bridge bar load cell (kit of 4 + HX711) | 1 | $10 | Amazon "4x 50kg load cell HX711 kit" |
| Weight — shielded cable | CAT6 foiled twisted pair, ~2 m | 1 | $5 | Any electronics supplier — needed for HX711→Pico noise immunity |
| Internal temp probes | DS18B20 waterproof stainless probe, 1 m | 4 | $3–5 ea | Adafruit #381, Amazon multipacks |
| 1-Wire pull-up | 4.7 kΩ 1/4 W resistor | 1 | $0.05 | Any |
| Internal RH+T | Sensirion SHT41 breakout (Adafruit) **or** SHT31-DIS-F with PTFE membrane | 1 | $12–15 | Adafruit #5665 |
| External weather | Bosch BME280 breakout | 1 | $10 | Adafruit #2652 or SparkFun SEN-13676 |
| Weather shield | 3D-printable Stevenson-style radiation shield (files not included; search Thingiverse "Stevenson screen sensor") | 1 | print cost | — |
| Audio | Adafruit SPH0645LM4H I²S MEMS mic breakout | 1 | $7 | Adafruit #3421 |
| IR gate sensors | Everlight ITR9606 slotted optocoupler (5 mm gap) | 16 | $1 ea | Digikey / Mouser |
| IR gate resistors | 220 Ω × 16 (IR LED), 10 kΩ × 16 (phototransistor pull-up) | 32 | $0.05 ea | Any |
| I/O expander for IR gate (optional) | MCP23017 I²C GPIO expander breakout | 1 | $5 | Adafruit #732 — used only if Pico GPIO count runs short |
| Entrance camera | Raspberry Pi Camera Module 3 (Standard, autofocus) | 1 | $30 | Pi vendors |
| Entrance camera ribbon | 15-pin CSI to 22-pin CSI cable (Pi 5) | 1 | $5 | Pi vendors |
| Inside camera | Raspberry Pi Camera Module 3 NoIR | 1 | $35 | Pi vendors |
| Inside camera window | 3 mm acrylic disc, 25 mm dia (anti-glare optional) | 1 | $2 | Any |
| IR illumination | 850 nm IR LED strip, 5 m, 12 V | 0.5 m | $10 (for full reel) | Amazon "IR LED strip 850nm" |
| Ambient light | VEML7700 lux breakout | 1 | $5 | Adafruit #4162 |
| Rain (recommended) | Hydreon RG-9 optical rain sensor | 1 | $60 | Hydreon direct |
| USB-serial for RG-9 (if not using Pi UART) | FTDI FT232RL breakout | 1 | $8 | Amazon |
| CO₂ (optional) | Sensirion SCD41 breakout | 1 | $50 | Adafruit #5190 |
| VOC (optional) | Sensirion SGP40 breakout | 1 | $15 | Adafruit #4829 |

## Power system

| Item | Part | Qty | ~Price | Notes |
|---|---|---:|---:|---|
| Cell tester | Opus BT-C3100 V2.2 | 1 | $55 | 4-bay capacity + IR tester — non-negotiable for salvaged cells |
| 18650 salvaged cells | Cells from disposable vapes | 40–60 | free | You'll cull ~70% |
| 4-cell parallel 18650 holders w/ solder tabs | Keystone 1042 or similar | 3 | $3 ea | Safer for hobbyists than DIY spot-welding |
| Nickel strip (light) | 0.15 × 8 mm pure nickel, 1 m | 1 | $8 | For interconnects between parallel groups |
| BMS | Daly 3S 20 A smart BMS with Bluetooth | 1 | $28 | Bluetooth per-cell telemetry is worth the extra $10 |
| Solar panel | Renogy 100 W 12 V monocrystalline rigid | 1 | $80 | Oversized on purpose |
| Solar cable | 10 AWG MC4 pair, 3 m | 1 | $12 | |
| MPPT charge controller | Victron SmartSolar MPPT 75/15 | 1 | $110 | Configure Li-ion profile, absorption **12.30 V** |
| Buck to 5 V | Pololu D36V50F5 (5 V, 5 A, synchronous) | 1 | $30 | Or Mean Well DDR-15G-5 for DIN-rail builds |
| Main fuse | ANL 15 A + fuse holder | 1 | $10 | Between battery + and everything else — mandatory |
| Load fuse | ATO 10 A + inline holder | 1 | $5 | |
| Thermal fuse | SEFUSE SF77E (77 °C, one-shot) | 1 | $2 | Series with pack — cheap insurance |
| Battery-temp NTC | 10 kΩ NTC thermistor, potted | 1 | $3 | Wired to Victron's battery temperature sense |
| Wire | 14 AWG silicone stranded (red + black), 5 m ea | 2 | $10 | Silicone insulation for outdoor UV/heat resistance |
| Battery interconnect | 22 AWG silicone stranded, ~2 m | 1 | $5 | For BMS balance leads |

## Enclosures & assembly

| Item | Part | Qty | ~Price | Notes |
|---|---|---:|---:|---|
| Electronics box | Bud Industries NBF-32026 IP66 polycarbonate, ~200 × 150 × 100 mm | 1 | $35 | UV-stable, screw lid |
| Battery box (separate) | Vented ammo-can-style, ~200 × 120 × 80 mm | 1 | $25 | Do NOT put batteries in the same box as electronics |
| Intumescent liner | Ceramic fiber blanket, 300 × 300 × 6 mm | 1 | $10 | Line battery box; buys minutes if a cell vents |
| Cable glands | PG9 + PG13 assortment | 6 | $8 | |
| DIN rail (optional) | 35 mm × 200 mm | 1 | $5 | Tidier internal layout |
| Solar panel mount | Adjustable pole mount for 100 W panel | 1 | $30 | |
| Bee-gate body | 3D-printed ASA or PETG (STL not included yet — see [docs/hardware.md](../docs/hardware.md)) | 1 | print cost | Do NOT use PLA — summer sun deforms it |
| Sensor wiring in hive | 22 AWG silicone-jacketed (not PVC — propolis attacks PVC) | 5 m | $8 | |
| Conformal coating | MG Chemicals 419D acrylic | 1 | $15 | Coat every PCB going into/near the hive; MASK sensor apertures |
| Desiccant | Silica gel packs (indicating) | 4 | $5 | Inside every enclosure and the hive-side sensor pod |

## Tools (if you don't already have)

| Tool | Rough $ | Notes |
|---|---:|---|
| Multimeter | $30 | Any decent auto-ranging |
| Soldering iron w/ temp control | $50 | TS100 / Pinecil |
| Wire strippers, side cutters | $20 | |
| Heatshrink assortment | $10 | |
| Crimp tool + JST-XH/PH kit | $25 | For BMS balance connectors etc. |
| Hot glue + silicone sealant | $15 | Cable strain relief inside hive |
| 3D printer access | — | Or a print service — ~$20 for gate + shield |

## Totals (order-of-magnitude)

| Bucket | ~$ |
|---|---:|
| Compute (Pi 5 + Pico + SD + PSU) | $95 |
| Sensors (excluding optional CO₂/VOC/rain) | $200 |
| Sensors (all optional included) | $330 |
| Power system (incl. cell tester) | $400 |
| Enclosures & assembly | $150 |
| **Base total (minimum viable)** | **~$800** |
| **Fully loaded** | **~$1,000** |

Everything except the Victron MPPT and Opus tester has cheaper Chinese equivalents; you can shave $150–200 if you're willing to accept lower quality on those two items. I would not recommend cutting the MPPT or the tester — those are the two components where a bad decision lights a fire.
