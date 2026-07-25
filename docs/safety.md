# Safety

Read this before you start. It's short.

## Salvaged Li-ion cells

Every cell you pull from a disposable vape is guilty until proven innocent.

**Immediate discard, no testing:**
- Puffy, dented, torn wrap, rusty, wet, warm at rest, smells of solvent.
- Reads under 2.5 V — deep discharge plates lithium onto the anode. That plated lithium can grow a dendrite that shorts the cell weeks later. Not worth the risk.

**Mandatory testing pipeline** — see [`docs/power-system.md`](power-system.md) for detail:
1. Voltage check with a DMM.
2. Capacity + internal-resistance test on an **Opus BT-C3100** (or equivalent that measures IR — the $8 ZB2L3 does not).
3. One-week self-discharge test — reject cells that drop > 30 mV.
4. Match cells within ±5 % capacity and ±10 mΩ IR for any parallel group.

You will test 40–60 cells to find 12 keepers. That is normal for salvaged stock.

## Wiring rules that are not optional

1. **A fuse between battery+ and everything else.** ANL 15 A. This prevents a wiring short from turning your hive into a bonfire.
2. **A separate load fuse** (ATO 10 A) between the BMS output and the buck converter.
3. **Battery enclosure separate from electronics enclosure.** If a cell vents, hot electrolyte gas should escape to atmosphere, not into your Pi.
4. **A thermal fuse** (SEFUSE SF77E, 77 °C, one-shot) in series with the pack. $2. Do it.
5. **Silicone-insulated wire**, not PVC. Outdoor UV and hive propolis both degrade PVC.
6. **Strain relief on every cable entering an enclosure.** Cable glands, not zip-ties through a drilled hole.
7. **Absolutely never charge Li-ion below 0 °C.** Sub-freezing charging plates lithium — permanent damage that accumulates and eventually shorts. Wire the 10 kΩ NTC to the Victron's battery-temp input and let it disable charging automatically. In climates with hard winters, add a manual seasonal disconnect on the solar side as belt-and-suspenders.

## Charge to 4.10 V/cell, not 4.20 V

Configure the MPPT absorption voltage to **12.30 V** for a 3S pack (= 4.10 V/cell). You lose ~10 % capacity vs 4.20 V. You gain **2–3× cycle life**. For salvaged cells that have already lost part of their life, this is the difference between one year and four years of service.

## Two-week bench burn-in

Before you deploy: assemble the entire power stack on a bench, connect a resistive load equivalent to the Pi (a car headlight bulb works), and run it for two weeks. Watch the Daly BMS Bluetooth telemetry every day.

**Reject and rebuild any parallel group where a cell drifts more than 50 mV from its neighbors under load.**

## Hot weather

100 °F ambient inside a black electronics box in direct sun can hit 60 °C. Li-ion above 45 °C degrades fast; above 60 °C it becomes unsafe. Put the battery box in shade. If that's impossible, add a thermistor and log its temperature — you may need to bury the box or add passive shading.

## The camera and its IR LEDs

- **850 nm IR** — invisible-ish, bees don't see it well, safe for humans in the doses used here.
- **Do not** stare into the IR array at close range for extended periods. Your eye's blink reflex doesn't fire for IR because you can't see it. Point it into the hive, not at yourself.

## Working near the hive

Bees will investigate you the moment you start drilling, wiring, or making vibrations. Do initial installation in the morning before foragers are active, or in the evening after they've returned. Wear a veil. Have smoke ready. **Do the entire electrical build on the bench first** — the only work you should do at the hive is mounting and connecting pre-tested subassemblies.

## Fault modes worth knowing

| Fault | Symptom | What happens if you ignore it |
|---|---|---|
| Salvaged cell develops internal short | Cell voltage drops abruptly under load; BMS may or may not catch it | Runaway heating → vent or fire |
| BMS balance failure | One cell drifts > 100 mV from siblings | Overcharge of one cell → vent |
| MPPT set to lead-acid float | Pack stays at 13.6+ V continuously | Slow degradation → vent |
| PVC wire in hive | Propolis attacks insulation; bees chew through | Short circuit inside the hive |
| No fuse | Any wire short | Fire |
| Charging in freezing weather | Nothing visible at the time | Lithium plating accumulates; cell will fail unpredictably later |

None of this is meant to scare you off. Every one of these is trivially preventable. The point is that you need to prevent all of them, not just most of them.
