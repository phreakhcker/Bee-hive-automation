# Phase 03A — Battery, Option A (salvaged 18650 pack)

**This is one of two parallel Phase 03 docs.** If you're building the
purchased-LiFePO4 path, skip this and read
[Phase 03B](03-battery-B.md) instead.

Goal at end of phase: 12 matched, tested, characterized 18650 cells
assembled into a **3S4P** pack (three parallel groups of four, in
series), with a Daly 3S 20 A smart BMS wired and Bluetooth-verified.

Time: **2–3 weeks calendar** because the self-discharge test alone is a
week. Actual hands-on time is maybe 6–8 hours spread across that.

Read [`../safety.md`](../safety.md) before touching cells. Read it
again after this phase. It is the single most important document in
this project.

## Parts checklist

From [`../../hardware/BOM.md`](../../hardware/BOM.md) → "Battery — Option A":

- **Opus BT-C3100 V2.2** cell tester (verified US Amazon seller, not a
  clone).
- **40+ candidate 18650 cells.** Salvaged from vape pouches / laptop
  packs, or bought (Samsung 25R / LG HG2 from
  [liionwholesale.com](https://liionwholesale.com/) if new).
- **3× Keystone 1042** 4-cell 18650 holders with solder tabs.
- **~1 m pure nickel strip**, 0.15 × 8 mm (magnet test on arrival —
  should be only weakly magnetic; strongly magnetic = nickel-plated
  steel, wrong material).
- **Daly 3S 20 A smart BMS** with Bluetooth (buy from Overkill Solar or
  the Daly Official AliExpress store; avoid random Amazon third parties).
- **14 AWG silicone stranded** wire (red + black), ~1 m each.
- **22 AWG silicone stranded** wire in 4 colors for the BMS balance
  leads.
- **JST-XH 4-pin connector** kit — the Daly ships with one but a kit
  saves you if you kill it.
- **Vented battery box** (marine-battery style).
- **Ceramic-fiber blanket** to line the box.

Plus you'll want a phone with the free **Smart BMS** app (Daly's own —
find it in your app store, search "SMART BMS Daly").

## Step 1 — Visual + voltage triage (Day 1)

For each candidate cell:

1. **Reject on sight** if any of: puffy sides, dented case, torn wrap,
   rusty terminals, wet, warm at rest (touch it — should be room
   temperature), smells odd. **Do not test** a cell that fails visual —
   just retire it (see safety.md for disposal).
2. Wrap-scrape check: if the shrink wrap is torn near the top-cap
   crimp, the metal underneath is the cell's positive side; a bare
   metal can that's inserted upside-down into a holder shorts the pack.
   Re-wrap any that need it.
3. Check open-circuit voltage with your DMM.
   - **< 2.5 V** — reject (lithium plating risk on any recharge).
   - **2.5 – 3.5 V** — acceptable to test; over-discharged but likely OK.
   - **> 3.5 V** — good starting point.

Log each cell's OCV. A cheap notebook works; a spreadsheet is better.
Give every cell a permanent ID (Sharpie on the wrap: "01", "02"...).

**Expected reject rate at this step:** 20-40% of salvaged cells fail
visual or voltage triage. That's normal.

## Step 2 — Capacity + internal-resistance test (Days 2–5)

The Opus BT-C3100 has 4 bays; charge/discharge cycles take ~6 hours per
cell (charge at ~1 A + discharge at 500 mA). So 40 cells → ~10 batches
→ 5 days if you swap bays first thing in the morning and last thing at
night.

For each cell:

1. Insert into an Opus bay.
2. Menu: `Charge Test` mode. Set charge current to **1000 mA**, target
   **4.15 V** (not 4.20 V — we cap voltage below datasheet max to buy
   cycle life). Discharge current **500 mA**, cutoff **3.0 V**.
3. Let it run to completion. The Opus records:
   - Charge capacity (mAh)
   - Discharge capacity (mAh) ← this is what matters
   - Internal resistance (mΩ)
4. Log both discharge-mAh and IR against the cell's ID.

**Cull thresholds:**

| Reading | Action |
|---|---|
| Discharge capacity < 1500 mAh | Reject. Not enough left. |
| Internal resistance > 80 mΩ | Reject. Too lossy, will run hot in parallel. |
| Both above thresholds | Keeper — enter into the matching pool. |

Salvaged vape cells (25R / HG2 / 30Q clones) that pass typically show
**2000-2500 mAh** and **20-50 mΩ**.

**Expected reject rate at this step:** another 20-30% of survivors.

> **📷 Photo needed:** the Opus mid-test with 4 cells in bays and the
> display readable, so builders know what to look for.

## Step 3 — Self-discharge test (Days 6–13)

Charge every surviving cell to 4.15 V (Opus, `Charge Only` mode).
Record OCV immediately after removing from charger.

Set them aside on a **flame-resistant surface** (ceramic tile,
LiPo-safe bag, or metal cookie sheet). Don't stack them; don't leave
them in direct sunlight. Room temperature.

Wait **7 days**. Do not touch them.

After 7 days, measure OCV again on each cell.

**Reject if voltage dropped more than 30 mV.** That indicates a
high-self-discharge cell — will imbalance the pack over time.

## Step 4 — Match into 3 groups of 4 (Day 14)

You need 12 keepers from the survivors. Sort them by capacity, then
group so that:

- Each group's 4 cells have capacity within **±5%** of the group's mean.
- Each group's 4 cells have IR within **±10 mΩ** of the group's mean.

A common approach: sort all survivors by capacity, take the 4 highest
as Group 1, next 4 as Group 2, next 4 as Group 3. Then within each
group, check IR spread and swap cells between groups if needed to keep
IR tight.

If you can't hit both criteria with the cells you have, salvage more
and re-test until you can. **Do not** put a badly-mismatched cell into
a group just to complete the pack — it will drag its parallel group
down and imbalance the pack.

## Step 5 — Physically assemble the pack (Day 15)

1. Slot the 4 cells for Group 1 into a Keystone 1042 holder, all in the
   same orientation (all + up). The Keystone holder has cell-polarity
   arrows on the base — align to those.
2. Solder a short nickel-strip run along all four cell tops (parallel
   +) and another along all four cell bottoms (parallel −). Keep the
   iron time on each cell **under 3 seconds** — heat is what damages
   cells during pack building.
3. Repeat for Groups 2 and 3.
4. Stack the three groups (some builders zip-tie them; some hot-glue
   them into a plastic tray). Wire the three groups in **series** with
   14 AWG silicone: G1(+) → G2(−), G2(+) → G3(−). G1(−) is pack
   negative; G3(+) is pack positive.

> **📷 Photo needed:** the completed pack with three groups clearly
> visible, series wire runs labeled, and the balance-tap points
> highlighted (G1+, G2+, G3+).

**Do NOT DIY-spot-weld** unless you already own a spot welder and know
how to use it. A poorly-tacked weld on a salvaged cell is one of the
most reliable ways to start a fire.

## Step 6 — Wire the Daly BMS (Day 15)

Daly 3S 20 A BMS terminals:

- **B−** → pack negative (G1 bottom).
- **B1** → G1 top (between G1 and G2).
- **B2** → G2 top (between G2 and G3).
- **B3** → G3 top (= pack positive).
- **P−** → load negative (this is what the fuse and buck will connect to
  in Phase 04).
- Pack positive goes **direct** to the load positive path, through the
  ANL fuse, not through the BMS.

The balance leads land on a **JST-XH 4-pin** connector in this order,
looking at the plug with the tab facing away from you:

```
Pin 1 (leftmost): B−
Pin 2:            B1
Pin 3:            B2
Pin 4 (rightmost): B3
```

Wrong order will brick the BMS and possibly damage cells. Confirm every
connection with your DMM before plugging in the JST:

- Pin 2 relative to Pin 1: should read ~3.7-4.15 V (one cell voltage).
- Pin 3 relative to Pin 1: should read ~7.4-8.3 V (two cells).
- Pin 4 relative to Pin 1: should read ~11.1-12.45 V (three cells).

If any reading is wildly off (like 15 V or 0 V), stop — you have a
wiring error.

> **📷 Photo needed:** completed BMS wiring with balance leads plugged
> in, main pack leads to B− and pack+, and load leads on P− and the
> pack+ path.

## Step 7 — Bluetooth-verify the BMS

1. **Enable the Bluetooth** on the BMS. On the Daly Smart, this is a
   small switch or requires you to short a specific pad — check the
   sticker on your unit; production varies.
2. Open the **Smart BMS** app on your phone.
3. Pair with the BMS (default password is often `123456`; the manual
   that came with your unit has the actual value).
4. Verify:
   - All 4 voltages (V0/B−, V1, V2, V3) are within 20 mV of each other
     at rest.
   - Cell resistance readings match what the Opus measured (± maybe 10 mΩ
     — the Daly's measurement isn't as accurate but should be in the
     ballpark).
   - No protection events showing in the log.

If any cell reads far outside the others, unplug the JST, re-check
your wiring, and if that's fine, re-check the cell voltages with your
DMM. A cell that reads 3.9 V by DMM but 2.1 V on the BMS is not
actually low — it's a wiring problem.

## Step 8 — Enclosure prep (Day 16)

1. Line the vented battery box with a layer of ceramic-fiber blanket
   cut to fit each interior wall. Any Li-ion event vents flame; the
   fiber contains it long enough for the box to vent through its plugs.
2. Mount the pack + BMS inside. Route the P− and pack+ cables out
   through the highest cable gland on the box wall (heavy vent gases
   sink; put outlets high).
3. Add a 10 kΩ NTC thermistor: potted probe **taped to a cell mid-body**
   (not the tab), with its leads routed out through a smaller gland.
   This will feed the MPPT's battery-temperature input in Phase 04.

## Success check for this phase

- [ ] 12 cells assembled into 3S4P; each parallel group's cells match
      within ±5% capacity and ±10 mΩ IR.
- [ ] DMM at the pack terminals reads 11.1-12.45 V (depending on how
      charged the cells were).
- [ ] Daly BMS paired via Bluetooth, all 4 voltages within 20 mV.
- [ ] Balance leads on the correct JST pins (verified with DMM before
      plugging in).
- [ ] Pack physically inside the vented, fiber-lined battery box; NTC
      probe attached.
- [ ] You have not opened a cell, been startled by heat or a hiss, or
      seen any smoke. If you have, stop and read
      [`../safety.md`](../safety.md) again.

Move on to [Phase 04 — Power stack bench build](04-power-stack.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| Opus reports "high internal resistance" on a fresh-off-the-scavenge cell | Sometimes just needs a slow first charge (500 mA to 3.6 V, rest overnight, then normal test). If IR is still > 80 mΩ, reject. |
| Cells refuse to sit level in the Keystone holder | Slightly bent tab. File flat, or re-seat. If tabs are corroded, reject the cell. |
| Nickel strip won't take solder | You bought nickel-plated **steel**, not pure nickel. Return, buy again. |
| BMS immediately trips as soon as balance leads are connected | Cell voltages too far apart (some Daly models refuse to arm if any two cells differ by > 200 mV). Charge each cell individually to 3.8 V, retry. |
| Bluetooth app finds the BMS but won't connect | Default password varies — try `123456`, `000000`, or the value printed in the box. Some units want the "BLE-Q" app instead of "Smart BMS". |
| Cell heats up during test | Stop the test. That cell is failing. Cool it in a fire-safe location and dispose of it. Don't try to "revive" it. |
| You lit something on fire | Refer to safety.md. Don't use water on a Li-ion fire — smother with sand or a Class D extinguisher. |

## What NOT to do

- **Do not** connect the pack to anything other than the Daly BMS
  P− terminal for its load path.
- **Do not** charge without the BMS in circuit. Ever.
- **Do not** solder directly to cell terminals. Use spot-weld tabs
  (built into the Keystone 1042) or the pre-attached tabs of "tabbed"
  cells if you bought new.
- **Do not** stack cells in a way that lets a shorted case touch
  another cell's terminal (this has killed people).
- **Do not** skip the self-discharge test. This is the test that
  catches slow-death cells before they ruin your pack in the field.
