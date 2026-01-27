#!/usr/bin/env bash
# Use bash via env for portability across Linux environments.
# PURPOSE:
#   Remove previously installed KITT services and configs.
#   CAUTION: destructive — intended for clean teardown or redeploy.
#
# PSEUDOCODE STEPS:
# 1) Stop services in reverse order.
# 2) Disable services.
# 3) Remove systemd unit files from /etc/systemd/system/.
# 4) Remove udev rules (optional) and reload udev.
# 5) Optionally remove /etc/kitt env files (prompt the user).
# 6) Optionally remove /opt/kitt code, /var/lib/kitt data, /var/log/kitt logs (prompt the user).
# 7) daemon-reload and print summary.

# Fail fast on errors, unset variables, or pipe failures to keep removals safe.
set -euo pipefail

# Stop services (pseudo)
# sudo systemctl stop kitt-health.service || true
# sudo systemctl stop kitt-camera.service || true
# sudo systemctl stop kitt-orchestrator.service || true
# sudo systemctl stop kitt-jmri.service || true
# sudo systemctl stop kitt-mqtt.service || true
# sudo systemctl stop kitt.target || true

# Disable services (pseudo)
# sudo systemctl disable kitt-health.service || true
# sudo systemctl disable kitt-camera.service || true
# sudo systemctl disable kitt-orchestrator.service || true
# sudo systemctl disable kitt-jmri.service || true
# sudo systemctl disable kitt-mqtt.service || true
# sudo systemctl disable kitt.target || true

# Remove unit files (pseudo)
# sudo rm -f /etc/systemd/system/kitt-{orchestrator,jmri,mqtt,camera,health}.service
# sudo rm -f /etc/systemd/system/kitt.target

# Remove udev (pseudo)
# sudo rm -f /etc/udev/rules.d/99-kitt-devices.rules || true
# sudo udevadm control --reload || true
# sudo udevadm trigger || true

# Optional prompts for env, app, data (pseudo)
# read -r -p "Remove /etc/kitt env files? [y/N] " ans; [[ "$ans" =~ ^[Yy]$ ]] && sudo rm -rf /etc/kitt
# read -r -p "Remove /opt/kitt application code? [y/N] " ans; [[ "$ans" =~ ^[Yy]$ ]] && sudo rm -rf /opt/kitt
# read -r -p "Remove /var/lib/kitt data? [y/N] " ans; [[ "$ans" =~ ^[Yy]$ ]] && sudo rm -rf /var/lib/kitt
# read -r -p "Remove /var/log/kitt logs? [y/N] " ans; [[ "$ans" =~ ^[Yy]$ ]] && sudo rm -rf /var/log/kitt

# Reload systemd (pseudo)
# sudo systemctl daemon-reload

# echo "Uninstall complete."
