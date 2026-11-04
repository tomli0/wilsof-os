# Deviations and known limits

## Resolved

- The DMS-generated bindings conflicted with Wilsof bindings. Wilsof now removes the relevant generated bindings before registering its own overrides.
- Hypridle did not find `wilsof-lock` because its user-service PATH omitted `~/.local/bin`. The idle configuration now calls the wrapper by absolute user path.
- The shortcut-help path used Ghostty with `--command`. In the running Arch session Ghostty 1.3.1 created a non-functional terminal with `PostForkError` and a configuration-error dialog. Help now uses supported DMS Notepad IPC and the existing shared manifest; it no longer depends on Ghostty.
- The Command glyph was missing in the DMS Notepad font. The help text now says “Command key” rather than rendering the unsupported glyph.

## Current limits

- DMS Launcher is deliberately application-focused. It is not presented as a complete universal search until local files, open windows, settings, aliases and power actions have been individually tested through a supported provider path.
- DMS has no supported launcher widget in the installed minimal top bar. Wilsof does not add a decorative or fake search button.
- DMS and several upstream views have English category labels. Wilsof does not fork DMS for translation.
- A historical wallpaper oneshot run reached DMS before the target was available. The unit now directly requires DMS; a fresh manual start returned DMS `SUCCESS`, the expected `wallpaper get` value and systemd success. Login/reboot startup ordering still needs a real persistence test.
- Hyprlock's PAM file exists and a Wilsof lock configuration is installed. Unlock requires a human entering the account password locally; the agent does not collect or enter it.
- VM keyboard interception, idle lock, logout/login and reboot persistence require direct physical-console checks.
- The KVM test VM has no battery, ACPI platform-profile, or CPU-frequency interface. Before remediation DMS returned the exact status `ERROR: power-profiles-daemon not available`; the `power-profiles-daemon` package, system unit, and `net.hadess.PowerProfiles` D-Bus name were absent. The supported backend is now installed in VM 113 and new-image manifests; after a bounded DMS reload IPC returned `balanced`. Visual DMS control observation and physical laptop battery, thermal, or hardware-profile effects remain untested.

## Boot history

The active Arch disk uses an ESP at `/boot`, systemd-boot with fallback `EFI/BOOT/BOOTX64.EFI`, and Btrfs root parameters. The earlier failed disk boot was not retained, so its exact cause is unknown. The installation recipe validates the observed boot artifacts statically; it is not a substitute for a real reboot observation.
