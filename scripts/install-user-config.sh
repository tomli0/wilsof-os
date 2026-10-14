#!/bin/sh
# Installs only into the current user's home on an explicitly designated test VM.
set -eu

if [ "${WILSOF_TARGET_VM:-}" != "1" ]; then
  printf '%s\n' "Refusing to run: set WILSOF_TARGET_VM=1 on the dedicated Wilsof test VM." >&2
  exit 64
fi

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
"$root/scripts/preflight-fedora.sh"

install -d "$HOME/.local/bin" "$HOME/.local/share/wilsof-os/assets" \
  "$HOME/.config/hypr" "$HOME/.config/systemd/user"
install -m 0755 "$root/bin/wilsof-search" "$HOME/.local/bin/wilsof-search"
install -m 0644 "$root/config/hypr/wilsof.conf" "$HOME/.config/hypr/wilsof.conf"
install -m 0644 "$root/config/systemd/wilsof-session.target" "$HOME/.config/systemd/user/wilsof-session.target"
install -m 0644 "$root/config/systemd/wilsof-wallpaper.service" "$HOME/.config/systemd/user/wilsof-wallpaper.service"
install -m 0644 "$root/assets/Mørk geometrisk bakgrunn med isblått WS-monogram.png" "$HOME/.local/share/wilsof-os/assets/Mørk geometrisk bakgrunn med isblått WS-monogram.png"

systemctl --user daemon-reload
printf '%s\n' "Installed Wilsof files. Add 'source = ~/.config/hypr/wilsof.conf' once to the dedicated VM's Hyprland config, then enable: systemctl --user enable --now wilsof-wallpaper.service"
