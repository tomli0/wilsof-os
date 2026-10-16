# Architecture — Wilsof Arch prototype

## Stack

Arch Linux → systemd-boot/UEFI → greetd/tuigreet → Hyprland → DankMaterialShell (DMS). Wilsof is a versioned override layer over DMS-generated Hyprland configuration, not a DMS shell fork.

DMS generates `~/.config/hypr/hyprland.lua`. The user-profile installer appends one marked `require("wilsof")` after DMS's own modules. `wilsof.lua` owns Wilsof colors, layout, agreed bindings and `wilsof-session.target`; it does not modify generated `dms/*.lua` files.

## Design tokens

Wilsof-owned surfaces use charcoal `#14181E`, ice-blue `#86B9CE`, cool white `#E7EEF2`, inactive outline `#3A424B`, moderate 8/10 px gaps, 6 px rounding and a one-pixel focused border. Upstream DMS controls are themed through its supported custom-theme file rather than a DMS fork.

DMS is the wallpaper owner. Wilsof supplies the approved asset and fixed custom palette. The DMS systemd drop-in disables Matugen so wallpaper extraction cannot overwrite Wilsof colors. The installer seeds a DMS `settings.json` only once; later normal upgrades preserve personal settings.

## User flows

`wilsof-search` is an argument-validated bridge to `dms ipc call launcher toggleWith apps`. It deliberately provides application discovery, not unverified universal search providers.

`wilsof-help` renders the shared JSON shortcut manifest into a local state file and opens it through supported DMS Notepad IPC. This avoids the active-session Ghostty `PostForkError` while preserving a single shortcut data source.

`wilsof-lock` starts Hyprlock only when the current user has no existing Hyprlock process. The same wrapper is used by Super+L and Hypridle. `hyprlock.conf` defines only the lock presentation; `/etc/pam.d/hyprlock` remains system-owned authentication policy.

DMS and Hypridle are user services. `wilsof-session.target` starts the wallpaper oneshot after DMS is requested. The wallpaper service must be verified for an actual successful IPC result, not only a systemd exit status.

## Boot

The ESP is mounted at `/boot`; install systemd-boot with `bootctl --esp-path=/boot install`. The installer validates the NVRAM loader, `EFI/BOOT/BOOTX64.EFI`, kernel/initramfs and root UUID/Btrfs subvolume. Do not treat `/boot` as an XBOOTLDR path.
