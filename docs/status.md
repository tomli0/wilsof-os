# Status — Wilsof Arch prototype

Updated: 2026-10-16 UTC

## Access and deployment

- VM 113 is reachable as `wilsofdev` with the existing public-key SSH setup and strict host-key checking. Root SSH remains available through its existing authorized key. Password login and sudo policy were not changed.
- The live target is Arch Linux with Hyprland 0.56.2 and DMS 1.6.3. After the controlled reboot it is intentionally at the greetd/tuigreet login; do not claim a new graphical session until it is observed.
- The original deployment under `/opt/wilsof-os` had no Git metadata. The current working-tree changes to help and Hyprlock configuration were copied there and installed as `wilsofdev`; installed files were compared byte-for-byte after installation.
- `wilsof-wallpaper.service` is a completed `Type=oneshot` unit, so `inactive (dead)` is expected after a successful run. It now directly requires DMS, and a fresh manual start returned DMS `SUCCESS`, the approved asset through `wallpaper get`, and systemd `Result=success`/`ExecMainStatus=0`. Startup behavior after a new graphical login still needs persistence testing.

## Implemented and visually observed

- Empty desktop, approved WS wallpaper, charcoal `#14181E`, ice-blue `#86B9CE`, thin borders and restrained DMS top bar were visually inspected in the running VM.
- `Super+Space` calls `dms ipc call spotlight toggle`. The visible Spotlight opens focused, begins with applications/DMS tools and has Apps, Files and Plugins categories. DMS reported that its supported local file provider (`dsearch`) is absent, so no file-search capability is claimed.
- `Super+I` opens DMS Settings. Wallpaper, theme and colors, typography and motion, Hyprland, bar and workspace categories were visually inspected.
- The original Ghostty shortcut help was broken in the active session: Ghostty 1.3.1 produced `PostForkError` and a configuration-error dialog. Wilsof help now renders the shared shortcut manifest into DMS Notepad through supported DMS IPC. The deployed page was visually inspected, including standard bindings, Super explanation, active VM-test section and visible close control.
- A Wilsof Hyprlock configuration is installed. `/etc/pam.d/hyprlock` is present and includes the system `login` PAM stack. The user manually authenticated with the local password and unlocked successfully; this is explicitly one direct unlock observation, not idle/suspend validation.
- Ghostty 1.3.1-2 opened as a normal active-session Wayland client and ran a harmless command. The observed configuration warning was tied to a zero-byte optional config file; its empty original was backed up and replaced with a comment-only file, preserving settings.

## Evidence

- `evidence/vm113-2026-10-16-desktop.png` — desktop/top bar.
- `evidence/vm113-2026-10-16-launcher-apps.png` — installed application launcher.
- `evidence/vm113-2026-10-16-settings.png` — DMS Settings.
- `evidence/vm113-2026-10-16-powermenu.png` — power menu confirmation.
- `evidence/vm113-2026-10-16-help.png` — deployed local shortcut help at 1280×800.
- `evidence/vm113-2026-10-16-lock.png` — deployed Hyprlock surface at 1280×800.

## Not yet passed

- The current launcher is application-focused, not a verified universal search for files, open windows, settings and system actions.
- Physical MacBook → Omarchy → Proxmox → VM keyboard behavior, including Enter/Escape, remains untested.
- DMS Notepad help opening and IPC close were tested; physical `Super+F1`, `Esc`, and keyboard closure of the help view remain untested.
- The Hyprlock surface, local PAM unlock, five-minute idle lock, logout/login, reboot persistence, audio playback and screen sharing remain untested.
- This is engineering validation and visual review, not usability testing with new people.
