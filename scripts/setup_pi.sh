#!/usr/bin/env bash
# Provisions a fresh Raspberry Pi OS Lite (Bookworm, 64-bit) for beehive automation.
# Idempotent -- safe to re-run.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="/var/lib/beehive"

echo ">>> Beehive Pi setup"
echo ">>> repo: $REPO_ROOT"

if [[ $EUID -ne 0 ]]; then
    echo "!! run with sudo"
    exit 1
fi

echo ">>> Installing system packages"
apt-get update
apt-get install -y \
    python3 python3-pip python3-venv python3-serial python3-yaml \
    python3-flask python3-numpy python3-scipy python3-picamera2 \
    python3-libcamera python3-gpiozero \
    ffmpeg libatlas-base-dev libjpeg-dev libopenblas0 \
    sqlite3 mpremote uhubctl

echo ">>> Enabling camera + I2S + I2C in /boot/firmware/config.txt"
CONFIG_TXT=/boot/firmware/config.txt
grep -q '^dtparam=i2c_arm=on' "$CONFIG_TXT" || echo 'dtparam=i2c_arm=on' >> "$CONFIG_TXT"
grep -q '^dtparam=i2s=on'     "$CONFIG_TXT" || echo 'dtparam=i2s=on'     >> "$CONFIG_TXT"
grep -q '^camera_auto_detect=1' "$CONFIG_TXT" || echo 'camera_auto_detect=1' >> "$CONFIG_TXT"
grep -q 'googlevoicehat-soundcard' "$CONFIG_TXT" || \
    echo 'dtoverlay=googlevoicehat-soundcard' >> "$CONFIG_TXT"

echo ">>> Creating data dir $DATA_DIR"
mkdir -p "$DATA_DIR/captures" "$DATA_DIR/logs"
chown -R pi:pi "$DATA_DIR"

echo ">>> Installing config"
mkdir -p /etc/beehive
if [[ ! -f /etc/beehive/config.yaml ]]; then
    cp "$REPO_ROOT/config/config.example.yaml" /etc/beehive/config.yaml
    echo "   -> copied example; edit /etc/beehive/config.yaml if needed"
fi

echo ">>> Installing systemd units"
for unit in "$REPO_ROOT"/scripts/systemd/*.service; do
    install -m 644 "$unit" /etc/systemd/system/
    echo "   installed $(basename "$unit")"
done
systemctl daemon-reload

echo ">>> Enabling services"
for name in beehive-ingest beehive-camera-entrance beehive-camera-inside \
            beehive-audio beehive-rain beehive-shutdown-guard beehive-dashboard; do
    systemctl enable "$name"
done

echo
echo ">>> Done."
echo ">>> Reboot, then check:  systemctl status beehive-*"
echo ">>> Dashboard: http://$(hostname -I | awk '{print $1}'):8080/"
