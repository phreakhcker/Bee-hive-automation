# Phase 07 — HX711 + 4× load cells (hive weight)

Goal at end of phase: four 50 kg half-bridge load cells combined into
a single Wheatstone bridge, feeding an HX711 amplifier that talks to
the Pico. Tared to zero on an empty platform, calibrated against a
known reference weight, and reporting `w_kg` in every JSON packet to
within about ±50 g.

Time: about 3 hours, spread over two sessions if you can. Physical
assembly of the stand takes an hour or two. Calibration itself is
fast once the mechanics are sound.

## Prereqs

- Phase 04 done (Pico on the Pi-USB rail from the buck).
- Phase 06 done (you know the "wire, verify, edit config" rhythm).
- Access to a **known reference weight** for calibration. A 10 kg gym
  plate is ideal. Alternatives: 5 × 2 L water bottles (= 10 kg, ± ~0.5 %
  once you weigh them on a kitchen scale), or a bathroom scale + a
  friend willing to stand on the platform.

## Why this arrangement

Beekeepers care about weight because it's the single best signal for
what's happening inside the hive without opening it: a nectar flow
adds a kilogram or two a day, a robbing event drops weight visibly
inside an hour, and winter clusters chew through stores at a
predictable rate.

Four load cells under the corners of the hive stand form a **Wheatstone
bridge**, one leg per cell. This averages out uneven weight distribution
(off-center supers, one leg on a rock) and effectively multiplies the
sensitivity by 4. A single HX711 24-bit ADC digitizes the bridge output.

The HX711's timing is bit-banged in software on the Pico (see
`firmware/pico/drivers/hx711.py`). This is why it gets its own two GPIO
pins (`GP18` for DOUT, `GP19` for SCK, from `config.py:29-30`) — no I²C,
no SPI, just DOUT-ready-low + SCK-clock-out-24-bits.

## Parts checklist

- **4× 50 kg half-bridge load cells** (the small bars with a
  strain-gauge foil in the middle). Sold as a kit with the HX711 and
  usually a combinator board.
- **HX711 breakout** — SparkFun #13879 or the kit's included board.
  The kit board is fine for beekeeping; the SparkFun one has a
  better ground plane.
- **Combinator board** (optional but recommended). Small PCB that
  wires the four half-bridges into a single full Wheatstone. Comes
  with most 4-cell kits. If yours didn't include one, follow SparkFun's
  guide: https://learn.sparkfun.com/tutorials/load-cell-amplifier-hx711-breakout-hookup-guide
- **CAT6 F/UTP** (foil + drain wire) cable, ~2 m. This carries the
  HX711 signals from the hive stand back to the electronics box. Do
  NOT use ribbon or unshielded wire for this run — HX711 is
  microvolt-sensitive.
- **22 AWG silicone stranded** for the HX711 → Pico jumpers.
- **Hive stand base plate** — 3/4" plywood cut to hive footprint plus
  ~5 cm all around, or an aluminum plate if you're feeling fancy.
- **Top platform** — same size as base, will hold the actual hive.
  Plywood or plastic composite. Do not put the hive directly on the
  load cells; they need the platform above them to spread the load.
- **4 machine screws / washers / nuts** to bolt each load cell between
  the base and the top platform — usually M6 × 20 mm for the standard
  50 kg cells.

## Wiring — load cells to combinator

Each of the four load cells has **3 wires** (some kits: 4 wires with
one being a bare shield — ignore the shield for now).

| Load cell wire | Signal |
|---|---|
| **Red** | E+ (bridge excitation +) |
| **Black** | E− (bridge excitation −) |
| **White** or **green** | S+ or S− (signal, one of the two arms) |

Each individual cell is a **half-bridge** — the strain-gauge foil is
one arm and there's an internal reference arm. To form a full bridge
from 4 half-bridges, wire diagonally-opposite cells to be the
"upper" and "lower" arms:

```
                          E+  (red)
                           │
              ┌────────────┼────────────┐
              │            │            │
        Cell 1 (LF)                Cell 3 (RB)
              │                         │
              ├───────── S+ (white) ────┤
              │                         │
        Cell 2 (RF)                Cell 4 (LB)
              │            │            │
              └────────────┼────────────┘
                           │
                          E−  (black)
```

Where LF/RF/LB/RB = the four corners of the stand (Left Front, Right
Front, Left Back, Right Back). The **combinator board** does this
wiring for you — every cell's red goes to one screw terminal, every
cell's black to another, and the whites/greens split into two S+
and S− terminals following the diagonal rule.

**If you skip the combinator board and hand-wire it:** double-check
the diagonal pattern before applying weight. A wrong-diagonal wiring
produces near-zero output regardless of load, and you'll spend an
afternoon wondering why.

## Wiring — combinator to HX711

| Combinator output | HX711 pin |
|---|---|
| E+ | E+ |
| E− | E− |
| S+ | A+ (or A−, both work — swap if the sign is inverted at calibration) |
| S− | A− |

Leave B+/B− on the HX711 unconnected. Channel B is a secondary input
with fixed gain 32 and isn't used here.

## Wiring — HX711 to Pico

| HX711 pin | Pico pin | Physical Pico pin | Wire color |
|---|---|---|---|
| VCC | **3V3_OUT** | pin 36 | orange |
| GND | GND | any GND | black |
| DT (DOUT) | GP18 | pin 24 | white |
| SCK | GP19 | pin 25 | grey |

**Do not** power the HX711 from VBUS/5V, even though the datasheet
says it can take up to 5.5 V. On the Pico, the ADC reference and DOUT
levels are 3.3 V — powering the HX711 from 5 V puts 5 V on DOUT which
is over the Pico's Vih spec and will slowly stress the pin (and can
sometimes latch). **3.3 V power = 3.3 V I/O**, exactly what you want.

Pin values are enforced by `firmware/pico/config.py:29-30`:

```python
HX711_DOUT = 18
HX711_SCK = 19
```

## Cable — HX711 to the hive stand

At the hive, you want ~1-2 m of cable between the HX711 (in the
electronics box) and the combinator on the stand.

**Use CAT6 F/UTP** (foiled twisted pair). Assign pairs like this:

| CAT6 pair | Signal | Note |
|---|---|---|
| Orange pair | E+ / E− | Excitation is DC — twisted for common-mode noise |
| Green pair | S+ / S− | Signal is microvolts — this pair benefits most from being twisted |
| Blue pair | VCC / GND to combinator (if you power it locally) | Otherwise unused |
| Brown pair | Spare / signal ground | Tie to GND at the HX711 end only |

**Foil shield + drain wire → HX711 GND at the HX711 end only.** Do NOT
also ground the shield at the combinator end. Ground-loop currents
along the shield show up as noise in the HX711 reading.

Keep the run under 2 m if possible. Every additional meter adds noise
you'll spend calibration time fighting.

> **📷 Photo needed:** the combinator board mounted on the stand base
> with the 4 cell wires terminated, plus the CAT6 pigtail heading
> back to the electronics box.

## Step 1 — Bench-wire everything, no weight yet

1. Unplug the Pico from USB.
2. Wire the HX711 breakout to the Pico per the table above.
3. Wire the combinator (or hand-wired bridge) to the HX711 with short
   jumpers. Don't build the physical stand yet — we're proving the
   electronics first.
4. Plug the Pico back into the Pi's USB.

Boot log:

```
# hx711 ready
```

If it says `hx711 init failed`, the driver couldn't get a first read
within the 100 ms timeout at `hx711.py:23`. Most common: DOUT/SCK
swapped, or GND not actually connected.

## Step 2 — Confirm the raw reading responds to force

The Pico is publishing `w_kg` in every packet, but with the default
`HX711_SCALE = 1.0` and `HX711_TARE_OFFSET = 0` (`config.py:32-33`),
that number is meaningless — it's the raw ADC value times 1.0.

Watch it change as you flex a cell. From your laptop:

```bash
mpremote connect /dev/ttyACM0
```

Note the current `w_kg` value. Press down on ANY of the four load
cells with your finger. `w_kg` should change — usually by hundreds of
thousands (raw units).

- **No change at all** — HX711 sees the bridge but the bridge isn't
  outputting anything. Most likely the diagonal wiring is wrong, or
  one E+/E− lead is disconnected.
- **Wildly bouncing value** — no shielded cable, or a cell is
  physically loose in its mounting.
- **Change is very small (< 1000 raw)** — one or more cells is
  mis-wired (contribution cancels rather than adds). Swap the
  polarity of one of the S connections.

Good news if you see the raw values move — the electronics are sound
and it's now a mechanical problem, not an electrical one.

## Step 3 — Build the physical stand

1. Mount each load cell to the base plate. The cell has two threaded
   holes on **one end** — that end is the fixed end, bolted to the base.
2. The **other end** of each cell (with two threaded holes on the
   opposite face) is the moving end. Bolt the top platform to this
   end.
3. Between base and top platform: only the four load cells make
   contact. There must be a small **air gap** (2-5 mm) between the
   top platform and the base plate everywhere else, so that all load
   travels through the cells.

**Common mechanical mistake:** the top platform rests on the base at
some point (a warped board, a bolt head, a rubber foot). Any bypass
path steals load from the cells and gives you inconsistent readings.
Check with a sheet of paper — you should be able to slide it under
the top platform anywhere in the gap.

> **📷 Photo needed:** side view of the assembled stand showing the
> air gap between base and top platform, with a corner load cell
> visible.

## Step 4 — Tare the stand (empty, before any weight)

Once the stand is fully assembled and empty:

1. From your laptop:

   ```bash
   mpremote connect /dev/ttyACM0
   ```

2. In another terminal, send the tare command. Easiest way:

   ```bash
   echo '{"cmd":"tare"}' > /dev/ttyACM0
   ```

   Or from an active `mpremote` REPL:

   ```python
   >>> import sys
   >>> sys.stdout.write('{"cmd":"tare"}\n')
   ```

3. The boot-log stream will print:

   ```
   # tare set to <some big number>
   ```

   The number is the current raw ADC reading — that's now defined as
   "zero kg". Note it down.

4. Subsequent `w_kg` values in the JSON packets will now hover near 0
   (in raw units × current scale = 1.0, so still meaningless
   magnitude, but should sit near zero).

**Save the tare value to `config.py`** so it survives reboots. Edit
`firmware/pico/config.py:32`:

```python
HX711_TARE_OFFSET = 12345678   # your value from the log
```

Re-copy config:

```bash
cd firmware/pico
mpremote connect /dev/ttyACM0 cp config.py :
mpremote connect /dev/ttyACM0 reset
```

## Step 5 — Calibrate with a known weight

1. Place your reference weight (10 kg) in the center of the top
   platform. Distribute it evenly if it's several items.
2. Watch a few JSON packets and note the reported `w_kg`. Since scale
   is still 1.0, this will be a large raw-unit number like `183472.5`.
3. Compute the calibration factor:

   ```
   new_scale = 10.0 / current_reported_w_kg
   ```

   Example: if the reported reading is `183472.5`, then
   `new_scale = 10.0 / 183472.5 = 0.0000545` (or `5.45e-5`).

4. Send the calibrate command:

   ```bash
   echo '{"cmd":"calibrate","cal":0.0000545}' > /dev/ttyACM0
   ```

   (Substitute your actual value.)

   Log:

   ```
   # scale set to 5.45e-05
   ```

5. Verify: the next JSON packets should now report `w_kg` at very
   close to `10.0`. Remove the weight — should drop to near 0. Add
   the weight back — should return to ~10.0.

6. **Save the scale to `config.py`** so it survives reboots. Edit
   `config.py:33`:

   ```python
   HX711_SCALE = 5.45e-05        # from calibration
   ```

   Re-copy and reset:

   ```bash
   mpremote connect /dev/ttyACM0 cp config.py :
   mpremote connect /dev/ttyACM0 reset
   ```

## Step 6 — Verify from the Pi side

From the Pi (SSH):

```bash
sudo sqlite3 /var/lib/beehive/hive.db \
  "SELECT ts, w_kg FROM readings WHERE w_kg IS NOT NULL
   ORDER BY ts DESC LIMIT 5;"
```

Recent rows should show `w_kg` matching whatever you have on the
platform right now.

## Step 7 — Sanity check under real hive weight

If you have an empty hive body / boxes / frames, stack them on the
platform:

- Empty single-medium (10 frames, no bees, no honey): ~15 kg.
- Empty deep + medium (20 frames): ~25-30 kg.
- Full deep + medium in mid-summer with bees + honey: 40-60 kg.

Anything wildly off (reading half, double, or negative) means you
have a physical bypass path stealing load, or you calibrated with
weight only in one corner. Re-check the mechanical assembly.

## Success check for this phase

- [ ] `# hx711 ready` in the boot log.
- [ ] Pressing on the empty platform noticeably moves the `w_kg`
      value in the JSON stream.
- [ ] The 4-cell diagonal is wired correctly (verified in Step 2).
- [ ] Physical stand has a real air gap between base and top
      platform everywhere except at the cell mounts.
- [ ] `HX711_TARE_OFFSET` and `HX711_SCALE` are set in
      `config.py` and survive a reboot.
- [ ] Placing the reference weight gives a reading within ±0.05 kg of
      the true value.
- [ ] Removing the reference weight returns to ≤ ±0.02 kg of zero
      within a few packets.
- [ ] SQL query on the Pi returns fresh `w_kg` values.

Move on to Phase 08 (bee gate) once the weight sensor is verified.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `hx711 init failed: HX711 not ready` | DOUT/SCK wiring — check they're on GP18/GP19 not swapped, and both connected. Also check power (VCC=3V3, not floating). |
| Raw value drifts by tens of thousands even under stable load | Cable isn't shielded, or shield is grounded at both ends (ground loop). Use CAT6 F/UTP with drain wire tied to HX711 GND only. Keep the run < 2 m. |
| Raw value increases when you press one corner but decreases when you press the opposite | S+/S− swapped on one of the diagonals. Swap the wiring at the combinator or at the HX711's A+/A−. |
| Reading is very noisy but the mean is right | Increase `HX711_SAMPLES` in `config.py:34` from 5 to 10. Median-of-N takes longer per packet but rejects more spikes. |
| Value creeps upward or downward slowly with no weight change | Thermal drift — the load cells are temperature-sensitive (up to a few 100 g per 10 °C). Recalibrate seasonally if you care about ±50 g accuracy. In practice for beekeeping, daily deltas matter more than absolute accuracy. |
| Value jumps by hundreds of kg momentarily | Nearby motor / relay / big load switching creating EMI. Ferrite bead on the CAT6 near the HX711 helps. Or move the electronics box further from the noise source. |
| Reading is exactly half of what it should be | You have one cell disconnected (open circuit) — the remaining 3 form an unbalanced bridge that outputs roughly half. Check every cell's continuity with a DMM. |
| Reading is negative when weight is added | Perfectly valid — the bridge output polarity is arbitrary. Either swap S+/S− at the HX711, or make `HX711_SCALE` negative. |
| Stand reads correctly with 10 kg in the center but wildly with 10 kg in one corner | Non-linearity from a stuck / warped stand. Verify air gap everywhere in the stand (the paper-slide test). |

## What NOT to do

- **Do not** put the hive directly on the load cells. They need a
  spreader platform above them to distribute load, and the platform
  itself must not touch the base except through the cells.
- **Do not** overload the cells. 4× 50 kg = 200 kg theoretical, but
  practical limit is ~150 kg to leave safety margin (a rowdy bear or
  a stormy day could momentarily double the load). If you're running
  giant super stacks, spec 100 kg cells and start over.
- **Do not** use unshielded cable. HX711 is microvolt-sensitive; even
  a 30 cm unshielded run picks up enough noise to give you ±0.5 kg
  jitter.
- **Do not** power the HX711 from 5 V. See Step 1's note.
- **Do not** try to calibrate with weight in only one corner. Center
  the reference weight so all four cells share it. Corner-only
  calibration bakes in the leverage error and produces bad readings
  under real-world loading.
- **Do not** recalibrate every time the reading changes. Weight
  changes are usually real (nectar flow, evaporation, feeding). Only
  recalibrate seasonally, or after any physical disturbance of the
  stand.
