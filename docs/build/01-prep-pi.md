# Phase 01 — Prep the Raspberry Pi

Goal at end of phase: the Pi boots to a clean OS, you can SSH in, and
running `bash scripts/setup_pi.sh` has installed the beehive services.

Time: about 1 hour, most of it waiting for `apt-get install`.

## Parts checklist

- Raspberry Pi 5 (4 GB is fine; 8 GB if you want headroom for ML later).
  Pi 4 works if that's what you have.
- Official 27 W USB-C PSU (bench setup only — the field system runs off
  the buck; see [Phase 04](04-power-stack.md)).
- SanDisk High Endurance 64 GB microSD or larger.
- Monitor + microHDMI cable + USB keyboard, **OR** headless setup:
  Wi-Fi credentials + something to find the DHCP lease (router admin,
  or `arp -a` after boot).
- Ethernet cable optional but makes headless setup easier.

## Step 1 — Flash the SD card

1. On your laptop, install **Raspberry Pi Imager**:
   https://www.raspberrypi.com/software/
2. Insert the microSD card via a reader.
3. In Imager: choose **Raspberry Pi 5** as the device, **Raspberry Pi
   OS Lite (64-bit)** as the OS (from "Raspberry Pi OS (other)"). Lite
   because we have no monitor at the hive, ever.
4. Before writing, click the ⚙️ (advanced settings) or press
   `Ctrl-Shift-X`. Set:
   - Hostname: `beehive` (or whatever you like).
   - **Enable SSH** with password authentication (or, better, paste your
     SSH public key).
   - **Set username and password** (default `pi` / something you'll
     remember).
   - Configure your Wi-Fi SSID + password if going headless. Set the
     Wi-Fi country too.
   - Set your locale/timezone.
5. Write the image. Takes ~5 minutes.

## Step 2 — First boot

1. Eject the SD card, insert into the Pi.
2. Connect Ethernet if using it (recommended for the first boot).
3. Power on with the official PSU. Wait ~90 seconds for first-boot
   expansion.
4. Find the Pi on your network:

   ```bash
   # From your laptop:
   ping beehive.local          # mDNS -- works on macOS, most Linux, Windows with Bonjour
   # or, if that fails:
   arp -a | grep -i b8:27:eb   # older Pi MAC prefix
   arp -a | grep -i dc:a6:32   # Pi 4/5 MAC prefix
   ```

5. SSH in:

   ```bash
   ssh pi@beehive.local
   # or
   ssh pi@<ip.address>
   ```

   Accept the host key on first connect.

**Success check for Step 2:** you see a shell prompt like
`pi@beehive:~ $`.

## Step 3 — System update + clone the repo

```bash
sudo apt-get update
sudo apt-get -y full-upgrade
sudo reboot
```

Reconnect after the reboot, then:

```bash
sudo apt-get install -y git
git clone https://github.com/phreakhcker/Bee-hive-automation.git beehive
cd beehive
```

(If your Wi-Fi is flaky here, do the clone over Ethernet — much less
painful.)

## Step 4 — Run the setup script

The script at [`scripts/setup_pi.sh`](../../scripts/setup_pi.sh) does
everything the Pi needs. Read it first (it's 60 lines) so you know
what's about to happen — briefly, it:

- Installs `python3-*` packages (flask, numpy, scipy, picamera2, serial,
  gpiozero) plus `ffmpeg`, `sqlite3`, `mpremote`, `uhubctl`.
- Enables I²C, I²S, and camera auto-detect in `/boot/firmware/config.txt`.
- Creates `/var/lib/beehive/{captures,logs}` and hands them to the `pi` user.
- Copies `config/config.example.yaml` to `/etc/beehive/config.yaml`.
- Installs and enables the seven systemd units under
  [`scripts/systemd/`](../../scripts/systemd/).

Run it:

```bash
sudo bash scripts/setup_pi.sh
```

Expected: no red errors. The last line says "Reboot, then check:
`systemctl status beehive-*`".

Reboot:

```bash
sudo reboot
```

## Step 5 — Verify the services came up

After reboot, SSH back in:

```bash
systemctl status beehive-ingest
systemctl status beehive-dashboard
```

They will report **"activating (auto-restart)"** or **"failed"** at this
point — that is fine and expected. The ingest service can't do anything
without a Pico plugged in, and the dashboard can start but shows an
empty database. What you're checking is that systemd knows about the
units and is trying.

If a service isn't found at all, `setup_pi.sh` didn't install it — check
the earlier output for errors, most likely `apt` failed.

## Step 6 — Reach the dashboard

```bash
hostname -I
```

Note the IP address. From a phone or laptop on the same network:

```
http://<pi-ip>:8080/
```

You should see the empty dashboard shell. No data yet — that's normal.

> **📷 Photo needed:** screenshot of the empty dashboard as it first
> appears, so builders know what "success" looks like at this stage.

## Success check for this phase

- [ ] `ssh pi@beehive.local` (or IP) works.
- [ ] `systemctl list-unit-files 'beehive-*'` lists 7 units, all `enabled`.
- [ ] `ls /var/lib/beehive/` shows `captures/` and `logs/`.
- [ ] `cat /etc/beehive/config.yaml` prints the config.
- [ ] The dashboard at `http://<pi>:8080/` responds (even if empty).
- [ ] `groups pi | grep -q i2c && echo yes` — should print `yes` after
      reboot. If not, `sudo usermod -aG i2c,gpio,video,audio pi && sudo reboot`.

Move on to [Phase 02 — Prep the Pico](02-prep-pico.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `beehive.local` doesn't resolve | Your network doesn't do mDNS. Find the IP via router or `arp`. |
| SSH says "connection refused" | You didn't check the "Enable SSH" box in Imager. Re-flash, or add an empty `ssh` file to the boot partition. |
| `setup_pi.sh: command not found` | You're not in the repo root. `cd ~/beehive` first. |
| `apt-get` fails with 404s | `sudo apt-get update` first, then retry. |
| `systemctl status beehive-*` shows units are missing | The script silently failed on the systemd copy step. Re-run with `bash -x scripts/setup_pi.sh` to see where. |
| Dashboard 8080 not reachable | `sudo systemctl start beehive-dashboard` and check `journalctl -u beehive-dashboard`. Firewall on the Pi is off by default. |
| `python3-picamera2` won't install | You're on Pi OS Bookworm's older release — `sudo apt-get -y full-upgrade` and retry. |

## What NOT to do yet

- Don't wire anything to the GPIO header. That's Phase 04 and after.
- Don't try to plug the Pico in yet. That's Phase 02.
- Don't run the field system on this SD card for burn-in and then swap
  cards later — burn in on the SD card you'll actually deploy. The Pi
  will change identifiers between cards.
