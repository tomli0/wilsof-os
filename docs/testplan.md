# Test matrix — Arch prototype

A PASS only covers the stated method. “IPC” is not physical keyboard evidence.

| Area | Check | Status | Evidence |
|---|---|---|---|
| Base system | Installed Arch root, Btrfs, systemd-boot and fallback loader | PASS (static/SSH) | Prior VM inspection; recovery steps in `docs/vm-runbook.md` |
| Session | greetd, SSH, Hyprland, DMS and Hypridle running | PASS (SSH) | live process and unit inspection on VM 113 |
| Theme | approved wallpaper, charcoal, ice-blue, empty desktop and minimal bar | PASS (visual) | `evidence/vm113-2026-10-16-desktop.png` |
| Launcher | application-mode DMS launcher opens through installed wrapper | PASS (IPC/visual) | `dms ipc call launcher toggleWith apps`; launcher screenshot |
| Launcher | empty query and selected Firefox result | PASS (visual) | `evidence/vm113-2026-10-16-launcher-apps.png` and launcher evidence |
| Launcher | local file/window/settings/power universal search | NOT IMPLEMENTED / NOT TESTED | application mode is intentionally scoped |
| Launcher | keyboard arrows, Enter and Escape through physical client | NOT TESTED | requires actual console input |
| Settings | DMS Settings opens through Wilsof entry | PASS (IPC/visual) | `evidence/vm113-2026-10-16-settings.png` |
| Help | shared-manifest rendering in DMS Notepad | PASS (wrapper/IPC/visual) | `help-notepad-final-2026-10-16.png` |
| Help | close through supported DMS IPC | PASS (IPC) | `dms ipc call notepad close` returned success |
| Help | physical `Super+F1`, Escape and keyboard close | NOT TESTED | no physical-console observation |
| Bindings | declared Wilsof binding layer | PASS (static) | 33 local pytest tests cover source relationships |
| Bindings | actual physical key delivery | NOT TESTED | client may intercept Super |
| VM fallback | four Ctrl+Alt bindings shown as active | PASS (visual/static) | help screenshot and manifest |
| VM fallback | physical MacBook → Omarchy → Proxmox → VM path | NOT TESTED | requires human observation |
| System actions | DMS power menu and 500 ms confirmation visible | PASS (visual) | `evidence/vm113-2026-10-16-powermenu.png` |
| System actions | keyboard cancellation and destructive action safety | NOT TESTED | destructive action was intentionally not run |
| Applications | required package set installed | PASS (package query) | Firefox, Ghostty, Nautilus, GNOME Text Editor, Papers, Loupe and VLC |
| Applications | real graphical starts | PARTIAL | Firefox was shown in launcher; representative starts still need active-session tests |
| Portals/audio | portal backend and PipeWire/WirePlumber units | PASS (service) | live package/service inspection |
| Audio/screen sharing | playback and sharing user flows | NOT TESTED | no user-flow test |
| Lock setup | Hyprlock package, PAM file, approved transparent WS logo and Wilsof config present | PASS (static) | source tests verify the supported `image` block, asset alpha channel and installer deployment path |
| Lock surface | live configured Hyprlock display with the approved WS logo | RETEST REQUIRED | prior screenshot predates the logo change; requires a permitted local lock observation at 1280×800 |
| Unlock | PAM password authentication | NOT TESTED | must be entered locally by authorized human |
| Idle | one Hypridle service and 300-second listener | PASS (service/config) | live unit status and `hypridle.conf` |
| Idle | actual lock after five minutes | FAIL (before fix) / RETEST REQUIRED | prior logs: Hyprlock lacked config and exited |
| Wallpaper | desktop shows approved asset | PASS (visual) | desktop screenshots |
| Wallpaper service | fresh DMS IPC result after unit start | PASS (IPC) | DMS `SUCCESS`, `wallpaper get` returns approved asset, systemd result success |
| Wallpaper service | startup after new graphical login | NOT TESTED | requires logout/login or reboot observation |
| Persistence | logout/login and reboot observation | NOT TESTED | not yet performed |
| Local quality gate | unit tests, shell syntax, theme JSON and diff whitespace | PASS | `33 passed`; shell/JSON/diff checks |
| CI | GitHub Actions on current pushed commit | PENDING | must be rechecked after the final push |

## Physical-console checklist

1. Test `Super+Space`, type a query, use arrow keys, Enter and Escape; open Firefox.
2. Test `Super+I` and `Super+F1`; close help with the UI and try Escape.
3. Enable the optional layer only if needed, then test all four Ctrl+Alt fallbacks and disable it again.
4. Open the system menu and cancel every destructive confirmation.
5. When ready to enter the local password, test `Super+L`, confirm the centered WS logo above the clock has no rectangular sheet background and is unclipped at 1280×800, then wait five minutes for idle lock.
6. Only after all other GUI work is saved, perform a controlled logout/login or reboot and re-check the session.
