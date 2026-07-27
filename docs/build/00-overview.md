# Phase 00 — Overview + tools

Before you unbox anything, read this whole page. It's the shortest phase
and it saves you from ordering the wrong stuff.

## What you're building

An off-grid, solar-powered box that sits next to a beehive and measures
weight, temperature (inside and outside), humidity, entrance activity,
pollen loads, in-hive audio and video, and rain. Data lives on the Pi in
SQLite; you view it on a phone or laptop over Wi-Fi via a small Flask
dashboard.

See [`../architecture.md`](../architecture.md) for the block diagram and
data-flow detail.

## The two big decisions before you order parts

### 1. Battery: Option A or Option B?

| | Option A — Salvaged 18650 | Option B — Purchased LiFePO4 |
|---|---|---|
| What you buy | Opus cell tester, Daly BMS, holders, nickel strip. Cells free (salvage) or $30-40 new. | One packaged 12 V LiFePO4 pack with built-in BMS. |
| Effort | 2–3 weeks of cell testing before you can build. | Bolt it in. |
| Fire risk | Higher — Li-ion NMC, recovered cells | Lower — LiFePO4 is the safest common lithium chemistry |
| Choose if | You want the practice, or you already have salvage cells and a tester. | You want to skip battery-pack work and get to beekeeping. |

Full trade-off table in [`../power-system.md`](../power-system.md) →
"Two battery options". You'll follow either [Phase 03A](03-battery-A.md)
or [Phase 03B](03-battery-B.md), not both.

### 2. Which Pico do you have?

- **Pi Pico 2 (RP2350)** — recommended, faster, more RAM. Use the
  `RPI_PICO2` MicroPython UF2.
- **Pi Pico / Pico H (RP2040)** — works fine, use the `RPI_PICO` UF2.
- **Pi Pico W / 2 W** — works, use the matching UF2. Wi-Fi is unused
  (the Pi handles networking), so no benefit to the W.

Pin assignments in [`../hardware.md`](../hardware.md) apply to all
variants.

## Tools you'll need

Split into "must have on day one" and "get before Phase 3+."

### Day 1 (Phases 01–02)

- Laptop with a USB-A or USB-C port (whichever matches your Pico cable).
- **Data-capable** USB cable for the Pico (many charging cables have no
  data lines and will silently fail).
- microSD card reader (built-in or USB) for flashing the Pi.
- Monitor + HDMI-to-microHDMI cable + USB keyboard, **OR** a router
  where you can find the Pi's DHCP lease and SSH in headless.

### Before Phase 03

- Digital multimeter (auto-ranging). Any $30 model. Non-negotiable.
- Temperature-controlled soldering iron (Pinecil V2 or equivalent).
- Wire strippers, flush cutters, heatshrink assortment.
- For **Option A only:** Opus BT-C3100 V2.2 cell tester + 40+ candidate
  18650 cells (see [Phase 03A](03-battery-A.md)).
- For **Option B only:** the packaged LiFePO4 pack (see BOM).

### Before Phase 04

- All the Day-1 stuff, plus:
- 100 W solar panel (Renogy or equivalent).
- Victron SmartSolar MPPT 75/15 (**buy from an authorized dealer** — do
  not risk AliExpress; see BOM counterfeit notes).
- Pololu D36V50F5 5 V buck.
- ANL fuse (15 A for Option A, 20 A for Option B) + ATO 10 A fuse.
- 14 AWG silicone stranded wire, red + black, ~5 m each.

Full list, quantities, prices, and links in
[`../../hardware/BOM.md`](../../hardware/BOM.md).

## Bench setup before you start

You want a spot with:

- Room for a 2 × 3 ft mat (Pi, Pico, sensors, cables all spread out).
- A power strip near your laptop.
- Good light — small sensor boards have tiny silkscreens.
- Nothing flammable within a meter of where you'll test batteries.
- A fire extinguisher (Class D for lithium is ideal; Class ABC works for
  most incipient fires — better than nothing).

**Read [`../safety.md`](../safety.md) before you plug in any battery.**
That page is short and it's the difference between "oh well, ruined a
board" and "oh no, my garage is on fire."

## Success check for this phase

You've read this page and:

- [ ] You've picked Option A or Option B for the battery.
- [ ] You know which Pico variant you have.
- [ ] You have (or have ordered) at minimum the Day-1 tools.
- [ ] You've skimmed [`../safety.md`](../safety.md).

Move on to [Phase 01 — Prep the Pi](01-prep-pi.md).
