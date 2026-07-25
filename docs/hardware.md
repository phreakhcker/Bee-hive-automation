# Hardware Wiring & Pinouts

Cross-reference this with the SVG diagrams in [`../diagrams/`](../diagrams/). Colors here match the diagrams.

## Wire color convention

| Signal type | Color |
|---|---|
| +5 V | Red |
| +3.3 V | Orange |
| GND | Black |
| I²C SDA | Yellow |
| I²C SCL | Green |
| 1-Wire data | Purple |
| UART / USB data | Blue |
| Interrupt / GPIO | White |
| PWM / control | Grey |
| Analog (ADC) | Brown |
| I²S (BCK/WS/DATA) | Pink |

## Pi Pico 2 — pin assignments

```
                             ┌──USB──┐
                        GP0 ─┤1    40├─ VBUS   (5 V from Pi USB)
                        GP1 ─┤2    39├─ VSYS
                        GND ─┤3    38├─ GND
                        GP2 ─┤4    37├─ 3V3_EN
                        GP3 ─┤5    36├─ 3V3_OUT
                        GP4 ─┤6    35├─ ADC_VREF
                        GP5 ─┤7    34├─ GP28 / ADC2   ── pack voltage (÷5)
                        GND ─┤8    33├─ GND / AGND
                        GP6 ─┤9    32├─ GP27 / ADC1   ── (spare analog)
                        GP7 ─┤10   31├─ GP26 / ADC0   ── (spare analog)
                        GP8 ─┤11   30├─ RUN            (Pi can reset Pico)
                        GP9 ─┤12   29├─ GP22           ── DS18B20 1-Wire data
                        GND ─┤13   28├─ GND
                       GP10 ─┤14   27├─ GP21 / I²C0 SCL ── SHT41, BME280
                       GP11 ─┤15   26├─ GP20 / I²C0 SDA ── SHT41, BME280
                       GP12 ─┤16   25├─ GP19           ── HX711 SCK
                       GP13 ─┤17   24├─ GP18           ── HX711 DOUT
                        GND ─┤18   23├─ GND
                       GP14 ─┤19   22├─ GP17 / I²C1 SCL ── VEML7700, SCD41, SGP40
                       GP15 ─┤20   21├─ GP16 / I²C1 SDA ── same
                             └───────┘

GP0..GP15 (mostly free): reserved for the 8-channel bee gate PIO
   GP0..GP7   : IR gate channel A phototransistors  (8 channels)
   GP8..GP15  : IR gate channel B phototransistors  (8 channels)
   GP4/GP5    : reused for I²C0 if you shrink the gate — see notes
```

**Pin choice rationale:**
- I²C0 (SHT41, BME280) is on GP20/GP21 — moderate-speed devices; SHT41's polymer-membrane variant is inside the hive.
- I²C1 (VEML7700, SCD41, SGP40) is on GP16/GP17 — separated so a hot SCD41 or hung SGP40 doesn't take down the hive-interior sensors on I²C0.
- HX711 gets a dedicated pair GP18/GP19 — its bit-banged timing must not fight PIO.
- DS18B20 on GP22 — 1-Wire, 4.7 kΩ pull-up to 3V3.
- Pack voltage on ADC2 (GP28), fed from a 100 k / 22 k divider (12.6 V max → 2.27 V — well inside Pico's 3.3 V ADC range).
- Bee gate uses GP0–GP15 with PIO. If you want fewer channels (e.g. 4 wide × 2 tall), you can free some pins.

## Detailed sensor wiring

### HX711 → Pico

| HX711 pin | Pico pin | Wire color |
|---|---|---|
| VCC | 3V3_OUT (pin 36) | orange |
| GND | GND | black |
| DT (DOUT) | GP18 | white |
| SCK | GP19 | grey |

Load cells (4× 50 kg half-bridge bars) → HX711 as a **full Wheatstone bridge**. Wiring for a typical kit:

| Load cell wire | HX711 pin |
|---|---|
| Red (E+) | E+ |
| Black (E–) | E– |
| Green (A– / S–) | A– |
| White (A+ / S+) | A+ |

For the 4-cell config, wire the 4 cells so that opposite cells make the diagonals of the bridge — most kits come with a small combinator board that does this. If not, follow [the SparkFun 4-load-cell guide](https://learn.sparkfun.com/tutorials/load-cell-amplifier-hx711-breakout-hookup-guide).

**Cable:** use CAT6 with foil shield. Data pair (DT, SCK) on one twisted pair; power (VCC, GND) on another. Foil shield → drain wire → Pico GND at the Pico end only. Keep the run under 1 m if possible.

### DS18B20 array → Pico

| DS18B20 wire | Pico pin | Wire color |
|---|---|---|
| Red (VDD) | 3V3_OUT | orange |
| Yellow (DQ / data) | GP22 | purple |
| Black (GND) | GND | black |

**4.7 kΩ pull-up** from GP22 to 3V3.

Wire all four probes in parallel on one bus. Each has a unique 64-bit ROM address; MicroPython's `onewire` library enumerates them. Log their addresses during setup and label each probe (P1 top cover, P2 above brood, P3 side brood, P4 entrance) in `config.py`.

### SHT41 & BME280 (I²C0)

| Device | Addr | Pico pin | Wire |
|---|---|---|---|
| SHT41 VIN | — | 3V3_OUT | orange |
| SHT41 GND | — | GND | black |
| SHT41 SDA | 0x44 | GP20 (I²C0 SDA) | yellow |
| SHT41 SCL | 0x44 | GP21 (I²C0 SCL) | green |
| BME280 VIN | — | 3V3_OUT | orange |
| BME280 GND | — | GND | black |
| BME280 SDA | 0x76 | GP20 | yellow |
| BME280 SCL | 0x76 | GP21 | green |

I²C pull-ups: both breakouts have them on-board. If you have both connected, you now have 2 × 10 k in parallel = 5 k pull-ups — fine at 100 kHz.

### VEML7700, SCD41, SGP40 (I²C1)

| Device | Addr | Pico pin | Wire |
|---|---|---|---|
| VEML7700 SDA | 0x10 | GP16 | yellow |
| VEML7700 SCL | 0x10 | GP17 | green |
| SCD41 SDA | 0x62 | GP16 | yellow |
| SCD41 SCL | 0x62 | GP17 | green |
| SGP40 SDA | 0x59 | GP16 | yellow |
| SGP40 SCL | 0x59 | GP17 | green |

All powered from 3V3. **SCD41 draws ~205 mA in peak measurement** — supply it directly from 3V3 with a 10 µF cap nearby.

### Bee-gate IR array

Each of 8 tunnels has two ITR9606 slotted opto-interrupters spaced 6–8 mm apart along the tunnel axis. IR LED side is current-limited by a 220 Ω resistor from 3V3. Phototransistor collector goes to Pico GPIO with a 10 kΩ pull-up to 3V3; emitter goes to GND.

| Channel | Beam-A GPIO | Beam-B GPIO |
|---|---|---|
| 1 | GP0 | GP8 |
| 2 | GP1 | GP9 |
| 3 | GP2 | GP10 |
| 4 | GP3 | GP11 |
| 5 | GP4 | GP12 |
| 6 | GP5 | GP13 |
| 7 | GP6 | GP14 |
| 8 | GP7 | GP15 |

Direction logic (in `drivers/bee_gate.py`): if beam A trips first then beam B within 500 ms, it's an **exit** (bee moved outward). B-then-A within 500 ms is an **entry**. Isolated single trips (no complementary event within 500 ms) are logged as ambiguous.

**Physical build** (see [`../diagrams/bee-gate.svg`](../diagrams/bee-gate.svg)):
- 3D-printed **ASA or PETG** entrance restrictor, 8 mm × 8 mm tunnels, 30 mm deep.
- The ITR9606's 5 mm slot straddles the tunnel — tunnel wall passes through the slot with 1.5 mm clearance each side.
- Two ITR9606s per tunnel, 8 mm apart along the tunnel.
- Slide-out tray for cleaning propolis.
- **Do not use PLA** — it warps in summer sun. ASA or PETG only.

### Battery pack voltage monitor

Pack + → 100 kΩ → GP28 (ADC2) → 22 kΩ → GND. This divides the pack voltage by (100+22)/22 ≈ 5.55×, so at 12.6 V max the ADC sees 2.27 V (well under 3.3 V max).

Calibration: measure actual pack voltage with a DMM, read the raw ADC, compute a per-unit multiplier in `config.py`.

### RUN reset line

Pi GPIO23 → Pico RUN (pin 30). Pi's `shutdown_guard.py` can pulse this line low for 200 ms to hard-reset a wedged Pico.

## Pi 5 — pin assignments

| Function | Pi GPIO | Wire | Notes |
|---|---|---|---|
| I²S mic BCK | GPIO18 (physical 12) | pink | SPH0645 BCLK |
| I²S mic LRCK | GPIO19 (physical 35) | pink | SPH0645 LRCLK / WS |
| I²S mic DATA | GPIO20 (physical 38) | pink | SPH0645 DOUT |
| Pico RUN reset | GPIO23 (physical 16) | white | Pull low ≥100 ms to reset Pico |
| Low-batt notify | GPIO24 (physical 18) | white | Pico can raise this to warn Pi (redundant to serial) |
| Cam entrance | CSI-1 | ribbon | Pi Camera Module 3 |
| Cam inside | CSI-0 | ribbon | Pi Camera Module 3 NoIR |
| Rain sensor | USB (via FT232 adapter) | blue | `/dev/ttyUSB0` for RG-9 |

Enable I²S in `/boot/firmware/config.txt`:
```
dtparam=i2s=on
dtoverlay=googlevoicehat-soundcard
```
The `googlevoicehat-soundcard` overlay is the closest match for the SPH0645; alternative: build a custom overlay (search "SPH0645 raspberry pi overlay").

Enable both CSI cameras in the same file:
```
dtoverlay=imx708,cam0
dtoverlay=imx708,cam1
```

## Power delivery to the Pi

Pololu D36V50F5 output (5 V, up to 5 A) → Pi 5's **GPIO 5 V pin (physical pin 2 or 4)** and a GND pin. **This bypasses the Pi's onboard PSU management and its aggressive under-voltage detection.**

Alternative (safer, keeps the PMIC involved): 5 V → USB-C via a soldered pigtail. Slightly more voltage drop but cleaner shutdown behavior if the buck sags.

Add a **large capacitor (2200 µF, 10 V+) at the Pi's 5 V rail** to ride out momentary current spikes (camera + Wi-Fi bursts).

## Grounding

Single-point ground at the Pi. All GNDs (Pico, HX711, sensors, buck output) return to the Pi's GND rail. Do not create ground loops by running two separate GND returns to the battery.

## What to build first

1. Bench-test the power stack (see [`safety.md`](safety.md), two-week burn-in).
2. Flash Pico, wire up **just one sensor at a time**, confirm it reads via serial monitor.
3. Once all sensors read on the bench, print/build the bee gate and validate IR beams with your finger before you put it on the hive.
4. Move to the hive last. Do the transition on a mild evening — cool bees are calm bees.
