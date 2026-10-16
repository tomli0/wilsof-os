#!/bin/sh
# Read-only target-VM preflight for the dedicated Arch Wilsof test VM.
set -eu

if [ ! -r /etc/os-release ]; then
  printf '%s\n' "Arch preflight: /etc/os-release is unavailable." >&2
  exit 1
fi
. /etc/os-release
if [ "${ID:-}" != "arch" ]; then
  printf '%s\n' "Arch preflight: target must be Arch Linux; found ${ID:-unknown}." >&2
  exit 1
fi

missing=0
for command in systemctl pacman hyprctl dms loginctl; do
  if command -v "$command" >/dev/null 2>&1; then
    printf 'PASS command: %s\n' "$command"
  else
    printf 'FAIL command missing: %s\n' "$command" >&2
    missing=1
  fi
done

for package in dms-shell hyprland hyprlock hypridle xdg-desktop-portal-hyprland ghostty firefox nautilus gnome-text-editor papers loupe vlc; do
  if pacman -Q "$package" >/dev/null 2>&1; then
    printf 'PASS package: %s\n' "$package"
  else
    printf 'FAIL package missing: %s\n' "$package" >&2
    missing=1
  fi
done

if systemctl --user show-environment >/dev/null 2>&1; then
  printf '%s\n' "PASS user systemd session"
else
  printf '%s\n' "FAIL user systemd session unavailable" >&2
  missing=1
fi

exit "$missing"
