#!/bin/sh
# Installs only into the current user's home on an explicitly designated test VM.
set -eu

if [ "${WILSOF_TARGET_VM:-}" != "1" ]; then
  printf '%s\n' "Refusing to run: set WILSOF_TARGET_VM=1 on the dedicated Wilsof test VM." >&2
  exit 64
fi

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
[ -r /etc/os-release ] || { printf '%s\n' "Target OS cannot be identified." >&2; exit 1; }
. /etc/os-release
case "${ID:-}" in
  fedora) "$root/scripts/preflight-fedora.sh" ;;
  arch) "$root/scripts/preflight-arch.sh" ;;
  *) printf '%s\n' "Unsupported target OS: ${ID:-unknown}." >&2; exit 1 ;;
esac

install -d "$HOME/.local/bin" "$HOME/.local/share/wilsof-os/assets" \
  "$HOME/.config/hypr" "$HOME/.config/systemd/user"
install -m 0755 "$root/bin/wilsof-search" "$HOME/.local/bin/wilsof-search"
install -m 0755 "$root/bin/wilsof-lock" "$HOME/.local/bin/wilsof-lock"
install -m 0644 "$root/config/hypr/wilsof.conf" "$HOME/.config/hypr/wilsof.conf"
install -m 0644 "$root/config/hypr/wilsof.lua" "$HOME/.config/hypr/wilsof.lua"
install -m 0644 "$root/config/hypr/hypridle.conf" "$HOME/.config/hypr/hypridle.conf"
install -m 0644 "$root/config/systemd/wilsof-session.target" "$HOME/.config/systemd/user/wilsof-session.target"
install -m 0644 "$root/config/systemd/wilsof-wallpaper.service" "$HOME/.config/systemd/user/wilsof-wallpaper.service"
install -m 0644 "$root/assets/Mørk geometrisk bakgrunn med isblått WS-monogram.png" "$HOME/.local/share/wilsof-os/assets/Mørk geometrisk bakgrunn med isblått WS-monogram.png"

# DMS owns the base Hyprland Lua configuration; generate it only when absent.
if [ ! -f "$HOME/.config/hypr/hyprland.lua" ]; then
  dms setup headless --compositor hyprland --skip-existing
fi

entry="$HOME/.config/hypr/hyprland.lua"
[ -f "$entry" ] || { printf '%s\n' "DMS did not create $entry" >&2; exit 1; }
if ! grep -Fq 'require("wilsof")' "$entry"; then
  printf '\n-- WILSOF_MANAGED: local visual and keyboard overrides\nrequire("wilsof")\n' >> "$entry"
fi

systemctl --user daemon-reload
systemctl --user enable dms.service hypridle.service wilsof-wallpaper.service
printf '%s\n' "Installed Wilsof user configuration. Start a Hyprland session through the configured display manager; DMS, Hypridle, the Wilsof wallpaper service, Super+Space and Super+L are enabled for that graphical session."
