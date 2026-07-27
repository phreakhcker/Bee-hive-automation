# Power System

Read [`safety.md`](safety.md) first if you haven't.

## Two battery options

You have a choice for the battery half of the system. The rest of the stack
(panel → MPPT → fuse → buck → Pi) is the same either way.

| | **Option A — Salvaged 18650 (3S4P)** | **Option B — Purchased LiFePO4 pack (4S built-in BMS)** |
|---|---|---|
| Chemistry | Li-ion NMC (recovered vape/laptop cells) | LiFePO4 (lithium iron phosphate) |
| Nominal V / range | 11.1 V / 9.0–12.6 V | 12.8 V / 10.0–14.6 V |
| Usable energy | ~89 Wh (12 × ~2.2 Ah at 3.7 V) | 256 Wh (20 Ah at 12.8 V) |
| Autonomy at ~5 W average load | ~18 hr | ~48 hr |
| External BMS | Required (Daly 3S 20 A) | Built into the pack |
| Cell testing / matching | Required — 40+ cells over 2–3 weeks | None |
| Weight | ~600 g | ~2.5 kg |
| Fire risk | Higher (recovered cells, less mature chemistry) | Lower (LiFePO4 is the safest common lithium chemistry) |
| Winter behavior | Same NTC cutoff logic; smaller pack drains faster | Same NTC cutoff; larger pack rides through longer |
| Cost | $30–70 (mostly the tester + BMS + holders) | $100–150 (the pack) plus the same MPPT/fuse/buck |
| Right for | You already have salvage cells and want the practice | You want to bolt it together and get to the beekeeping |

**Both options work with the same Victron 75/15 MPPT, same solar panel, same
buck, and same Pico voltage-divider sensing.** Only the pack, the BMS
requirement, and the Victron charge-profile settings differ. See the
"Option B" section below for the deltas.

## Overview (Option A — salvaged 3S)

```
     ┌──────────────┐
     │  100 W Solar │
     │   Panel      │
     └──────┬───────┘
            │  ~18 V open-circuit, ~5.5 A short-circuit
            │  MC4 connectors, 10 AWG
            ▼
   ┌────────────────────────┐          10 kΩ NTC (battery temp)
   │ Victron SmartSolar     │◀───────── potted, taped to pack
   │ MPPT 75/15             │          (disables charge below 0 °C)
   │  • Li-ion profile      │
   │  • absorption 12.30 V  │
   │  • float 12.10 V       │
   └───────────┬────────────┘
               │  12.30 V max, current-limited
               ▼
      ┌─────[ANL 15 A]───┐   ◀── fuse
               │
               ▼
   ┌────────────────────────┐
   │ Daly 3S 20 A smart BMS │  ── Bluetooth telemetry (BAT-MON app)
   │  • balance             │
   │  • over-charge protect │
   │  • over-discharge cut  │
   │  • short-circuit cut   │
   └───────────┬────────────┘
               │
               ▼
   ┌────────────────────────┐
   │ 3S4P — 12 matched      │  ~11.1 V nominal, 9.0–12.6 V range
   │ 18650 salvaged cells   │  ~89 Wh actual (varies by salvage quality)
   └───────────┬────────────┘
               │  9.0–12.6 V
               ▼
      ┌─────[ATO 10 A]───┐   ◀── load fuse
               │
   ┌───────────┴────────────────────────┐
   │                                    │
   ▼                                    ▼
┌───────────────┐               ┌──────────────────┐
│ Pololu        │               │ Voltage divider  │
│ D36V50F5      │               │ 100 k / 22 k     │
│ 12→5 V, 5 A   │               │  → Pico ADC2     │
│ synchronous   │               │  (pack V sense)  │
└──────┬────────┘               └──────────────────┘
       │  5 V, up to 5 A
       ▼
  ┌─────────────┐
  │ Pi 5 GPIO   │  and via Pi's 3V3 rail →  Pi Pico + I²C sensors
  │ 5 V pin     │
  └─────────────┘
```

## Salvaged-cell testing pipeline

You will process 40–60 cells and end with 12 keepers matched into three parallel groups of 4.

### Step 1: Visual + voltage triage

Discard immediately: puffy, dented, torn wrap, rusty, wet, warm at rest, smells odd. Then check open-circuit voltage with a DMM. Anything under **2.5 V** — discard (lithium plating risk).

### Step 2: Capacity + IR

Charge each survivor to 4.15 V (not 4.20 V — we're testing at our target operating point) on an **Opus BT-C3100 V2.2**. Discharge at 500 mA to 3.0 V. Record capacity and internal resistance.

**Cull thresholds:**
- Capacity < 1500 mAh → reject.
- IR > 80 mΩ → reject.

Vape cells that pass are usually the well-known 25R / HG2 / 30Q pulls, typically 2000–2500 mAh.

### Step 3: Self-discharge

Charge each remaining cell to 4.15 V. Rest one week. Reject any that drop more than **30 mV**.

### Step 4: Match into groups

Sort surviving cells by capacity. Assemble groups of 4 with:
- capacity within ±5 % of the group mean, AND
- IR within ±10 mΩ of the group mean.

You need 3 groups of 4 = 12 matched cells total.

### Step 5: Assemble

Use **plastic 18650 holders with solder tabs** (Keystone 1042 or similar). Solder short nickel-strip parallel links between the 4 cells in each group. Then connect the three groups in series with 12 AWG for the main current path.

Skip DIY spot welding unless you already own the equipment and know how to use it. A poorly-tacked weld on a salvaged cell is one of the more reliable ways to start a fire.

## BMS wiring

Daly 3S 20 A smart BMS has:
- **B–** to pack negative
- **B1** to positive of cell group 1 (first cell above B–)
- **B2** to positive of cell group 2
- **B3** to positive of cell group 3 (= pack positive)
- **P–** to load negative (through your load fuse then to load)
- Pack positive goes direct to load positive (through the ANL fuse)

Connect balance leads to a JST-XH connector in order: B–, B1, B2, B3. Every Daly ships with a diagram; follow it — reversed leads brick the BMS and possibly the cells.

**Enable Bluetooth**, download the "SMART BMS" app (Daly's), pair, and verify:
- All four voltages (V0/B–, V1, V2, V3) are within 20 mV at rest.
- Cell resistance readings match what you measured on the Opus (they should).

## Victron MPPT configuration

Using the VictronConnect app over Bluetooth:

| Setting | Value | Why |
|---|---|---|
| Battery preset | User defined / Li-ion | |
| Absorption voltage | **12.30 V** | 4.10 V/cell — the "lithium longevity" trade |
| Float voltage | 12.10 V | Well below absorption; safe idle |
| Equalization | Disabled | Not applicable to Li-ion |
| Charge current limit | 8 A | Well under BMS max, gentle on salvaged cells |
| Temperature compensation | 0 mV/°C | Li-ion does not want lead-acid temp comp |
| Battery temperature sense | Enabled, via NTC input | Cold cutoff |
| Low temperature cutoff | 5 °C (charge disabled) | Safety margin above 0 °C |
| Rebulk voltage offset | 0.4 V | Standard |

The 75/15 model can be firmware-updated over Bluetooth if any of these menus are missing — do this first.

## Buck converter setup

The Pololu D36V50F5 is fixed 5 V output — no configuration required. Just wire it:

| D36V50F5 | Wire to |
|---|---|
| VIN | BMS P+ side (through 10 A ATO fuse) |
| GND (input) | BMS P– |
| VOUT | Pi 5 V (GPIO pin 2 or 4) |
| GND (output) | Pi GND (GPIO pin 6, 9, 14, 20, 25, 30, 34, or 39) |

Add a **2200 µF, 10 V+ low-ESR capacitor** across VOUT/GND at the Pi end. This reservoir smooths the Pi 5's transient bursts.

## Low-voltage cutoff — layered defense

| Layer | Voltage | Action |
|---|---|---|
| Software warning | 11.4 V | Dashboard displays "low battery"; alerts sent if MQTT configured |
| Software graceful shutdown | 10.8 V | `shutdown_guard.py` runs `sudo shutdown -h now` |
| Software hard cutoff | 9.9 V | Pico raises GPIO24 → Pi drops Pico's power to sensors |
| BMS UVP | ~9.0 V (3.0 V/cell) | BMS opens P– FET; whole system loses power |
| Cell damage threshold | ~7.5 V (2.5 V/cell) | Below this permanent damage begins — we never reach it |

The important gap: **the software shutdown at 10.8 V happens well before the BMS cutoff at 9.0 V**. That protects the SD card from an unclean power loss.

## Recharge

The MPPT will resume charging as soon as pack voltage climbs. If cells got fully discharged, expect ~24 hours of good sun to fully refill an 89 Wh pack from ~9 V.

Set a **rebulk hysteresis** of 0.4 V so the charger doesn't oscillate near the absorption voltage.

## Option B — Purchased LiFePO4 pack (deltas from Option A)

If you skip salvaged cells and buy a packaged 4S LiFePO4 with an integrated
BMS, everything downstream of the pack terminals stays the same. The
changes:

### What you buy

**Recommended pack — Bioenno BLF-1220A** (12 V 20 Ah LiFePO4, ~$130).
Ham-radio community's default for solar/portable ops for a decade.
Honest spec sheet, factory-direct support, US company. Ships from
Bioenno or Powerwerx.

Alternates (all built-in BMS, same nominal 12 V / ~13.6 V charge / 4S
LiFePO4 chemistry — any of them work with the Victron):

- **ExpertPower EP1220-20AH** — ~$100, Amazon, decent for the price.
- **LiTime 12V 20Ah** — ~$70, Amazon, budget-brand, mass-market.
- **Renogy 12V 20Ah** — ~$110, Renogy direct or Amazon, if you're
  already buying the panel from them.

Sizing note: 20 Ah gives ~2 days of autonomy under cloud. Bump to
**30 Ah** if you're in a northern climate or want more winter margin.
50 Ah is overkill for this load and adds weight + cost with no benefit.

**Distributor honesty:** you asked for a Mouser/DigiKey link. Neither
distributor stocks finished consumer LiFePO4 packs — they carry raw
prismatic cells (EVE 3.2 V, Molicel) plus BMS boards, which is the
same pack-build work as Option A with a different chemistry. If a
DigiKey/Mouser sourcing chain is a hard requirement (e.g. corporate
procurement), tell me and we'll design that variant, but for a
hobbyist the specialty-battery distributors above are the right
channel.

### What you skip

- ✂ **Daly 3S 20 A BMS** — the pack has one built in.
- ✂ **Keystone 1042 holders** — not needed, no cell assembly.
- ✂ **Pure nickel strip** — not needed.
- ✂ **Opus BT-C3100 tester** — not needed unless you also want it for
  general Li-ion work.
- ✂ **Weeks of cell triage + burn-in on the 18650s.** The pack ships
  balanced and tested.

### What changes in the wiring diagram

```
     ┌──────────────┐
     │  100 W Solar │
     └──────┬───────┘
            │
            ▼
   ┌────────────────────────┐          10 kΩ NTC (optional here — the
   │ Victron SmartSolar     │◀───────── pack BMS also does low-T cutoff,
   │ MPPT 75/15             │          but NTC on MPPT is a second layer)
   │  • LiFePO4 preset      │
   │  • absorption 14.20 V  │
   │  • float 13.50 V       │
   └───────────┬────────────┘
               │
               ▼
      ┌─────[ANL 20 A]───┐   ◀── fuse (bump from 15 A because 20 Ah
               │                     pack can source higher inrush)
               ▼
   ┌────────────────────────┐
   │ 12 V 20 Ah LiFePO4     │  10.0–14.6 V range
   │ pack (BMS INTERNAL)    │  Pack does its own cell balancing +
   │                        │  over/under-voltage cutoff
   └───────────┬────────────┘
               │
               ▼
      ┌─────[ATO 10 A]───┐   ◀── load fuse (unchanged)
               │
      (rest of stack unchanged — buck, Pi, Pico ADC divider)
```

### What changes in the Victron config

Replace the Option A settings table with these:

| Setting | Value | Why |
|---|---|---|
| Battery preset | **LiFePO4** (built-in) | The 75/15 has this preset in firmware ≥ v1.50 |
| Absorption voltage | **14.20 V** | 3.55 V/cell — standard LiFePO4 |
| Float voltage | **13.50 V** | 3.375 V/cell — safe idle for LiFePO4 |
| Absorption time | 2 hr (preset default) | Allows the internal BMS time to balance |
| Equalization | Disabled | Never for lithium |
| Charge current limit | 15 A (or panel-limited) | LiFePO4 tolerates full C-rate; no need to derate |
| Temperature compensation | 0 mV/°C | Lithium doesn't want lead-acid temp comp |
| Battery temperature sense | Enabled, via NTC | Redundant with pack BMS but harmless |
| Low temperature cutoff | 5 °C (charge disabled) | LiFePO4 also degrades if charged below 0 °C |
| Rebulk voltage offset | 0.4 V | Standard |

If your Victron's firmware is old and doesn't show a LiFePO4 preset,
update via VictronConnect first — free, over Bluetooth.

### What changes in the software cutoffs

The Pi's `shutdown_guard.py` thresholds shift because LiFePO4 sits at
a different voltage. Edit `pi/services/shutdown_guard.py`:

| Layer | Option A (3S Li-ion) | Option B (4S LiFePO4) |
|---|---|---|
| Software warning | 11.4 V | **12.5 V** |
| Software graceful shutdown | 10.8 V | **11.8 V** |
| Software hard cutoff | 9.9 V | **11.0 V** |
| BMS UVP | ~9.0 V | **~10.0 V** (pack internal) |

The Pico voltage-divider (100 kΩ / 22 kΩ) is safe as-is: max pack
voltage 14.6 V × (22 / 122) = 2.63 V, comfortably below the Pico's
3.3 V ADC ceiling.

### What stays the same

- Same 100 W Renogy panel, same MC4 cabling, same MPPT.
- Same Pololu D36V50F5 buck, same 5 V rail to Pi.
- Same 10 A ATO load fuse.
- Same enclosure layout, same NTC probe placement, same rain sealing.
- Same insulation strategy for cold-weather deployment.
- **Bench burn-in still recommended** — even a factory pack should
  run on your bench for a week before it goes on the hive, so any
  DOA / infant-mortality shows up where you can return it.

## Winter behavior

In climates with sub-freezing days:
1. The NTC → MPPT stops charging below 5 °C.
2. Pack still discharges to run the Pi.
3. If sun returns but pack is cold, it will not recharge until pack warms.
4. This can result in a completely discharged pack sitting for weeks.

Mitigations, in order of hobbyist-friendliness:
- **Accept it.** Deploy a fresh battery in spring; monitor with dashboard alerts.
- **Insulate the battery box.** Salvaged closed-cell foam around the box keeps discharge heat inside; the pack self-heats above freezing during Pi operation. Effective down to about −5 °C ambient.
- **Add a battery heater.** 12 V silicone heater pad, thermostat, powered from the pack. Adds ~5 W parasitic load in cold weather. Only justifiable in serious cold.
- **Seasonal shutdown.** Manual disconnect switch on solar input; bring the pack inside for winter.

## Two-week bench burn-in — what to actually do

1. Assemble everything on a bench, no hive.
2. Load: a 5 V car headlight bulb pulled down to ~2 A draws ~10 W — matches Pi 5 under load.
3. Log Daly BMS Bluetooth cell voltages hourly for 14 days.
4. Log MPPT charge/discharge cycles.
5. Simulate cloudy days by covering the panel with cardboard.
6. **Success criteria:** all cells stay within 50 mV of each other under all load conditions; no BMS protection events; MPPT tracks properly; buck delivers steady 4.95–5.10 V to the "Pi" load.
7. **Failure investigation:** if a cell drifts, remove and rebuild that parallel group. If BMS trips repeatedly, verify balance leads are correct order. If buck output sags below 4.85 V, the buck cannot handle your load — upgrade it.

Do not skip this step. It's the difference between finding a bad cell on your bench (fixable) and finding one at the hive (harder).
