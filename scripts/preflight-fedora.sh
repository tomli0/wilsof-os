#!/bin/sh
# Read-only target-VM preflight. Never installs packages or alters configuration.
set -eu

if [ ! -r /etc/os-release ]; then
  printf '%s\n' "Fedora preflight: /etc/os-release is unavailable." >&2
  exit 1
fi
# shellcheck source=/etc/os-release
. /etc/os-release
if [ "${ID:-}" != "fedora" ]; then
  printf '%s\n' "Fedora preflight: target must be Fedora; found ${ID:-unknown}." >&2
  exit 1
fi

missing=0
for command in systemctl dnf hyprctl dms loginctl; do
  if command -v "$command" >/dev/null 2>&1; then
    printf 'PASS command: %s\n' "$command"
  else
    printf 'FAIL command missing: %s\n' "$command" >&2
    missing=1
  fi
done

if systemctl --user show-environment >/dev/null 2>&1; then
  printf '%s\n' "PASS user systemd session"
else
  printf '%s\n' "FAIL user systemd session unavailable" >&2
  missing=1
fi

if command -v getenforce >/dev/null 2>&1; then
  printf 'SELinux: %s\n' "$(getenforce)"
else
  printf '%s\n' "FAIL getenforce missing" >&2
  missing=1
fi

exit "$missing"
