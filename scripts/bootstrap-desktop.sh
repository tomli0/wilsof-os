#!/bin/sh
# Privileged, repeatable package bootstrap for the dedicated Wilsof Fedora VM.
# It does not alter GDM, users, sudo policy, or any compositor configuration.
set -eu

required_packages='dms hyprland hyprlock hypridle xdg-desktop-portal-hyprland'

fail() {
  printf '%s\n' "bootstrap: $*" >&2
  exit 1
}

[ "$(id -un)" = "wilsofdev" ] || fail "must run as wilsofdev on the dedicated test VM"
[ -r /etc/os-release ] || fail "/etc/os-release is unavailable"
. /etc/os-release
[ "${ID:-}" = "fedora" ] || fail "target must be Fedora; found ${ID:-unknown}"
[ "${VERSION_ID:-}" = "44" ] || fail "target must be Fedora 44; found ${VERSION_ID:-unknown}"
command -v sudo >/dev/null || fail "sudo is required"
command -v dnf >/dev/null || fail "dnf is required"
command -v rpm >/dev/null || fail "rpm is required"

# Do not create password-free sudo rules. Request normal local sudo authentication once.
sudo -v

# DMS's documented stable COPR and a Fedora 44 Hyprland COPR with the required
# compositor, portal, locker and idle daemon. dnf imports and enforces repo RPM keys.
sudo dnf -y copr enable avengemedia/dms
sudo dnf -y copr enable ashbuk/Hyprland-Fedora

# Refuse to install if the enabled sources do not provide every agreed component.
for package in $required_packages; do
  dnf -q repoquery --latest-limit=1 --qf '%{name} %{evr} %{repoid}' "$package" | grep -q '^' \
    || fail "enabled sources do not provide $package for Fedora ${VERSION_ID}"
done

sudo dnf -y install dms hyprland hyprlock hypridle xdg-desktop-portal-hyprland
rpm -q dms hyprland hyprlock hypridle xdg-desktop-portal-hyprland >/dev/null

# dnf verifies RPM signatures during installation. Validate any retained RPM payloads too.
find /var/cache/dnf -type f -name '*.rpm' -print0 2>/dev/null | xargs -0 -r rpm --checksig

# GNOME remains the fallback desktop: the bootstrap must not disable GDM.
systemctl is-enabled gdm >/dev/null || fail "GDM is not enabled; refusing to continue"

printf '%s\n' 'Bootstrap complete. DMS, Hyprland, Hyprlock, Hypridle and the Hyprland portal are installed; GDM remains enabled.'
