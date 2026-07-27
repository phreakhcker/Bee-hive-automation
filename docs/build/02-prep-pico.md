# Phase 02 — Prep the Pico

Goal at end of phase: MicroPython is on the Pico, the beehive firmware
is deployed, and running `mpremote` shows JSON packets appearing once
per second (with most sensor fields `null` because nothing is wired up
yet — that is expected).

Time: 30 minutes.

## Parts checklist

- Pi Pico 2 (RP2350) — or Pico / Pico H / Pico W / Pico 2 W, any variant.
- **Data-capable** USB cable to plug the Pico into your laptop.
- The laptop you used in Phase 01 is fine.

## Step 1 — Get MicroPython

1. Download the current MicroPython UF2 for your board:
   - **Pi Pico 2 (RP2350):** https://micropython.org/download/RPI_PICO2/
   - **Pi Pico / Pico H (RP2040):** https://micropython.org/download/RPI_PICO/
   - **Pi Pico W:** https://micropython.org/download/RPI_PICO_W/
   - **Pi Pico 2 W:** https://micropython.org/download/RPI_PICO2_W/

   Grab the top ".uf2" file listed. Save it somewhere you can find.

2. **Hold the BOOTSEL button** on the Pico and plug it into your laptop's
   USB port. Keep holding BOOTSEL until it enumerates.

3. The Pico appears as a USB mass-storage device named `RPI-RP2` (for
   the RP2040) or `RP2350` (for the RP2350). Confirm you see it in your
   file manager.

4. Drag the `.uf2` file onto that drive. The Pico reboots automatically
   and the drive disappears. That's normal — it's now running MicroPython.

> **📷 Photo needed:** the Pico plugged in with BOOTSEL clearly visible,
> and the mounted `RPI-RP2` drive on the desktop.

## Step 2 — Verify MicroPython booted

The Pico now enumerates as a USB CDC serial device:

- **Linux:** `/dev/ttyACM0` (may be `ttyACM1` if you have another
  serial device already).
- **macOS:** `/dev/tty.usbmodem*` (Terminal: `ls /dev/tty.usb*`).
- **Windows:** some `COMx` port (Device Manager → Ports).

Install `mpremote` if you don't have it:

```bash
pip install --user mpremote
```

Test the REPL:

```bash
mpremote connect /dev/ttyACM0 repl
```

You should see a `>>>` prompt after a moment. Type:

```python
>>> print("hello")
hello
>>> 2+2
4
```

Ctrl-X to exit the REPL. Ctrl-D inside the REPL soft-resets.

**Success check for Step 2:** the REPL works. If not, see
Troubleshooting.

## Step 3 — Copy the beehive firmware onto the Pico

From the beehive repo root on your **laptop** (not the Pi — you're
flashing over the laptop's USB port for now; the Pico will move to the
Pi in Phase 04):

```bash
cd firmware/pico
mpremote connect /dev/ttyACM0 cp config.py :
mpremote connect /dev/ttyACM0 cp main.py :
mpremote connect /dev/ttyACM0 mkdir drivers   # ignore "EEXIST" if it prints
mpremote connect /dev/ttyACM0 cp -r drivers/. :drivers/
mpremote connect /dev/ttyACM0 reset
```

The `reset` at the end reboots the Pico so `main.py` starts.

Same steps are in [`scripts/flash_pico.md`](../../scripts/flash_pico.md)
if you want a shorter reference later.

## Step 4 — Watch it run

```bash
mpremote connect /dev/ttyACM0
```

Within a few seconds you should see output like:

```
# beehive firmware 0.1.0 starting
# hx711 init failed: ...
# ds18b20 init failed: ...
# sht41 init failed: ...
# bme280 init failed: ...
# veml7700 init failed: ...
# bee_gate ready (8 channels)
# battery monitor ready
{"t": 12, "bees_in": 0, "bees_out": 0, "bees_ambiguous": 0, "v_pack": 0.005}
{"t": 13, "bees_in": 0, "bees_out": 0, "bees_ambiguous": 0, "v_pack": 0.007}
...
```

Every line starting with `#` is a human-readable log; the JSON lines are
the actual sensor packets. Ctrl-X detaches without resetting.

**Why so many "init failed":** none of the I²C, 1-Wire, or HX711 sensors
are physically wired up yet — the driver tries to talk to the chip,
gets nothing, and logs it. This is exactly what you want at this stage.
The bee-gate and battery-monitor drivers report "ready" because they
just claim GPIO pins without needing to talk to a chip.

## Step 5 — Send a ping command

Prove the two-way channel works. In another terminal (or after
Ctrl-X'ing out of the passive watch):

```bash
echo '{"cmd":"ping"}' | mpremote connect /dev/ttyACM0 exec "import sys; sys.stdin.readline()"
```

Or more simply, drop into the REPL and paste:

```python
>>> import sys
>>> sys.stdout.write('{"cmd":"ping"}\n')
```

The next JSON packet or so, you should see:

```
# pong v=0.1.0
```

The [firmware README](../../firmware/pico/README.md) lists all
currently-supported commands (`ping`, `tare`, `calibrate`).

## Success check for this phase

- [ ] The Pico enumerates as `/dev/ttyACM0` (or your OS's equivalent)
      every time you plug it in.
- [ ] `mpremote connect ... repl` gives a `>>>` prompt.
- [ ] `mpremote connect ...` (no args) shows JSON packets at roughly
      1 per second.
- [ ] You see `# beehive firmware 0.1.0 starting` in the boot log.
- [ ] `{"cmd":"ping"}` gets a `# pong` reply.

Move on to your chosen battery phase — either
[Phase 03A (salvaged 18650)](03-battery-A.md) or
[Phase 03B (purchased LiFePO4)](03-battery-B.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| No `RPI-RP2` drive when holding BOOTSEL | USB cable is charge-only. Try a different cable. |
| `mpremote: no device found` | Confirm `/dev/ttyACM0` exists (`ls /dev/ttyACM*`). Try `sudo` (some Linux distros don't put your user in `dialout`). Best fix: `sudo usermod -aG dialout $USER`, log out and back in. |
| REPL works but no JSON output on reset | `main.py` crashed. Reconnect REPL: `mpremote connect /dev/ttyACM0 repl`, then Ctrl-C to see the traceback. |
| `ImportError: no module named 'drivers'` | The `drivers/` copy step didn't work. Re-run `mpremote connect ... cp -r drivers/. :drivers/`. |
| Random file-write errors | Filesystem was corrupted somehow. `mpremote connect ... exec "import os; os.mkfs()"` (destroys everything on the Pico) then re-flash. |
| Windows: no COM port appears | Install the Zadig-Adafruit driver or the Microsoft "Windows Terminal" USB-CDC driver package. |

## What NOT to do yet

- Don't wire any sensors to the Pico yet — that's Phase 05 onwards.
- Don't move the Pico to the Pi's USB port yet. Keep it on the laptop
  until the power system is bench-tested in Phase 04.
