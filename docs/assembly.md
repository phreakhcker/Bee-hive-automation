# Assembly Guide

The order matters. Do these steps in sequence.

## 1. Battery pack (Week 1–2)

Follow [`power-system.md`](power-system.md) *Salvaged-cell testing pipeline*. This takes real calendar time — the self-discharge test alone is a week.

## 2. Power stack bench build (Week 3)

1. Wire panel → MPPT → fuse → BMS → pack.
2. Configure MPPT via VictronConnect (settings table in [`power-system.md`](power-system.md)).
3. Attach NTC thermistor to a cell, wire to MPPT battery-temp input.
4. Wire pack → fuse → buck → dummy load (10 W bulb).
5. Bluetooth pair with both MPPT and Daly BMS. Verify cell balance.

## 3. Bench burn-in (Week 3–4)

Two weeks running the dummy load. Log per-cell voltages daily. Any cell that drifts > 50 mV under load — pull it, cull the group, rebuild with fresh matched cells.

## 4. Prep the Pi (parallel with burn-in)

```bash
# Fresh Raspberry Pi OS Lite (Bookworm 64-bit) on SD card.
# SSH in.
git clone https://github.com/<you>/beehive-automation.git
cd beehive-automation
bash scripts/setup_pi.sh
```

That script (see it for details): installs deps, enables I²S + camera in `/boot/firmware/config.txt`, creates the data directory, installs systemd units.

## 5. Prep the Pico

Follow [`../scripts/flash_pico.md`](../scripts/flash_pico.md):

1. Hold BOOTSEL, plug into laptop, drag `RPI_PICO2-*.uf2` MicroPython image.
2. Use `mpremote` to copy `firmware/pico/` to the Pico.
3. Reset — `main.py` runs on boot.

## 6. Bench-wire sensors one at a time

Do **not** try to wire everything at once and hope it works. Wire each sensor, plug the Pico into the Pi, run `python3 pi/services/sensor_ingest.py --debug` and confirm the reading appears.

Order:
1. DS18B20 array — easiest, always works.
2. SHT41 (I²C0) — verify address 0x44.
3. BME280 (I²C0) — verify address 0x76.
4. VEML7700 (I²C1) — verify address 0x10.
5. HX711 + load cells — the trickiest to calibrate. See calibration section below.
6. Optional: SCD41, SGP40.
7. Bee gate — build the acrylic/3D-printed body, wire all 16 phototransistors, test by breaking beams with a toothpick.

## 7. Weight sensor calibration

1. Mount all 4 load cells on the hive stand base with the combinator board on top.
2. Empty stand + top platform: `{"cmd":"tare"}` — establishes zero.
3. Place a known weight on it (10 kg dumbbell, or 5 × 2 L water bottles = ~10 kg): note the raw reading.
4. Compute `cal = known_kg / (raw_reading - tare)`.
5. Send `{"cmd":"calibrate","cal":<value>}` to Pico. Verify the reported weight matches your reference within ~50 g.

Repeat calibration seasonally — HX711 drifts with temperature and humidity.

## 8. Camera setup

- Entrance camera: mount 10 cm above and 15° forward of the landing board. Ring light optional but greatly improves pollen classifier accuracy later.
- Inside camera: recessed behind a 3 mm acrylic disc, mounted through the top cover or an inner cover. IR LED strip (~30 cm, cut from reel) around the perimeter facing inward.

```bash
libcamera-hello --list-cameras   # confirm both cameras enumerated
libcamera-still -o test.jpg      # capture from camera 0
libcamera-still --camera 1 -o test.jpg
```

## 9. Enclosures

- **Electronics box** (Bud NBF-32026): Pi, Pico, buck, USB hub if used. Cable glands on the bottom.
- **Battery box** (vented ammo-can style): pack, BMS, ANL fuse. Ceramic fiber liner. Cable glands high on the wall (heavy gases sink).
- Keep the two boxes at least 20 cm apart.
- Mount both on the hive stand, or on a nearby post.

## 10. Hive-side installation

Do this at dusk or dawn, cool weather, wearing a veil.

1. Slide the pre-built bee gate over the entrance reducer.
2. Route SHT41 and 4× DS18B20 cables in through the inner cover with strain relief. Use silicone-insulated wire from cable-gland point onward — bees eat PVC.
3. Route inside-camera cable through the top cover.
4. Route IR LED strip inside.
5. Bring one 8-conductor cable back to the electronics box: this carries I²C, 1-Wire, and 3V3/GND to the hive-side sensors. Use a shielded 8-conductor cable (like an S/FTP CAT6).
6. Coat all in-hive electronics with MG Chemicals 419D conformal coating **before** installation. Mask sensor apertures (SHT41 opening, DS18B20 tips) with polyimide tape while coating.

## 11. Solar panel install

- Mount facing south (northern hemisphere) at latitude-tilt angle.
- No shading between 10 AM and 4 PM local solar time.
- Route MC4 cable through a cable gland in the electronics box.
- Ground the panel frame per local electrical code (in the US: 8 AWG bare copper to a ground rod, if permanently installed).

## 12. First boot at the hive

1. Confirm all cables land where they should.
2. Reconnect BMS to pack. Pack goes live.
3. Buck output should show 5 V within a second.
4. Pi boots. `journalctl -u beehive-*` shows services starting.
5. Browse to `http://<pi>:8080/` from a phone or laptop. Dashboard appears.

Give it 24 hours before you touch it. Bees will investigate for a day and then ignore the whole setup.

## 13. Ongoing maintenance

| Task | Frequency |
|---|---|
| Check dashboard for gaps | Weekly |
| Verify pack balance via Daly app | Monthly |
| Re-tare weight sensor | Monthly (or after inspections) |
| Clean bee-gate slots (propolis) | Monthly during flow, quarterly off-season |
| Wipe camera windows | Monthly |
| Replace silica gel packs | Every 3–6 months |
| Full pack health check (recap capacity) | Annually, off-season |
| Conformal-coating touch-up | Annually |
