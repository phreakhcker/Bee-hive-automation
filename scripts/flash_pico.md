# Flashing the Pico

One-time setup, then copying the firmware.

## 1. Get MicroPython onto the Pico

1. Download the latest MicroPython UF2 for your board:
   - **Pi Pico 2 (RP2350):** https://micropython.org/download/RPI_PICO2/
   - **Pi Pico / Pico H (RP2040):** https://micropython.org/download/RPI_PICO/
   - **Pi Pico W:** https://micropython.org/download/RPI_PICO_W/
2. **Hold BOOTSEL** on the Pico while plugging into your laptop's USB.
3. It appears as a USB mass storage device named `RPI-RP2` (or `RP2350`).
4. Drag the `.uf2` onto that drive. The Pico reboots automatically.

## 2. Verify it booted

The Pico now enumerates as a USB CDC device:

- Linux: `/dev/ttyACM0`
- macOS: `/dev/tty.usbmodem*`
- Windows: some `COM` port

```bash
# From your laptop:
pip install --user mpremote
mpremote connect /dev/ttyACM0 repl
```
You should get a `>>>` prompt. Ctrl-D to soft-reset, Ctrl-X to exit.

## 3. Copy the firmware

From this repo root, with the Pico plugged in:

```bash
cd firmware/pico
mpremote connect /dev/ttyACM0 cp config.py :
mpremote connect /dev/ttyACM0 cp main.py :
mpremote connect /dev/ttyACM0 mkdir drivers   # ignore error if it exists
mpremote connect /dev/ttyACM0 cp -r drivers/. :drivers/
mpremote connect /dev/ttyACM0 reset
```

## 4. Watch it run

```bash
mpremote connect /dev/ttyACM0
```

You should see one-line JSON packets appearing about once per second, plus `#`-prefixed log lines during init. Ctrl-X to detach without resetting.

## 5. Enumerate DS18B20 probes (one-time)

Once the DS18B20 array is wired:

```bash
mpremote connect /dev/ttyACM0 exec "
from drivers.ds18b20 import DS18B20Array
d = DS18B20Array(22)
print(d.rom_list())
"
```

Note the addresses. Edit `firmware/pico/config.py` → `DS18B20_LABELS` to map each address to a human-readable label (`top_cover`, `above_brood`, etc.), then re-copy `config.py`:

```bash
mpremote connect /dev/ttyACM0 cp config.py :
mpremote connect /dev/ttyACM0 reset
```

## 6. Weight calibration

Once load cells are wired and the physical stand is assembled — see [`../docs/assembly.md`](../docs/assembly.md) *Weight sensor calibration*. In short:

1. Empty platform. Send `{"cmd":"tare"}` via serial or the dashboard button.
2. Place a known reference weight (10 kg is convenient).
3. Read reported weight (probably wrong on first run).
4. Compute new `cal = 10.0 / (reported_kg / current_cal)`.
5. Send `{"cmd":"calibrate","cal":<value>}`.
6. Save the value to `config.HX711_SCALE` and re-copy `config.py`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `mpremote: no device` | Check cable is data-capable (not charge-only) |
| Pico never enumerates on boot | Re-flash MicroPython UF2 |
| REPL works but no JSON output | Something in `main.py` crashed — check with `mpremote connect ... repl` and Ctrl-C |
| Sensors init as `failed` | Check wiring, and confirm `ENABLE_*` flags in `config.py` |
| `SHT4x not found at 0x44` | I²C0 wiring (SDA=GP20, SCL=GP21) |
| `BME280 not found` | Try alt address 0x77 (driver auto-falls-back) |
| Weight reads garbage | HX711 cable too long / not shielded — use CAT6 with foil |
