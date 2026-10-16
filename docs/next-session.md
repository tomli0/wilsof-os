# Next session — Wilsof Arch VM 113

Updated: 2026-10-16 UTC

## Checkpoint

- Branch: `arch-install`; confirm `git rev-parse HEAD` before new work.
- VM 113: `wilsofdev@192.168.10.250`; pin the ED25519 host key `SHA256:0IOuFZDTGymRZzoa5kSAO1x8FCo+ZO1khL3q/xqNAqw` before connecting.
- The current session is unlocked. The authorized local user manually authenticated to Hyprlock successfully at 17:45 CEST. This confirms only that one local authentication/unlock; it does not validate idle locking or suspend.
- SSH inspection found active greetd, Hyprland, DMS, Wilsof session target, Hypridle and Hyprland portal. Root filesystem is Btrfs `/dev/sda2[/@]`.

## Current development findings

- Ghostty 1.3.1-2 launched successfully inside the active Wayland session, was listed by Hyprland, and ran a harmless command. No `PostForkError` occurred in this reproduction.
- The observed Ghostty configuration error was reproduced as the zero-byte `~/.config/ghostty/config.ghostty`: Ghostty logs `error.FileIsEmpty`. The empty file was backed up under `~/.local/state/wilsof-os/backups/ghostty/`, then replaced with a comment-only harmless configuration; no personal setting was overwritten.
- `Super+Space` now invokes DMS Spotlight rather than apps-only launcher. Empty search visibly begins with applications and local DMS tools/settings; file mode explicitly reported that the supported `dsearch` provider is absent. Open-window search and complete power-action search are still not implemented.
- `wilsof-doctor` is installed and read-only. It reports packages, Wilsof files, Ghostty empty-config hazard, user/session units and journal locations.
- `iso/` plus `scripts/build-iso.sh` prepares an internal Archiso overlay. No ISO was built, published or installed; see `docs/iso.md`.

## Exact remaining checks

1. One controlled reboot was completed after commit `8c7628d`. SSH returned, the pinned ED25519 fingerprint matched, root remained `/dev/sda2[/@]` Btrfs, and `greetd` is enabled/active with `tuigreet --cmd Hyprland`. The VM is intentionally stopped at the greetd login; DMS, Hypridle, Wilsof target and wallpaper await the next authenticated graphical session.
2. Physically test `Super+Space`, arrows, Enter and Esc; then DMS power menu keyboard navigation/cancellation and the 500 ms hold explanation without running a power action.
3. Install/configure `dsearch` only on a separately approved disposable target if file search is required; the current VM does not provide it. Do not claim complete universal search until files, windows and actions are demonstrated.
4. Observe actual five-minute idle lock and suspend independently from the manually confirmed direct Hyprlock unlock.
