# Phase 05 — I²C sensors (SHT41, BME280, VEML7700, optional SCD41 / SGP40)

Goal at end of phase: two live I²C buses on the Pico, with humidity /
temperature / pressure / lux appearing in the JSON packets and being
stored in the Pi's SQLite. Wire **one sensor at a time** — do not try
to bring the whole bus up at once and debug six problems at once.

Time: about 2 hours if you go slow (which you should).

## Prereqs

- Phase 02 done (Pico firmware runs, JSON on USB-CDC).
- Phase 04 done (Pico powered from the buck, plugged into the Pi's USB
  port, packets landing in `/var/lib/beehive/hive.db`).

## Two buses, and why

The Pico has two hardware I²C peripherals. The firmware uses both:

| Bus | Pico pins | Sensors | Why they're grouped here |
|---|---|---|---|
| **I²C0** | SDA = **GP20**, SCL = **GP21** | SHT41, BME280 | Hive-interior + external weather. Simple, robust chips. Keep them on their own bus so a misbehaving optional sensor can't take them down. |
| **I²C1** | SDA = **GP16**, SCL = **GP17** | VEML7700, SCD41 *(opt)*, SGP40 *(opt)* | Ambient light plus the optional CO₂ / VOC sensors. The SCD41 in particular draws ~205 mA in spikes; isolating it is safer. |

Pin choices are enforced by `firmware/pico/config.py:8-14` — do not
change them without also updating `config.py`.

**I²C addresses** (from the driver files — don't guess these):

| Sensor | Address | Bus | Driver |
|---|---|---|---|
| SHT41 | `0x44` | I²C0 | `drivers/sht4x.py:11` |
| BME280 | `0x76` (fallback `0x77`) | I²C0 | `drivers/bme280.py:11,28-32` |
| VEML7700 | `0x10` | I²C1 | `drivers/veml7700.py:10` |
| SCD41 | `0x62` | I²C1 | `drivers/scd41.py:10` |
| SGP40 | `0x59` | I²C1 | `drivers/sgp40.py:11` |

No collisions on either bus — you can populate any combination.

## Parts checklist

Required (both):

- **Sensirion SHT41 (or SHT45) breakout** — Adafruit #5665.
- **Bosch BME280 breakout** — Adafruit #2652 or SparkFun. **Do not** use
  the "GY-BME280" clones from AliExpress; they often ship with a BMP280
  (no humidity) and the driver will not detect the swap.
- **Vishay VEML7700 lux breakout** — Adafruit #4162.

Optional (skip if you're not running these):

- **Sensirion SCD41 CO₂ breakout** — Adafruit #5190. Only real from
  Adafruit / DigiKey; AliExpress "SCD41" often ships an SCD40.
- **Sensirion SGP40 VOC breakout** — Adafruit #4829.

Wiring hardware:

- **22 AWG silicone stranded** in yellow (SDA), green (SCL), orange
  (3V3), black (GND). Follow the color convention from
  [`../hardware.md`](../hardware.md).
- **Solderless breadboard** for bench-testing. Full-size (830-tie) is
  plenty; a mini works if it's just I²C.
- **Female-to-male jumper wires** if your Pico isn't already on
  breakout pins (see note below).
- **10 µF ceramic capacitor** — bench decoupling if you're wiring SCD41
  (its 205 mA measurement spikes can droop the 3V3 rail).

**Note on the Pico:** if you soldered header pins onto your Pico in
Phase 02, you can drop it into a breadboard. If you didn't, either
solder pins now or use a Pico-with-headers variant. Trying to hand-hold
jumpers into castellated pads is a bad time.

## General wiring pattern

Every I²C breakout in this project wires the same way:

| Breakout label | Pico pin | Wire color |
|---|---|---|
| `VIN` / `VCC` / `3V3` | **3V3_OUT (pin 36)** | orange |
| `GND` | any GND pin | black |
| `SDA` | I²C0 SDA = GP20, or I²C1 SDA = GP16 | yellow |
| `SCL` | I²C0 SCL = GP21, or I²C1 SCL = GP17 | green |

The breakouts all include on-board I²C pull-up resistors (typically
10 kΩ). With two breakouts on one bus you get 10 kΩ ∥ 10 kΩ = 5 kΩ
which is still fine at 100 kHz. With three on one bus you get ~3.3 kΩ
— still OK. This is why you don't add external pull-ups.

> **📷 Photo needed:** breadboard layout with the Pico + one I²C sensor
> wired up, so builders can compare their layout to yours.

## Step 1 — Wire the SHT41 (I²C0)

1. Power off the Pico (unplug USB from the Pi — or in Phase 04's setup,
   unplug from the Pi's port; the buck rail keeps the Pi alive).
2. Slot the SHT41 breakout into the breadboard.
3. Wire per the table above with **GP20 for SDA** and **GP21 for SCL**.
4. Double-check: 3V3 to VIN (**not to SCL** — a very common mistake
   with 4-pin breakouts). If 3V3 lands on SCL you'll fry the chip.
5. Plug the Pico back into the Pi's USB port.

## Step 2 — Verify SHT41

The SHT41 is enabled by default (`config.py:61` has
`ENABLE_SHT41 = True`). If you didn't turn it off, the firmware is
already trying to talk to it.

From your laptop (or SSH to the Pi and use `screen /dev/ttyACM0 115200`):

```bash
mpremote connect /dev/ttyACM0
```

Look at the boot log. You want:

```
# sht41 ready
```

**Not** what you had in Phase 02:

```
# sht41 init failed: SHT4x not found at 0x44
```

Once initialized, subsequent JSON packets should include `t_in` and
`rh_in`:

```
{"t": 1234, "t_in": 22.14, "rh_in": 48.3, ...}
```

Independent verification from the Pi:

```bash
sudo sqlite3 /var/lib/beehive/hive.db \
  "SELECT ts, t_in, rh_in FROM readings ORDER BY ts DESC LIMIT 3;"
```

Three recent rows, all with sensible numbers (roughly matching room
temp and humidity). Success.

If it still says "init failed" — see Troubleshooting.

## Step 3 — Wire the BME280 (also I²C0)

1. Unplug the Pico from USB.
2. Add the BME280 breakout to the breadboard next to the SHT41.
3. Wire SDA to the **same GP20** row (both sensors share the bus).
   Same for SCL on GP21. Both power off 3V3 and GND.
4. Plug back in.

## Step 4 — Verify BME280

Boot log should now show both:

```
# sht41 ready
# bme280 ready
```

JSON packets should now have `t_out`, `rh_out`, `p_hpa`:

```
{"t": 1234, "t_in": 22.14, "rh_in": 48.3, "t_out": 22.30,
 "rh_out": 47.1, "p_hpa": 1013.8, ...}
```

SQL check:

```bash
sudo sqlite3 /var/lib/beehive/hive.db \
  "SELECT ts, t_in, t_out, p_hpa FROM readings ORDER BY ts DESC LIMIT 3;"
```

If BME280 says `not found on I2C` — the driver checks 0x76 then 0x77
(`drivers/bme280.py:26-32`). Some breakouts have a solder-jumper that
switches between the two. Yours may need the jumper closed, or you may
have a BMP280 counterfeit that reports an unexpected chip ID (line 34).

## Step 5 — Wire the VEML7700 (I²C1)

Same drill, different bus.

1. Unplug the Pico.
2. VEML7700 breakout onto the breadboard.
3. Wire SDA to **GP16** (not GP20 — this is a different bus). SCL to
   **GP17**. Power on 3V3 and GND.
4. Plug back in.

## Step 6 — Verify VEML7700

Boot log:

```
# veml7700 ready
```

The VEML7700 reads on the **slow-sensor cadence** (5 s by default,
`config.py:56`). Every 5th packet or so, `lux` will appear:

```
{"t": 1234, ..., "lux": 342.7}
```

Shine a phone flashlight on the sensor — `lux` should jump into the
thousands. Cover it — `lux` should drop to single digits.

SQL check:

```bash
sudo sqlite3 /var/lib/beehive/hive.db \
  "SELECT ts, lux FROM readings WHERE lux IS NOT NULL ORDER BY ts DESC LIMIT 3;"
```

## Step 7 — (Optional) enable and wire the SCD41 (CO₂)

Skip if you're not running CO₂. You can always come back to this later.

### Enable in firmware

The SCD41 is **disabled by default** (`config.py:64` has
`ENABLE_SCD41 = False`). Edit `firmware/pico/config.py` on your
laptop:

```python
ENABLE_SCD41 = True
```

Re-copy config to the Pico:

```bash
cd firmware/pico
mpremote connect /dev/ttyACM0 cp config.py :
mpremote connect /dev/ttyACM0 reset
```

### Wire it

1. Unplug the Pico.
2. SCD41 breakout onto the breadboard. Same wiring pattern — SDA to
   **GP16**, SCL to **GP17**, 3V3, GND.
3. **Add the 10 µF ceramic cap** across the SCD41's VIN and GND pins,
   as close to the breakout as you can. The chip pulls ~205 mA in
   measurement spikes and the cap keeps 3V3 from sagging.
4. Plug back in.

### Verify

Boot log:

```
# scd41 ready
```

The SCD41 in low-power periodic mode takes measurements every 30 s
(`drivers/scd41.py:11`). Give it a couple of minutes for the first
reading, then:

```bash
sudo sqlite3 /var/lib/beehive/hive.db \
  "SELECT ts, co2_ppm FROM readings WHERE co2_ppm IS NOT NULL
   ORDER BY ts DESC LIMIT 3;"
```

**Sanity check:** indoor CO₂ is typically 400-1500 ppm. Blow gently
into the room from a meter away — CO₂ should spike into the thousands
briefly. If your reading is stuck at 0 or 65535, the sensor probably
isn't warmed up yet — wait 5 minutes.

## Step 8 — (Optional) enable and wire the SGP40 (VOC)

Same pattern as SCD41. Enable in `config.py:65`:

```python
ENABLE_SGP40 = True
```

Re-copy `config.py`, wire (SDA=GP16, SCL=GP17, 3V3, GND), verify:

```
# sgp40 ready
```

JSON should have `voc_idx` (the raw ticks value from the driver —
`drivers/sgp40.py:39-41` — the Pi is responsible for turning this into
the 0-500 VOC Index using Sensirion's gas-index algorithm downstream).
On the bench, expect raw values in the range 25000-35000 in clean air;
values change with contaminants (breath, alcohol, cleaning products).

## Step 9 — Confirm everything survives a reboot

The Pico's firmware re-reads `config.py` on every boot. To be sure
your changes stuck:

```bash
mpremote connect /dev/ttyACM0 reset
mpremote connect /dev/ttyACM0
```

Watch the boot log. Every sensor you wired and enabled should print
`# ... ready`. Every one you did NOT wire should print
`# ... init failed` (unless you also flipped its `ENABLE_*` flag to
`False`, which is fine too).

If a sensor was working and now isn't — most likely you nudged a
jumper wire on the breadboard. Reseat, reboot.

## Success check for this phase

- [ ] Boot log shows `# sht41 ready`, `# bme280 ready`, `# veml7700 ready`.
- [ ] JSON packets contain `t_in`, `rh_in`, `t_out`, `rh_out`, `p_hpa`,
      and (every ~5 s) `lux`.
- [ ] SQL query returns fresh rows with all six fields non-null.
- [ ] If you enabled SCD41: `co2_ppm` appears every ~30 s and responds
      to breath.
- [ ] If you enabled SGP40: `voc_idx` (raw) appears in every packet.
- [ ] Values look plausible (temp within 5 °C of room, humidity 20-90%,
      pressure roughly 990-1030 hPa unless you live at altitude).

Move on to [Phase 06 — DS18B20 1-Wire array](06-sensors-1wire.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `# sht41 init failed: SHT4x not found at 0x44` | 1) Verify SDA/SCL on GP20/GP21, not swapped and not on GP16/GP17 (that's the other bus). 2) DMM continuity from Pico pin to breakout pad — jumpers fail more than you'd think. 3) Confirm 3V3 is on VIN, not on SCL (that fries the chip and you need a new one). |
| `# bme280 not found on I2C` | Check the solder-jumper for the address select (0x76 vs 0x77). Adafruit's ships at 0x77; SparkFun's ships at 0x76. Driver falls back at `bme280.py:28-32`, so either should work — but if the jumper is in a weird half-state it won't respond to either. |
| `# bme280 unexpected chip id 0x??` | You have a BMP280 (chip id 0x58) or a fake. BMP280 is temp/pressure only, no humidity. Buy a real BME280 from Adafruit / SparkFun. |
| SHT41 boots but reads temperature 60 °C / humidity 100 % | Chip's on-die heater fired. The driver doesn't use the heater command — this is usually a hardware fault (shorted trace) or a fake sensor. Return it. |
| VEML7700 reports 0 lux even in bright light | Sensor face is covered (the little clear plastic window at the top of the chip). Some breakouts ship with protective film — peel it off. |
| SCD41 reads 65535 ppm | Data-ready check flaked out. The driver retries every second; if it stays stuck, unplug and re-plug. If persistent, wait 5 min for the first proper measurement (chip warm-up). |
| SCD41 reads 400 ppm forever, even when you exhale on it | Sensor might be running in single-shot mode from a previous firmware. The driver's `__init__` calls `CMD_STOP` then `CMD_START_LOW_POWER` — but sometimes the chip needs a full power cycle. Unplug the Pico for 10 s, plug back in. |
| SGP40 raw value pinned at 30000 | Sensor hasn't warmed up. It takes ~10 minutes of continuous operation for the surface to reach equilibrium. Leave it running. |
| Multiple `init failed` after adding a new sensor | You probably have a short between SDA and SCL on the breadboard. DMM continuity check on the two rails should read OPEN when the Pico is unpowered. |
| Sensors read fine on I²C0 but I²C1 devices don't respond | GP16/GP17 got confused. Double-check the pin numbers on your Pico's silkscreen — physical pins 21 (SDA1) and 22 (SCL1). |
| Random dropouts / init failures every few hours | Bad power. If you're still bench-powering the Pico from a laptop, the USB drop from a suspend cycle can trigger it. Move the Pico to the buck-powered Pi USB from Phase 04. |

## What NOT to do

- **Do not** put I²C sensors on the wrong bus and expect them to work.
  The firmware reads them by bus reference (`config.py:34-37`) — a
  SHT41 wired to GP16/GP17 will silently be invisible.
- **Do not** add external pull-up resistors to SDA/SCL if the
  breakouts have them (all the recommended breakouts do). Doubling up
  gets you very low resistance, which strains the driver.
- **Do not** exceed one meter of I²C cable at 100 kHz without proper
  differential drivers. All these breakouts are meant for
  bench-cluster-length runs.
- **Do not** enable a sensor's `ENABLE_*` flag in `config.py` unless
  you actually plan to wire it up. The "init failed" log spam isn't
  harmful, but it clutters diagnostics.
- **Do not** solder directly to a breakout's I²C pads unless you're
  ready to commit to that layout. Leave headers so you can breadboard
  during sensor phases and only pot / conformal-coat in Phase 12.
