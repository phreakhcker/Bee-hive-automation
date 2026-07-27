# Phase 04 — Power stack bench build + burn-in

Goal at end of phase: a fully wired, fused, and running power stack on
your bench — solar panel → MPPT → fuse → battery pack → fuse → buck →
5 V rail — with a dummy load simulating the Pi. Two-week burn-in
running to catch any bad cells (Option A) or infant-mortality parts
(Option B).

Time: **~2 hours build**, then **10-14 days bench burn-in** running
before you move to Phase 05. That burn-in is the difference between
finding a problem on your bench (fixable) and finding it at the hive
(a pain).

## Prereqs

- Phase 01 done (Pi is functional).
- Phase 02 done (Pico firmware runs and emits JSON).
- **Either** Phase 03A **or** Phase 03B done (you have a battery pack
  with load pigtails and an NTC probe).

## Parts checklist

From [`../../hardware/BOM.md`](../../hardware/BOM.md) → "Power system —
protection & charging":

- **Renogy 100 W** 12 V monocrystalline panel (or equivalent 60-120 W
  panel — if you're using the salvaged traffic-flasher panel, measure
  Voc first per [`../power-system.md`](../power-system.md)).
- **10 AWG MC4 solar cable pair**, 3 m.
- **Victron SmartSolar MPPT 75/15** (**authorized US dealer only** — see
  BOM counterfeit note).
- **Pololu D36V50F5** 5 V synchronous buck.
- **ANL fuse + inline holder**: **15 A for Option A**, **20 A for Option B**.
- **ATO/ATC 10 A fuse + inline holder** — load-side.
- **10 kΩ NTC thermistor** — already attached in Phase 03.
- **14 AWG silicone stranded** wire, red + black — a couple more
  meters beyond what you used in Phase 03.
- **Dummy load** for burn-in — a 12 V car headlight bulb (~10 W) works;
  a 5 V USB power bank being charged is another option.
- **2200 µF, 10 V+ low-ESR capacitor** — bulk reservoir at the Pi end
  of the buck (installed later at the Pi during Phase 12 / enclosure
  assembly, but buy it now).

Plus you'll want the VictronConnect app on your phone (App Store /
Play Store, free).

## Step 1 — Sanity-check the solar panel (do this outdoors, in sun)

Before wiring the panel to anything, verify what it actually produces.

1. Take the panel outside, orient it toward the sun (angle roughly at
   the sun; doesn't need to be perfect).
2. Wait 60 seconds for it to warm up and stabilize.
3. **Measure Voc** (open-circuit voltage) with your DMM on the MC4
   leads — one probe on the + lead, one on the −. Do not connect
   anything else.
   - Expected: **18-22 V** for a "12 V nominal" panel (Renogy 100 W is
     typically ~22 V Voc in full sun).
   - **36-44 V** = someone sold you a "24 V nominal" panel. Also fine
     for the Victron 75/15 (accepts up to 75 V), just note it.
   - **< 15 V** = shaded, cloudy, or damaged panel. Investigate before
     wiring in.
4. **Measure Isc** (short-circuit current) by switching your DMM to DC
   amps mode, and touching the probes across the MC4 leads. It will
   spark slightly — that's normal. Read the current.
   - Expected for 100 W / 12 V: **~5.5 A**.
   - Expected for 100 W / 24 V: **~2.8 A**.

If either reading is far off, do not proceed — the panel is damaged or
shaded. Fix that first.

> **📷 Photo needed:** DMM reading Voc on the MC4 leads, so builders
> have a reference for "this is what right looks like."

**Cover the panel with cardboard** before bringing it inside. Any
sunlight through a window means live leads.

## Step 2 — Bench-wire the stack (order matters)

Work with the panel still covered. Do **not** connect the battery until
Step 4.

```
Panel [COVERED]
   │ MC4 pair
   ▼
Victron MPPT 75/15
   │  PV+ / PV−  (panel leads)
   │  BATT+ / BATT−  (goes to fuse → pack)
   │  T− / T+  (NTC probe from Phase 03)
   │
   ├─ BATT+ ──┬──[ ANL 15 A / 20 A ]──┬── pack +
   │          │                        │
   │          │                        │  (pack + is the "always live" rail)
   │          │                        │
   │          └──── to buck VIN + ──[ ATO 10 A ]── D36V50F5 VIN+
   │
   └─ BATT− ────────────────────────── pack −  (also = buck GND)

Buck output:
   D36V50F5 VOUT+ ──── to bench dummy load / eventually Pi 5 V pin
   D36V50F5 GND    ──── to dummy load return / eventually Pi GND
```

Detailed wiring order:

1. **Panel MC4 leads → MPPT PV+ / PV−.** MC4 connectors are polarized
   — they only fit one way. Confirm color at the panel matches color at
   the MPPT.
2. **MPPT T+ / T− → NTC probe leads.** No polarity for an NTC. Follow
   your MPPT's silkscreen; on the 75/15 the terminals are next to the
   BATT+ / BATT− block, labeled with a "T" symbol.
3. **MPPT BATT+ → ANL fuse holder input.** Use 14 AWG silicone. Keep
   this run short (< 30 cm on the bench).
4. **ANL fuse holder output → pack + pigtail.** Not yet connected to
   the pack.
5. **MPPT BATT− → pack − pigtail.** Not yet connected to the pack.
6. **From the pack + pigtail (downstream of the ANL fuse) → ATO fuse
   holder input.**
7. **ATO fuse holder output → D36V50F5 VIN+.**
8. **Pack − pigtail (via a T-junction or terminal block) → D36V50F5 GND
   (input side).**
9. **D36V50F5 VOUT+ → your dummy load + input.**
10. **D36V50F5 GND (output side) → your dummy load return.**

**Leave the pack pigtails disconnected from the pack for now.** All you
have on the bench is a bunch of wire with no live current anywhere.

> **📷 Photo needed:** the full bench layout with everything visible
> and clearly labeled — helps builders verify their own layout.

## Step 3 — Configure the Victron MPPT (before power-up)

You can configure the Victron *before* the panel or battery is live, as
long as it has power. Give it either:

- Power via the panel (with the cardboard cover off briefly), or
- A bench supply hooked to BATT+ / BATT−  at ~12 V, or
- Wait until Step 5 when the battery is connected.

Once it has power, its LED blinks — VictronConnect can pair with it.

1. Open VictronConnect. Pair with your MPPT (default PIN is `000000`;
   the app will prompt you to change it immediately — pick something
   you'll remember).
2. **Update firmware** if the app prompts. Do this before anything
   else — some presets don't exist in older firmwares.
3. Go to **Settings** → **Battery**.

**Settings for Option A (salvaged Li-ion, 3S NMC):**

| Setting | Value |
|---|---|
| Battery preset | User defined / Li-ion |
| Absorption voltage | **12.30 V** |
| Float voltage | 12.10 V |
| Equalization | Disabled |
| Charge current limit | 8 A |
| Temperature compensation | 0 mV/°C |
| Battery temperature sense | Enabled, via NTC |
| Low temperature cutoff | 5 °C (charge disabled) |
| Rebulk voltage offset | 0.4 V |

**Settings for Option B (LiFePO4, 4S):**

| Setting | Value |
|---|---|
| Battery preset | **LiFePO4** (built-in) |
| Absorption voltage | **14.20 V** |
| Float voltage | **13.50 V** |
| Absorption time | 2 hr (default) |
| Equalization | Disabled |
| Charge current limit | 15 A (or panel-limited) |
| Temperature compensation | 0 mV/°C |
| Battery temperature sense | Enabled, via NTC |
| Low temperature cutoff | 5 °C |
| Rebulk voltage offset | 0.4 V |

Save. VictronConnect will apply immediately.

## Step 4 — Connect the battery (order matters!)

**Fuse must be installed and rated correctly before this step.** If
you skipped installing the ANL fuse holder, go back to Step 2 now.

1. Confirm the ATO fuse and ANL fuse are **installed** in their
   holders. Some holders ship without the fuse inside.
2. Confirm the buck-input path is clear (nothing shorting VIN to GND
   at the buck). DMM in continuity mode: probe between VIN+ and GND —
   should read OPEN. If it reads short, you have a wiring error;
   **do not connect the battery** until you fix it.
3. Connect the **black pigtail first** (pack − → BATT− chain).
4. Connect the **red pigtail second** (pack + → ANL fuse chain). You
   may see a small spark as the D36V50F5's input capacitor charges —
   this is normal for a big buck like the 50F5, but if it's a sustained
   arc you have a short.
5. Immediately verify with DMM:
   - Pack voltage still nominal (11-12.6 V for Option A; 12.8-14 V for
     Option B).
   - Voltage across the buck's input (VIN to GND) matches pack voltage.
   - Voltage across the buck's output (VOUT to GND) reads **4.95-5.10 V**.

If the buck output is 0 V, the ATO fuse blew (short somewhere) — turn
off, find the short, replace the fuse, retry.

## Step 5 — Uncover the panel

Once battery + buck are live and stable:

1. Take the cardboard off the solar panel.
2. Check VictronConnect: the app should show:
   - PV voltage: whatever your panel is producing (18-22 V for 12 V
     nominal).
   - PV current: 0-5.5 A depending on sun.
   - PV power: watts flowing in.
   - Battery voltage: your pack voltage.
   - **State**: "Bulk" if the pack is below absorption voltage, "Absorption"
     if at, "Float" if fully charged.

If the MPPT reports no PV, check the MC4 connections (they can be
finicky if not fully seated — you should hear/feel a click when
inserted correctly).

## Step 6 — Bench burn-in (10-14 days)

Now the boring part. Leave it running.

**Set up:**

- Load: 12 V car headlight bulb (~10 W) across the buck output pulls
  roughly the same current as a busy Pi 5. Or run a real Pi under
  synthetic load (`stress --cpu 4` for 5 minutes an hour).
- Log the pack voltage daily. Simplest: DMM reading, in your build
  notebook.
- If you're on **Option A**: use the Daly Smart BMS app to log per-cell
  voltages **hourly** for the first 48 hours, then daily. Any cell
  drifting > 50 mV from its group's average = pull that cell, cull the
  group, rebuild with fresh matched cells.
- If you're on **Option B**: pack voltage is the only signal you get.
  Log it once per day. Should stay within ±0.2 V day-over-day at rest.
- Simulate cloudy days by covering the panel with cardboard for 24-48 hr
  chunks — this exercises the low-voltage cutoff logic without waiting
  for actual weather.

**Success criteria over the two weeks:**

| Metric | Option A pass | Option B pass |
|---|---|---|
| Cell voltages under load | Within 50 mV of each other | (single-cell readings not exposed; monitor pack V only) |
| BMS protection events | Zero | Zero |
| MPPT reports charging on sunny days | Yes | Yes |
| Buck output steady 4.95-5.10 V under all load | Yes | Yes |
| Buck rail sags below 4.85 V under load | Fail — buck can't handle it, upgrade | Same |
| Pack sat idle at rest for 24 hr, voltage drop | < 10 mV | < 20 mV |

**Failure investigation:**

- Cell drifts (Option A) — remove that cell, retest with the Opus,
  probably a marginal cell that snuck through Phase 03A. Rebuild the
  group with a fresh matched cell.
- BMS trips repeatedly (Option A) — verify balance-lead JST order
  again. If correct, the pack is imbalanced — do a manual balance
  (charge every cell individually to 4.10 V, then re-assemble).
- Pack voltage drops steadily on Option B — infant-mortality pack.
  Under warranty; contact seller.
- Buck output sags — the D36V50F5 can source 5.5 A; if your load is
  pulling more, upgrade the buck or reduce load.

## Step 7 — Connect the Pico to its final power source

Once burn-in is complete and everything's stable:

1. Wire the Pico's `VBUS` pin (physical pin 40 on the Pico header) to
   the buck's 5 V rail. Wire Pico `GND` (physical pins 3, 8, 13, 18,
   23, 28, 33, 38 — any of them) to the buck's GND.
2. Wire the Pico's **battery voltage sensing** input: from the pack +
   node, through a **100 kΩ / 22 kΩ voltage divider** to the Pico's
   **GP28** pin (`ADC2`). Reference the resistor values in
   `firmware/pico/config.py`: `BATT_ADC_PIN = 28` and
   `BATT_DIVIDER_RATIO = 5.545`. (For Option B's higher pack voltage,
   check that the divided voltage stays under 3.3 V — see
   [`../power-system.md`](../power-system.md) "What stays the same".)
3. Plug the Pico's USB-CDC into the **Pi's** USB port (not your
   laptop's — the Pi is what ingests the packets in the field).

**One-time software adjustment for Option B:** edit
`/etc/beehive/config.yaml` on the Pi to shift the battery thresholds:

```yaml
battery:
  low_warn_v: 12.5       # was 11.4 for Option A
  low_shutdown_v: 11.8   # was 10.8 for Option A
  hard_cut_v: 11.0       # was 9.9 for Option A
```

Then restart the service:

```bash
sudo systemctl restart beehive-shutdown-guard
```

For Option A, the file already has the correct values from the
example config — no edit needed.

## Success check for this phase

- [ ] Buck output measures 4.95-5.10 V continuously, under load and no load.
- [ ] MPPT reports charging when the panel is uncovered in sun.
- [ ] Two weeks of burn-in complete with no BMS trips, no cell drift
      (Option A), no unexplained pack-voltage sag.
- [ ] `/etc/beehive/config.yaml` `battery` thresholds match your option.
- [ ] Pico is now powered from the buck, not USB from the laptop.
- [ ] Pico plugs into the Pi's USB port and JSON packets appear in the
      Pi's SQLite: `sudo sqlite3 /var/lib/beehive/hive.db 'SELECT ts, v_pack FROM readings ORDER BY ts DESC LIMIT 5;'` should show recent readings with sensible `v_pack` values.

You now have a working off-grid compute rail with a live battery
telemetry link. Sensor phases are next (Phase 05+, upcoming — not yet
written in this session).

## Troubleshooting

| Symptom | Fix |
|---|---|
| MPPT never leaves "Bulk" state | Panel isn't producing enough current to hit the absorption threshold. Check panel voltage under load. |
| MPPT LED red / fault | VictronConnect will show the specific error. Most common: reversed panel polarity, or PV voltage exceeds the 75 V limit (a 24 V nominal panel wired in series with another = too much). |
| Buck output 0 V but pack is live | ATO fuse blew. Something shorted. Disconnect load, replace fuse, add load back one wire at a time to find the short. |
| Buck output oscillates or squeals | Missing bulk capacitance at the load end. Add the 2200 µF cap between VOUT and GND at the load. |
| Pico enumerates on Pi but no JSON in SQLite | Check `sudo journalctl -u beehive-ingest -f`. Most likely the ingest service can't open `/dev/ttyACM0` — fix: `sudo usermod -aG dialout pi && sudo reboot`. |
| Daly BMS trips as soon as load draws current | (Option A) Over-current cutoff might be set too low; the Daly's default is fine but some pre-programmed units are stricter. Check current limit in the app. |
| Pack won't charge, MPPT reports temp cutoff active | (Both options) NTC probe reads too cold. Verify with DMM (should be ~10 kΩ at room temp). If open (∞), NTC lead is broken. |
| VictronConnect can't find the MPPT | Bluetooth range issue; hold the phone near the MPPT. If still nothing, the MPPT's Bluetooth may need to be manually enabled — long-press the mode button on the front. |

## What NOT to do

- **Do not** connect the panel to the MPPT before the battery is
  connected. Victron controllers can be damaged by "PV before BATT"
  power-up sequences on some firmware revisions.
- **Do not** skip the fuses. They exist because a single short in
  outdoor wiring can start a fire.
- **Do not** use "12 V" wire from a hardware store. Most is
  copper-clad aluminum — high resistance, gets warm under load. Use
  the silicone-insulated stranded copper from the BOM.
- **Do not** connect the Pi to the buck output until Step 7 (Pico
  first, Pi later once the whole stack is proven — otherwise a
  power-fault could corrupt the SD card mid-write).
- **Do not** skip the burn-in. It is the phase that catches problems
  before they become field failures.
