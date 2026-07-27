# Phase 06 — DS18B20 1-Wire temperature array

Goal at end of phase: four DS18B20 waterproof stainless probes on a
single-wire bus, each enumerated by its ROM address and mapped to a
human-readable label (`top_cover`, `above_brood`, `brood_side`,
`entrance`), all four temperatures appearing in every JSON packet.

Time: about 1 hour, plus however long you spend deciding where each
probe goes in the hive (do that thinking now — labels are annoying to
change later).

## Prereqs

- Phase 05 done (I²C sensors work, so you know the general "one at a
  time, verify" rhythm).

## Why 1-Wire (and not four ADC channels)

1-Wire lets **all four probes share a single data pin** plus power and
ground. Each probe has a factory-burned 64-bit ROM address, so the
driver can address them individually on a shared bus. That means one
cable run from the Pico to a junction near the hive, and four short
probe cables branching off. Much easier to install and re-route than
four separate wires back to the Pico.

The tradeoff: read latency. A 12-bit conversion takes ~750 ms per
probe. The driver hides this by triggering all four to convert in
parallel (`drivers/ds18b20.py:34-35`) and reading them out afterwards
— so total array read is ~800 ms, not 3 seconds. Firmware runs this on
the slow-sensor cadence (5 s default, `config.py:56`).

## Parts checklist

- **4× DS18B20 waterproof stainless probes**, 1 m cable each. Any
  major distributor's kit (Adafruit #381 or Amazon multipack). Confirm
  they're the **waterproof stainless probes**, not bare TO-92 chips —
  a bare chip inside a hive will not last one season.
- **1× 4.7 kΩ resistor** for the pull-up. From the ALLECIN resistor
  kit in the BOM.
- **A junction / crimp block** for wiring the four probes together
  onto one bus. Options:
  - Small terminal block (WAGO 221 lever nuts work great)
  - Solder + heatshrink into a small potted junction
  - A tiny PCB with four sets of probe pads and one bus pad
- Same 22 AWG silicone wire from Phase 05 for the run from Pico to the
  junction (purple for 1-Wire data per the color convention in
  `docs/hardware.md`).

**Probe wire colors (usually):**

| Wire | Meaning |
|---|---|
| Red | VDD (3.3 V) |
| Yellow | DQ (data) |
| Black | GND |

**Watch out:** cheap probes vary. Some kits ship red/**white**/black.
Some ship red/yellow/black. **Check with a DMM** in continuity mode
before wiring — probe the stainless tip to each wire; the wire that
beeps is GND (the tip is grounded on almost every waterproof probe).
Data and VDD you have to identify by process of elimination from the
datasheet — safer to buy from a reputable seller that documents the
color scheme.

## Wiring

One bus, all four probes in **parallel**:

```
              3V3_OUT (Pico pin 36)
                        │
                        ├─────────────── all 4 probe REDs (VDD)
                        │
                     [4.7 kΩ]
                        │
              GP22 ─────┴─────────────── all 4 probe YELLOWs (DQ)
                                          (bus data line)

              GND ────────────────────── all 4 probe BLACKs
```

- **Data**: all four yellow wires tied together, going to Pico **GP22**.
- **Pull-up**: 4.7 kΩ between GP22 and 3V3. **Exactly one pull-up on the
  whole bus** — not one per probe.
- **Power**: all four red wires tied together, going to Pico 3V3_OUT.
- **Ground**: all four black wires tied together, going to any Pico GND.

The junction where the four probe wires meet can be a WAGO lever nut
set (nice for reconfiguration), a small terminal block, or a soldered
potted junction (permanent but reliable). For bench testing use WAGOs;
for the field build in Phase 12 you'll want soldered + heatshrunk.

Pin reference (from `firmware/pico/config.py:17`):

```python
ONEWIRE_PIN = 22
```

Do not change this without also updating the config.

> **📷 Photo needed:** the four probes joined at the junction with the
> 4.7 kΩ pull-up visible, so builders can compare their assembly to a
> known-good one.

## Step 1 — Wire it up

1. Unplug the Pico from USB.
2. Build the junction: all four REDs together, all four YELLOWs
   together, all four BLACKs together.
3. Run three wires from the junction back toward the Pico: red/orange
   (VDD), purple (DQ), black (GND).
4. At the Pico end:
   - VDD wire → 3V3_OUT (pin 36).
   - DQ wire → GP22 (pin 29).
   - GND wire → any GND pin.
5. Add the **4.7 kΩ resistor** between the DQ wire and the 3V3_OUT
   wire, as close to the Pico as convenient. This is the bus pull-up.
6. Confirm with DMM before powering up:
   - VDD wire to GND wire: OPEN (∞). If short — you have a wiring
     error; do not power up.
   - VDD wire to DQ wire: ~4.7 kΩ (via your pull-up resistor).
   - DQ wire to GND: OPEN (∞) unless a probe is holding the line low
     (rare at rest).
7. Plug the Pico back into the Pi's USB.

## Step 2 — Verify the probes are seen

Boot log:

```
# ds18b20: 4 probes
```

If it says `1 probes` or `0 probes`, the bus is only seeing some of
them — reseat every junction and retry. See Troubleshooting below.

## Step 3 — Enumerate the ROM addresses

You need each probe's unique 64-bit ROM address so you can label
which physical probe is which.

From your laptop:

```bash
mpremote connect /dev/ttyACM0 exec "
from drivers.ds18b20 import DS18B20Array
d = DS18B20Array(22)
print(d.rom_list())
"
```

Expected output — a list of 4 hex strings, each 16 chars long:

```
['28ff64...abcdef', '28ff64...123456', '28ff64...deadbe', '28ff64...cafeba']
```

Every DS18B20 ROM starts with `28` (that's the family code). If you
see something that doesn't start with `28`, you have a counterfeit or
a different sensor family entirely.

Copy those 4 strings somewhere you can find them again.

## Step 4 — Physically identify each probe

You have 4 anonymous probes and 4 anonymous ROM addresses. To pair
them, warm each probe individually and see which reading changes.

From the laptop, in a shell that will re-poll:

```bash
mpremote connect /dev/ttyACM0 exec "
from drivers.ds18b20 import DS18B20Array
import time
d = DS18B20Array(22)
for _ in range(30):
    print(d.read_all())
    time.sleep(2)
"
```

This prints all 4 probes' temperatures every ~2 seconds for 60 seconds.

While that's running:

1. Pick up **one probe**. Warm it in your hand for 15-20 seconds. Note
   which ROM address shows the temperature climbing (should go from
   room temp into the mid-30s °C).
2. **Label it physically** — masking tape near the connector end
   works; permanent marker on the probe cable near the joint is
   better. Give it its intended role: `top_cover`, `above_brood`,
   `brood_side`, or `entrance`.
3. Let it cool. Repeat with the next probe.
4. Repeat until all four are labeled.

Record which ROM address → which physical role. You'll need this
mapping in the next step.

### Where each probe should physically go in the hive

| Label | Position | Purpose |
|---|---|---|
| `top_cover` | Under the outer cover, just above the inner cover. | Attic temperature — early-warning for insulation problems in winter, ventilation problems in summer. |
| `above_brood` | Threaded through the inner cover hole, hanging ~1 cm above the top bars of the brood box. | Cluster temp — the number a beekeeper cares about most. |
| `brood_side` | Between two brood-box frames near the outside edge (e.g. between frames 1 and 2 in a 10-frame). | Detects cluster movement across seasons. |
| `entrance` | Just inside the entrance reducer, out of direct sun. | Approximate outside temperature at hive level (independent from the BME280 which is on a mast). |

Route the probe cables in through the inner cover and secure with the
neutral-cure silicone from the BOM (**not** acetoxy — that outgasses
acetic acid, bees will resent you).

## Step 5 — Update `config.py` with the labels

Now the fiddly bit. The firmware wants `DS18B20_LABELS` as a dict
mapping the ROM **as bytes** (not as a hex string) to a label string.
See `config.py:21-26`:

```python
DS18B20_LABELS = {
    # b"\x28\xff\x...": "top_cover",
    # b"\x28\xff\x...": "above_brood",
    # b"\x28\xff\x...": "brood_side",
    # b"\x28\xff\x...": "entrance",
}
```

Your `rom_list()` output from Step 3 was hex strings like
`28ff64abc123deef`. To convert one to the bytes-literal form MicroPython
wants:

- Split the 16-char hex string into 8 pairs.
- Prefix each pair with `\x`.
- Wrap the whole thing in `b"..."`.

Example — the hex `28ff64abc123deef` becomes:

```python
b"\x28\xff\x64\xab\xc1\x23\xde\xef"
```

Or do it programmatically to avoid transcription errors:

```bash
# On your laptop, in any Python REPL:
python3 -c "print(repr(bytes.fromhex('28ff64abc123deef')))"
# b'(\xffd\xab\xc1#\xde\xef'
```

Notice Python's `repr` uses printable ASCII where possible
(`(` = `0x28`, `d` = `0x64`, `#` = `0x23`) — this is **valid** MicroPython
syntax and works fine. If you find it hard to read, use the fully
escaped form everywhere (`\x28\xff...`).

Edit `firmware/pico/config.py` on your laptop:

```python
DS18B20_LABELS = {
    b"\x28\xff\x64\xab\xc1\x23\xde\xef": "top_cover",
    b"\x28\xff\x11\x22\x33\x44\x55\x66": "above_brood",
    b"\x28\xff\xaa\xbb\xcc\xdd\xee\xff": "brood_side",
    b"\x28\xff\xde\xad\xbe\xef\xca\xfe": "entrance",
}
```

Save. **Every ROM you have must be in the dict**, or the driver will
fall back to the hex string as the label (`ds18b20.py:22-26`), which
works but is ugly in the dashboard.

## Step 6 — Re-flash the config and verify

```bash
cd firmware/pico
mpremote connect /dev/ttyACM0 cp config.py :
mpremote connect /dev/ttyACM0 reset
mpremote connect /dev/ttyACM0
```

Watch the boot log — still says `# ds18b20: 4 probes`. Then wait ~5
seconds for a slow-sensor read. JSON packets should now have a
`t_probes` dict:

```json
{"t": 1234, ..., "t_probes": {"top_cover": 22.5, "above_brood": 22.6,
                              "brood_side": 22.5, "entrance": 22.4}}
```

Every 5 seconds you get a fresh set of readings.

SQL check from the Pi — the `t_probes` dict is stored inside the
`raw_json` column (the top-level `readings` table doesn't split them
into columns because the number of probes is a per-deployment choice):

```bash
sudo sqlite3 /var/lib/beehive/hive.db \
  "SELECT ts, json_extract(raw_json, '$.t_probes') FROM readings
   WHERE json_extract(raw_json, '$.t_probes') IS NOT NULL
   ORDER BY ts DESC LIMIT 3;"
```

You should get 3 rows with `{"top_cover": ..., "above_brood": ..., ...}`
as the second column.

## Success check for this phase

- [ ] Boot log shows `# ds18b20: 4 probes`.
- [ ] `rom_list()` returned 4 addresses, all starting with `28`.
- [ ] Each physical probe is labeled and mapped to a role
      (`top_cover` / `above_brood` / `brood_side` / `entrance`).
- [ ] `config.py` `DS18B20_LABELS` maps each ROM to the correct role.
- [ ] JSON packets include a `t_probes` dict with all four labeled
      keys.
- [ ] Warming one probe with your hand shows only that probe's
      temperature rise in the JSON — the others stay flat.
- [ ] SQL query on the Pi returns fresh `t_probes` data.

Sensor phases so far cover I²C and 1-Wire. Next in the series (upcoming
sessions): Phase 07 (HX711 weight sensor), Phase 08 (bee gate), Phase
09 (cameras), Phase 10 (audio), Phase 11 (rain), Phase 12 (enclosure),
Phase 13 (hive install), Phase 14 (first boot at the hive).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `no DS18B20 probes on bus` | Pull-up missing (you didn't wire the 4.7 kΩ, or wired it to the wrong pin). Or all 4 probes' data lines aren't actually tied together at the junction — reseat. |
| `# ds18b20: 1 probes` when you wired 4 | One or more probe data wires isn't making contact at the junction. Reseat every WAGO / re-solder every joint. |
| `# ds18b20: 3 probes` after 15 minutes of working | A probe's connection went intermittent. Wiggle each junction while watching `rom_list()` — the one that drops is the bad joint. |
| Every probe reads 85.0 °C | 85 °C is the DS18B20's power-on default — appears if you read before a conversion completes. The driver treats 85.0 as `None` (`ds18b20.py:41-42`); if you're consistently seeing 85, the driver isn't calling `convert_temp` before `read_temp`. Should not happen with the shipping driver — check you didn't accidentally edit it. |
| Some probes read −127 °C | That's the "CRC failed" value from the underlying MicroPython library. Usually a signal-integrity issue on a long bus — try shortening the run, or add a small (0.1 µF) cap between VDD and GND at each probe (parasitic bus noise). |
| ROM addresses don't start with `28` | You have counterfeit chips (some clones report family code `28` correctly, others don't). Also possible: you're mixing DS18B20 with the older DS18S20 (family `10`) — the driver should handle both but the address format differs. |
| Two probes report identical temperatures always | Two of your wires got shorted at the junction (both probes' data lines to the same wire is not the failure — that just puts them on the same bus, which is fine). More likely you swapped VDD and DQ on one probe, and it's parasitically powered off the bus. Rewire that probe. |
| Change to `DS18B20_LABELS` didn't take effect | You forgot to re-copy `config.py` after editing. `mpremote connect /dev/ttyACM0 cp config.py :` then `reset`. |
| Bytes literal syntax error when loading `config.py` | You wrote `b"28ff..."` (hex chars) instead of `b"\x28\xff..."` (escape sequences). MicroPython interpretation of `b"28"` is the ASCII bytes `0x32 0x38`, not `0x28`. Use the escape form. |

## What NOT to do

- **Do not** put multiple 4.7 kΩ pull-ups on the bus. One pull-up
  total. Multiple pull-ups pull the bus too hard and probes miss
  timing edges.
- **Do not** wire probes in a star topology with long stubs. The
  1-Wire timing budget assumes a bus-like layout — long branches
  cause reflections and CRC errors. Keep any stub under ~20 cm.
- **Do not** use parasite-power mode. The driver assumes normal
  3-wire power. Parasite mode is a wiring shortcut that has real
  timing tradeoffs, and this bus is short enough not to need it.
- **Do not** skip the physical labeling step. Six months from now
  you will not remember which probe is which — and swapping physical
  probes in the hive after they're potted and installed is annoying.
- **Do not** use PVC-jacketed extension cable inside the hive if you
  extend the probe leads. Bees eat PVC. Use silicone-jacketed wire
  from the cable gland inward.
