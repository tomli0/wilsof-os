# Arkitektur — Wilsof Arch-prototype

## Stabel

Arch Linux → systemd-boot/UEFI → greetd/tuigreet → Hyprland → DMS. Wilsof er et versjonert lag over DMS-generert Hyprland-konfigurasjon, ikke en shell-fork.

`~/.config/hypr/hyprland.lua` genereres av DMS. Installasjonen legger til én markert `require("wilsof")` sist. `wilsof.lua` eier Wilsof-farger, layout, avtalte bindinger og `wilsof-session.target`; den endrer ikke `dms/*.lua`.

## Bakgrunn og farger

DMS er eneste bakgrunnseier: `wilsof-wallpaper.service` kaller DMS-IPC med den godkjente asseten. DMS bruker `wilsof-theme.json` som fast custom theme. Systemd-drop-in setter `DMS_DISABLE_MATUGEN=1`, slik at bakgrunn ikke genererer eller overskriver Wilsof-paletten.

Førstegangsinstallasjonen skriver et minimalt `settings.json` fra template. Etter at markøren `~/.local/state/wilsof-os/dms-defaults-v1` finnes, beholder installasjonsskriptet personlige DMS-innstillinger. Eksplicit reset må være en separat brukerhandling.

## Launcher, lås og tjenester

`wilsof-search` er en smal, argumentvalidert bro til `dms ipc call spotlight toggle`; den påstår ikke egne providers. `wilsof-help` åpner DMS sin levende keybind-visning. `wilsof-lock` sikrer én Hyprlock-prosess og brukes både av Super+L og Hypridle.

DMS og Hypridle er user-tjenester. Wilsof-session.target starter wallpaper etter DMS. Dette er oppstartsrekkefølge, ikke en loop eller sleep-baserte reparasjon.

## Boot

ESP er montert på `/boot`; systemd-boot installeres med `bootctl --esp-path=/boot install`. Installasjonsskriptet verifiserer NVRAM-loader, `EFI/BOOT/BOOTX64.EFI`, kernel/initramfs og root UUID/Btrfs-subvolum. `/boot` skal ikke gis som `--boot-path` siden den er ESP, ikke XBOOTLDR.
