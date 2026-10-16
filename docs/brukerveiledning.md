# Using Wilsof

## Open applications

Press `Super+Space`. Wilsof opens DMS Launcher in application mode. Type an application name, use the arrow keys to select a result and press `Enter` to open it. The launcher is intended for local application discovery; Wilsof does not send the query to web services.

`Super` is the Command key on many Mac keyboards and the Windows key on PC keyboards. Press `Esc` to cancel the launcher; physical-keyboard confirmation is still recorded separately in the test plan.

## Find settings

Press `Super+I` to open DMS Settings. It exposes appearance, wallpaper, theme and colors, typography and motion, Hyprland, bar and workspace settings. Wilsof preserves an existing personal DMS `settings.json` during normal upgrades.

## Get help

Press `Super+F1`. Wilsof renders the shared shortcut manifest into a local DMS Notepad page. The page explains Super, lists standard bindings first and shows the optional VM bindings only when they are active. Close the page with its visible `X` control. It does not require network access.

## Workspaces and windows

- `Super+1` through `Super+9`: switch workspace.
- `Super+Shift+1` through `Super+Shift+9`: move the active window to a workspace.
- `Super+Arrow keys`: move focus.
- `Super+Shift+Arrow keys`: move the active window.
- `Super+Ctrl+Arrow keys`: resize the active window.
- `Super+Q`: close the active window.
- `Super+F`: fullscreen.
- `Super+Shift+Space`: toggle floating mode.

The ice-blue border identifies the active window. The top bar shows workspace orientation, time and essential status; it intentionally avoids a dock and desktop widgets.

## Lock and power actions

`Super+L` invokes Wilsof's Hyprlock wrapper. Hypridle invokes the same wrapper after five minutes and before suspend. Hyprlock uses the system PAM configuration; enter the account password locally to unlock. Do not place passwords in configuration files or project documentation.

The DMS system menu includes lock, log out, restart, power off and suspend. DMS displays a 500 ms hold confirmation before the destructive actions. During testing, cancel those confirmations rather than executing a destructive action.

## Power profiles

DMS uses the system `power-profiles-daemon` D-Bus service for its power-profile control. Wilsof installs that backend in new test VMs; it does not install or enable TLP, TuneD, auto-cpufreq, or another competing power manager.

If DMS says `ERROR: power-profiles-daemon not available`, the backend is missing or not reachable on D-Bus. Run `wilsof-doctor` and inspect `journalctl -b -u power-profiles-daemon.service`; do not treat a profile label alone as proof of reduced power use.

The test VM runs under KVM and exposes neither a battery nor an ACPI platform-profile interface. It is therefore an integration check for the D-Bus backend and DMS unavailable state, not evidence of laptop battery life, thermals, or a hardware performance profile. Use physical laptop hardware for those measurements.

## Optional VM fallback bindings

Some VM clients intercept Super before the guest receives it. From a graphical Wilsof terminal, enable the optional layer:

    wilsof-vm-test-binds enable

The following guest-only fallbacks then become available:

- `Ctrl+Alt+Space`: launcher
- `Ctrl+Alt+L`: lock
- `Ctrl+Alt+I`: settings
- `Ctrl+Alt+F1`: help

Disable the layer when the test is complete:

    wilsof-vm-test-binds disable

The fallback layer never changes the standard Super bindings. A physical keyboard test through the actual client and VM remains the only proof that client-side interception is solved.
