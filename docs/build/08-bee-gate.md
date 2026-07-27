# Phase 08 — Bee-gate IR array (entrance activity counter)

Goal at end of phase: an 8-tunnel entrance restrictor with two IR
slotted-optical sensors per tunnel (16 phototransistors total)
mounted at the hive entrance, wired to Pico GP0-GP15, with counts of
inbound / outbound / ambiguous bee crossings appearing in every JSON
packet.

Time: about 3-4 hours if you're printing the body yourself, plus
however long your printer takes. Wiring the 16 phototransistors is
the tedious part — expect a full evening.

## Prereqs

- Phase 07 done (you're through all the "one sensor at a time" phases
  and are comfortable with the config + boot-log workflow).
- Access to a **3D printer** capable of ASA or PETG. See "Body
  fabrication" below for alternatives if you don't.

## How it works

Each of the **8 tunnels** in the gate is just wide enough for one bee
to pass through at a time. Inside each tunnel, two **slotted
optical interrupters** (ITR9606) are mounted a few mm apart along the
tunnel axis:

- **Beam A** is the outer beam (nearer the outside world).
- **Beam B** is the inner beam (nearer the hive interior).

When a bee walks through the tunnel:

- Going **into** the hive: it breaks A first, then B → `bees_in += 1`.
- Coming **out** of the hive: it breaks B first, then A → `bees_out += 1`.

If only one beam trips and no partner event comes within 500 ms, the
crossing is `bees_ambiguous`. This handles bees that turn around
mid-tunnel, hover partway through, or shuffle in tight groups. The
direction inference lives in `firmware/pico/drivers/bee_gate.py`.

Beams that stay blocked for over 2 seconds (`config.py:52` —
`BEE_GATE_STUCK_TIMEOUT_MS = 2000`) are assumed to be a loitering bee
and silently disarmed until they clear — no phantom events.

See the SVG diagram at [`../../diagrams/bee-gate.svg`](../../diagrams/bee-gate.svg)
for the physical layout.

## Pin assignments (from `firmware/pico/config.py:48-49`)

```python
BEE_GATE_BEAM_A_PINS = [0, 1, 2, 3, 4, 5, 6, 7]     # outer beam per tunnel
BEE_GATE_BEAM_B_PINS = [8, 9, 10, 11, 12, 13, 14, 15]  # inner beam per tunnel
```

| Tunnel | Beam A (GP) | Beam B (GP) |
|---|---:|---:|
| 1 | 0 | 8 |
| 2 | 1 | 9 |
| 3 | 2 | 10 |
| 4 | 3 | 11 |
| 5 | 4 | 12 |
| 6 | 5 | 13 |
| 7 | 6 | 14 |
| 8 | 7 | 15 |

Sixteen phototransistor inputs on GP0-GP15. The 16 IR LEDs are all
driven from 3V3 through per-emitter current-limit resistors — the LEDs
do not need a GPIO each.

## Parts checklist

- **16× Everlight ITR9606-F** slotted opto-interrupters. **DigiKey or
  Mouser** — do not buy AliExpress unbranded; the knockoffs have
  higher forward voltage on the LED and drift more with temperature.
- **16× 220 Ω resistors** — current-limit for the IR LEDs.
- **16× 10 kΩ resistors** — pull-ups for the phototransistor
  collectors.
- The **ALLECIN 50-value resistor kit** in the BOM has plenty of both.
- **~2 m of ribbon cable** or a bundle of 22 AWG solid-core wire —
  the 16 signal returns and 16 LED wires plus power/GND add up to a
  lot of conductors from the gate to the Pico.
- **3D-printed gate body** (see below) — the mechanical enclosure that
  holds the 16 ITR9606s and creates the 8 tunnels.
- **Neutral-cure silicone RTV** for potting the ITR9606s into their
  slots on the printed body (not acetoxy — bees hate the smell).

## Body fabrication

The gate body is a 3D-printed part sized to fit over your **entrance
reducer** (or replace it entirely) on a standard Langstroth hive.

**Design constraints:**

- 8 tunnels, each **8 mm wide × 8 mm tall × 30 mm deep**.
- Each ITR9606's 5 mm slot straddles the tunnel — the tunnel wall
  passes through the slot with ~1.5 mm clearance on each side.
- Two ITR9606s per tunnel, ~8 mm apart along the tunnel length.
- Slide-out tray on the bottom so you can clean propolis off the
  sensors periodically.

**Material — ASA or PETG only.** Not PLA. PLA warps at ~50 °C which
is easily hit by summer sun on a dark surface, deforming the tunnels
and jamming beams. ASA and PETG are both dimensionally stable to
~70-80 °C.

**If you don't have a printer** — the STL file lives in
`hardware/` (add one if you don't see it — this is a hobby-hardware
project and the STL is user-contributed). Alternatives:

- **Print via a service** — Shapeways, Hubs, or your local hackerspace.
  Cost: about $30-40 for the small print in ASA.
- **Build from acrylic** — laser-cut 3 mm black acrylic sheets stacked
  and glued. More work but doable in a hackerspace.
- **Skip fewer tunnels** — for a first prototype, a 4-tunnel version
  is legitimate. Edit `config.py` to have 4-element lists instead of
  8, wire only GP0-GP3 and GP8-GP11. Half the counts, but proves the
  concept.

> **📷 Photo needed:** the printed body with tunnels visible from
> above and the ITR9606 slots visible from the side. Include a coin
> for scale.

## Wiring one ITR9606

The ITR9606 is a slotted optical interrupter — one side is an IR LED,
the other side is a phototransistor. The datasheet:
https://www.everlight.com/file/ProductFile/ITR9606-F.pdf

Pinout (from the datasheet, looking at the sensor with the slot
facing away):

| Pin | Function |
|---|---|
| 1 | LED anode |
| 2 | LED cathode |
| 3 | Phototransistor collector |
| 4 | Phototransistor emitter |

Per-sensor wiring:

```
                              3V3
                               │
                          ┌────┴────┐
                       [220 Ω]  [10 kΩ]
                          │         │
                          ▼         │
          Pin 1 ──[LED]── Pin 2     ├──── to Pico GPn
                          │         │
                         GND    Pin 3 ── Pin 4
                                          │
                                         GND
```

- **LED path:** 3V3 → 220 Ω → Pin 1 → LED → Pin 2 → GND.
- **Sense path:** 3V3 → 10 kΩ → Pin 3 (collector) → (through
  phototransistor) → Pin 4 → GND. Tap between the 10 kΩ and Pin 3 →
  goes to the Pico GPIO.
- Beam **unbroken** = phototransistor conducting = Pin 3 pulled low
  → Pico reads **LOW** (0).
- Beam **broken** = phototransistor open = Pin 3 pulled high by 10 kΩ
  → Pico reads **HIGH** (1).

Wait — the driver at `bee_gate.py:71-72` treats **falling edge as
beam-break**. That's the opposite of what the wiring above produces.
Let me correct: the driver assumes **HIGH = unbroken, LOW = broken**
(`_Beam.last_state = 1` initial, "beam just broke" = `state == 0`).
That means the correct wiring is:

- Beam **unbroken** = phototransistor conducting = Pin 3 pulled toward
  Vcc (**HIGH**) through the phototransistor (Pin 4 tied to Vcc via
  the 10 kΩ arrangement won't work — we need to flip it).

Corrected per-sensor wiring:

```
                              3V3
                               │
                          ┌────┴────┐
                       [220 Ω]   Pin 3 (collector)
                          │         │
                          ▼         │
          Pin 1 ──[LED]── Pin 2     │
                          │         │
                         GND    Pin 4 ── to Pico GPn
                                          │
                                       [10 kΩ]
                                          │
                                         GND
```

- **LED**: 3V3 → 220 Ω → Pin 1 → LED → Pin 2 → GND.
- **Phototransistor as an emitter-follower**: 3V3 → Pin 3 (collector).
  Pin 4 (emitter) → 10 kΩ pull-**down** to GND → Pico GPIO.
- Beam **unbroken** (light through) = phototransistor conducts = Pin 4
  pulled high by the collector = Pico reads **HIGH**.
- Beam **broken** (no light) = phototransistor off = Pin 4 held low
  by the 10 kΩ = Pico reads **LOW**. **Falling edge = beam break**,
  matching the driver.

Verify this on one sensor before you build all 16 — see Step 2.

## Step 1 — Prototype one channel on a breadboard

Before committing to 16 sensors:

1. Unplug the Pico.
2. Wire **one ITR9606** on a breadboard per the "corrected per-sensor
   wiring" above. Use tunnel 1 pinout: Beam A output → **GP0**.
3. Plug the Pico back in.

## Step 2 — Verify the one channel works

Open a monitor:

```bash
mpremote connect /dev/ttyACM0
```

Boot log should say `# bee_gate ready (8 channels)` — the driver
comes up even with only one sensor wired; the other 15 will just
report as continuously broken (LOW).

To test the wiring polarity, drop into REPL:

```bash
mpremote connect /dev/ttyACM0 repl
```

Then:

```python
>>> from machine import Pin
>>> beam_a1 = Pin(0, Pin.IN, Pin.PULL_UP)
>>> beam_a1.value()
1              # slot unobstructed = LED shines on phototransistor = HIGH
>>> # Now slide a piece of paper into the ITR9606 slot to block the beam:
>>> beam_a1.value()
0              # LOW when blocked = correct wiring
```

If you see the opposite (0 unobstructed, 1 blocked), you wired the
phototransistor as a common-emitter (Vcc → 10 kΩ → collector, emitter
→ GND). Swap the emitter and collector arrangement per the corrected
diagram.

Ctrl-X to exit the REPL.

Watch the JSON packets now. Wave your finger through the slot a few
times:

```json
{"t": 1234, ..., "bees_in": 0, "bees_out": 0, "bees_ambiguous": 3}
```

`bees_ambiguous` should increment for single-beam trips (you only have
Beam A wired so far, no direction pair possible). If those counts move,
the beam is detecting.

## Step 3 — Wire beam B for channel 1

1. Unplug Pico.
2. Wire a second ITR9606 to **GP8** (Beam B for tunnel 1).
3. Plug in.

Now sweep your finger through both slots from outside to inside (A
first, then B), taking ~200 ms total. Then from inside to outside
(B first, then A).

```json
{"t": 1234, ..., "bees_in": 2, "bees_out": 1, "bees_ambiguous": 0}
```

Two full-direction crossings recognized. If instead the counts always
go into `bees_ambiguous`, either your sweep is too slow (> 500 ms
between beams — outside the window), or your two beams are wired to
the wrong pins.

## Step 4 — Build out all 16 channels

Two schools of thought here:

**a) Repeat the breadboard proof for each pair.** Slow but low-risk.
Wire channel 2 (GP1 + GP9), verify, then channel 3, etc. Each pair
should show `bees_in` / `bees_out` incrementing when you finger-sweep
the pair.

**b) Build the whole 16-channel array on a proto-PCB or point-to-point
solder, then debug.** Faster mechanically, but a mis-wire is much
harder to find.

Regardless of which, the wiring **per channel** is identical to Step 1:

- Each channel's LED: 3V3 → 220 Ω → LED anode → LED cathode → GND.
- Each channel's phototransistor: 3V3 → collector; emitter → 10 kΩ
  → GND, with the tap going to the assigned GPIO.

The 16 LEDs can share a common 3V3 supply — total current draw is
~30 mA (16 × ~2 mA per LED at 220 Ω from 3V3). Well within the
Pico's 3V3_OUT capability.

**Labeling saves your sanity.** As you wire each pair, label both the
IR LED and the phototransistor pins on the ITR9606 with the channel
number and A/B side. Sharpie on masking tape works.

## Step 5 — Mount the ITR9606s in the printed body

1. Slot each ITR9606 into its printed pocket. The pocket dimensions
   in the STL are sized for a snug press-fit — don't force it, warm
   the plastic gently with a hair dryer if it's tight.
2. Confirm the tunnel wall passes through the 5 mm slot with clearance
   on both sides. If the wall is too thick, the sensor won't sit; if
   too thin, the beam floods around it.
3. Once seated, add a small dab of **neutral-cure silicone RTV** at
   each ITR9606's base to hold it in place. Do not cover the slot —
   propolis will find any exposed glue and glue up your sensors.
4. Route each channel's 4-wire tail out the back of the body toward
   your wiring bundle.

> **📷 Photo needed:** all 16 ITR9606s mounted in the gate body with
> their tail wires bundled toward the wiring exit.

## Step 6 — Full-array verification with a toothpick

Before the gate ever sees a bee:

1. Plug the Pico into the Pi's USB.
2. Watch the JSON stream on the Pi:

   ```bash
   sudo tail -f /var/log/beehive-ingest.log
   ```

   (Or `sudo journalctl -u beehive-ingest -f`.)

3. Use a **toothpick** to sweep each tunnel:
   - Outside → inside (A then B) — should increment `bees_in`.
   - Inside → outside (B then A) — should increment `bees_out`.

4. Repeat for every tunnel. Any tunnel that always reports
   `ambiguous` — one of its two beams isn't detecting. Swap the
   toothpick for a slower sweep and watch which pin toggles in the
   REPL to isolate the failing sensor.

## Step 7 — Adjust timing for your bees (optional)

The defaults (`config.py:50-52`):

```python
BEE_GATE_DIRECTION_WINDOW_MS = 500   # A-then-B must arrive within 500 ms
BEE_GATE_DEBOUNCE_MS = 5
BEE_GATE_STUCK_TIMEOUT_MS = 2000
```

If you get lots of ambiguous events during a real observation:

- **Increase `DIRECTION_WINDOW_MS`** to 800 or 1000 for slow bees in
  cool weather. Bees walk slower when it's under about 15 °C.
- **Decrease `DEBOUNCE_MS`** to 2 or 3 if fast-moving bees are being
  filtered out. Below 2 ms, beam noise starts producing false
  triggers.

Edit `config.py`, re-copy with `mpremote`, reset.

## Success check for this phase

- [ ] All 16 ITR9606s mounted in the body, wired to GP0-GP15
      correctly (A on GP0-7, B on GP8-15).
- [ ] Each beam reads **HIGH when unobstructed**, **LOW when
      blocked** (falling edge = beam break).
- [ ] Toothpick outside→inside sweep on each tunnel increments
      `bees_in`.
- [ ] Toothpick inside→outside sweep on each tunnel increments
      `bees_out`.
- [ ] `bees_ambiguous` stays low (< 20 % of total events) during
      normal test sweeps.
- [ ] SQL query returns fresh counts:
      ```bash
      sudo sqlite3 /var/lib/beehive/hive.db \
        "SELECT ts, bees_in, bees_out FROM readings ORDER BY ts DESC LIMIT 5;"
      ```

The bee gate itself sits at the hive entrance — physical installation
happens in Phase 13. For now, keep the assembled gate on the bench
and let it run so you can validate counts against visual observation
once installed.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `# bee_gate ready (8 channels)` but no counts ever from any tunnel | LED current-limit resistor value wrong (used 22 kΩ instead of 220 Ω, drops LED current by 100×). Sensor doesn't see the LED at all. Verify with DMM: voltage across 220 Ω resistor should be ~1.5-1.7 V. |
| One tunnel always shows `ambiguous` | One of its two beams isn't producing a falling edge. Isolate in REPL: `Pin(N, Pin.IN, Pin.PULL_UP).value()` should change when you block the slot. |
| All tunnels always show `ambiguous` | Direction window too short — try 800 ms. Or beams are physically too far apart on your printed body (bees can't span both in 500 ms). |
| Random counts appearing when nothing's in the gate | Ambient IR (sunlight) flooding the ITR9606. Cover the gate with a shade or add a lens hood over the LED side. |
| Counts show `bees_in` when you sweep from inside-to-outside (direction inverted) | You wired A and B swapped for that tunnel — swap the GPIOs at the Pico end. |
| First tunnel works, tunnel 8 doesn't | Voltage drop along your 3V3 supply run — the 16 LEDs share power and the end of the chain sees less voltage. Solve with heavier gauge for the 3V3 rail (14 AWG), or run parallel supply drops from the Pico. |
| Weird intermittent counts on hot days | Phototransistor thermal drift or PLA-warped body. If the body is PLA, reprint in ASA/PETG. If ASA/PETG, add small shade cover. |
| Body doesn't fit the entrance reducer | Every hive supplier's "standard" is different by 1-2 mm. Measure yours and rescale the STL before printing. |

## What NOT to do

- **Do not** print the body in PLA. It will warp in the sun and
  wreck the tunnel geometry.
- **Do not** connect the ITR9606 LED directly to 3V3 with no current
  limit — the LED forward current will exceed the datasheet and it
  will fail within days.
- **Do not** run 30 cm+ of unshielded wire between the phototransistor
  and the Pico for a hive-installed setup. If your electronics box is
  more than ~40 cm from the gate, use twisted-pair or a small
  differential-line driver at the gate end.
- **Do not** use acetoxy-cure ("bathroom") silicone for potting.
  Neutral-cure only. Bees will not forgive the acetic-acid outgassing.
- **Do not** skip the toothpick test. Doing the first real bee test
  at the hive with an untested gate wastes a whole day's worth of
  data.
- **Do not** overreact to the counts. Bees do weird things — 100 bees
  can leave in a burst and 10 minutes later 300 arrive. `bees_in −
  bees_out` isn't the colony size, and treating it as such will
  drive you crazy.
