# Phase 03B — Battery, Option B (purchased LiFePO4 pack)

**This is the other of two parallel Phase 03 docs.** If you're building
the salvaged-18650 path, skip this and read
[Phase 03A](03-battery-A.md) instead.

Goal at end of phase: a factory 12 V LiFePO4 pack sitting in its
enclosure with confirmed voltage, an NTC temp probe attached, and load
leads ready to hand off to the power stack in Phase 04.

Time: about 30 minutes hands-on. If your pack arrived below 12.8 V,
add whatever charge time it takes to get up there (see Step 4).

## Parts checklist

From [`../../hardware/BOM.md`](../../hardware/BOM.md) → "Battery — Option B":

- **One packaged 12 V LiFePO4 pack with built-in BMS.** Recommended:
  Bioenno BLF-1220A (20 Ah). Alternates: ExpertPower EP1220-20AH,
  LiTime 12V 20Ah, Renogy 12V 20Ah.
- **14 AWG silicone stranded** wire, red + black, ~1 m each — for the
  short pigtails from the pack terminals to your power-stack wiring in
  Phase 04.
- **Ring-terminal or spade-terminal crimps** sized for your pack's
  terminals (most 20 Ah LiFePO4 packs use M6 studs or F2 spade tabs
  — check the datasheet).
- **10 kΩ NTC thermistor** (potted probe, waterproof leads).
- **Vented battery box** (marine-battery style) — the LiFePO4 chemistry
  is much safer than Li-ion NMC and technically doesn't need
  intumescent liner, but the vented box is still worth it for weather
  protection and organized cable exits.
- **PG9 or PG13 cable glands** for wire pass-through on the box.

**Not needed** (you skipped these when you picked Option B):

- ❌ Opus BT-C3100 cell tester
- ❌ Daly external BMS
- ❌ Keystone cell holders
- ❌ Pure nickel strip
- ❌ Individual 18650 cells

## Step 1 — Unbox and inspect

1. Open the pack's shipping box carefully — factory LiFePO4 packs are
   heavy (~2.5 kg for 20 Ah).
2. Verify the pack model against your order. If you ordered a Bioenno
   BLF-1220A, the label should read exactly that. Wrong pack means
   wrong chemistry means wrong Victron config — do not proceed.
3. **Check for shipping damage.** Cracked case, bulging sides, hissing,
   any odor other than fresh plastic → do not use, contact seller. This
   is rare for LiFePO4 but not impossible.
4. Note the **manufacturing date** printed on the label. Anything more
   than 12 months old at delivery is fine (LiFePO4 has very low
   self-discharge) but note it in your log.

## Step 2 — Measure the pack voltage

With your DMM set to DC volts:

- Probe the pack terminals directly (not through any connector — bare
  metal to bare metal).
- Read the voltage.

**Expected reading:** anywhere from 12.8 V (shipped at ~30% SOC, which
most manufacturers do for shipping-safety reasons) up to 13.6 V
(shipped near full).

| Reading | What it means | Action |
|---|---|---|
| 12.8 – 13.6 V | Normal ship state | Fine — proceed |
| 10.0 – 12.8 V | Discharged in transit; unusual but not damaging for LiFePO4 | Charge before deploying (Step 4) |
| < 10.0 V | Pack's internal BMS should have cut off at ~10.0 V; if it didn't, the pack has an issue | Contact seller before using |
| > 13.7 V at rest | Someone charged and shipped it; unusual but harmless | Fine — proceed |
| 0 V or wildly wrong | Dead pack or internal short; **do not attempt to charge** | Contact seller |

Log the reading before you do anything else.

## Step 3 — Attach the NTC probe

The MPPT will use a 10 kΩ NTC to disable charging when the pack is too
cold. Even though the pack's internal BMS also does this, the MPPT-side
cutoff is a useful second layer — and the LiFePO4 pack won't tell you
its own temperature over any wire you can read from the outside.

1. Tape or gently strap the potted NTC probe to the **flat face of the
   pack's case**, midway between top and bottom. Kapton tape or foam
   tape is fine. Avoid the terminal end (localized heating from load
   currents can bias the reading).
2. Route the NTC leads out through one of the cable glands in the
   battery box.
3. Label the loose end with masking tape — it's going to the Victron
   MPPT's `T-` and `T+` (or `TS+` / `TS-`, per your MPPT's silkscreen)
   in Phase 04.

## Step 4 — Charge the pack, if needed

If Step 2 showed less than ~13.0 V and you want to bench-test the whole
system starting from a healthy full pack, charge it up.

Options:

- **The pack's included charger**, if one shipped with it. Most Bioenno
  / LiTime / ExpertPower packs sell the charger separately — check
  what was in your box.
- **A benchtop DC power supply**, set to **14.2 V** with a current
  limit of 5-10 A. Connect + to +, − to −. The pack's internal BMS will
  cut off charge when full.
- **Wait for Phase 04.** The Victron MPPT you're about to install will
  charge the pack from the solar panel. If you're not in a hurry, just
  go — a partially-charged pack is fine for bench burn-in.

Do NOT charge a LiFePO4 pack with a lead-acid charger set to 14.4 V+
absorption unless you know it also does the right float voltage
(13.5 V) — most cheap lead-acid chargers float at 13.8 V, which is
harmless for LiFePO4 but wastes cycle life over time.

## Step 5 — Wire the load pigtails

You need short leads from the pack terminals ready to hand off to the
power stack in Phase 04.

1. Cut two ~40 cm lengths of 14 AWG silicone: one red, one black.
2. Crimp a ring or spade terminal to one end of each (sized for your
   pack's studs — M6 is common for 20 Ah class).
3. Leave the other ends bare — they'll get their final connectors when
   you build the power stack.
4. Attach the crimped ends to the pack. **Torque as specified in the
   pack's datasheet** (usually 4-6 Nm for M6). Don't guess — over-tight
   cracks the terminal casting, under-tight causes resistive heating
   under load.

**Order of attachment when actually connecting to a pack later:** black
(negative) first, then red (positive). Reverse order for removal (red
off first, then black). This convention reduces the chance of a
short-to-chassis surprise.

## Step 6 — Mount the pack in the enclosure

1. Line the pack in position inside the vented box. Most 20 Ah packs
   fit a marine "group 24" or smaller battery box.
2. Secure it so it can't slide around — foam wedges, hook-and-loop
   strap around the box interior, or the box's included tie-down.
3. Route the load pigtails out through the highest cable gland (heavy
   gases sink — put outlets high even though LiFePO4 doesn't vent).
4. Route the NTC probe leads out through a smaller gland or the same
   one as the pigtails (with a proper multi-conductor gland or
   heatshrink to seal around both cables).

> **📷 Photo needed:** the pack sitting in its enclosure with the
> pigtails and NTC leads routed out through their cable glands, and the
> box lid open so the layout is visible.

## Step 7 — Verify one more time

Before you close the lid:

- [ ] DMM at the pigtail bare ends reads the same voltage as at the
      pack terminals (± 10 mV). If different, you have a bad crimp.
- [ ] DMM in continuity mode: red pigtail to pack + terminal =
      continuous. Black pigtail to pack − = continuous. Red pigtail to
      pack − = OPEN (not continuous). Black to pack + = OPEN. If any of
      these fail, you crossed a wire.
- [ ] NTC leads at their loose end read approximately 10 kΩ at room
      temperature (± 20% is normal). If open (∞), the NTC probe is bad
      or a lead is broken.
- [ ] Pack is physically secure inside the box, load cables have
      strain relief at the cable gland.

Close the lid loosely for now — you'll be back in the box during
Phase 04.

## Success check for this phase

- [ ] Pack terminals read 12.8 – 14.0 V.
- [ ] Load pigtails wired, torqued, and verified with DMM (no crossed
      polarity).
- [ ] NTC probe attached to pack case and leads routed out.
- [ ] Pack sits in the enclosure with cable strain relief.
- [ ] You haven't smelled anything, seen any sparks, or felt anything
      warm.

Move on to [Phase 04 — Power stack bench build](04-power-stack.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| Pack arrived at 0 V | Internal BMS in shipping mode (some manufacturers do this). Try a brief pulse from a bench supply at 12 V; that "wakes" the BMS. If it doesn't come up, contact seller. |
| Terminals feel "loose" when I tighten the ring terminal | Over-torqued at some point in the past. Do not fight it — contact seller. |
| NTC reads open (∞) | Broken lead inside the potted probe. Cheap part; replace it. |
| Pack heats up during first charge | Not normal. Stop charging immediately. Let it cool in a fire-safe location. Contact seller — LiFePO4 should not heat during a normal 0.5C charge. |
| Pack won't hold voltage after 24 hr rest | Internal cell imbalance or bad cell. Under warranty — contact seller. |
| Datasheet says "M8 studs" but stud looks like M6 | Different production revision. Buy new ring terminals for the actual stud size. Don't shim. |

## What NOT to do

- **Do not** open the pack case. The BMS is potted and any tampering
  voids warranty and probably the BMS's safety certifications.
- **Do not** parallel two packs to double capacity without a specific
  paralleling procedure (SOC-match the two packs to within 100 mV
  before connecting, or the imbalance current can trip the BMS). For
  this project, one pack is enough — go 30 Ah if you need more capacity.
- **Do not** put a LiFePO4 pack on a "Li-ion" charger unless it has an
  explicit LiFePO4 mode. Standard Li-ion chargers target 4.20 V/cell
  (16.8 V for a 4S pack), which will damage LiFePO4 cells.
- **Do not** skip the NTC probe. The internal BMS knows the pack's
  temperature but has no way to tell the MPPT; the external NTC gives
  the MPPT that visibility as a second layer of cold-cutoff protection.
