# WS screensaver decision and preview

## Decision

The current Wilsof configuration keeps Hypridle as the sole idle authority and Hyprlock as the sole PAM-backed lock surface. The five-minute `hypridle` listener continues to invoke `wilsof-lock`; `Super+L` continues to invoke that same wrapper directly. This change does not add a timer, alter display-off policy, or route input around Hyprlock.

The installed Hyprlock configuration cannot safely host this preview: its documented animation tree covers lock-surface fade and input-field effects, and its documented background image formats are non-animated. It is a session-lock client with PAM authentication, not a general-purpose external-surface compositor. A separate fullscreen preview would be unlocked and must never be presented as a lock screen. Therefore no idle integration is installed.

DMS has its own idle/session facilities upstream, but Wilsof already has Hypridle configured. Enabling a second idle manager would create competing lock timers and could change inhibitor handling. It is explicitly out of scope.

## Approved asset and derived mask

The source is `assets/Wilsof OS-logo med geometrisk WS-monogram.png`. Its left-side ice-blue angular WS mark was inspected; the derivation samples only that mark (not the `wilsof.os` wordmark) into `assets/ws-ascii-mask.json`. The original PNG is untouched. `prototype/screensaver.html` uses the matching mask as quiet monospace particles on `#14181E` with `#86B9CE` accents.

## Safe preview

Open `prototype/screensaver.html` through a local browser or static server. It demonstrates formation, a short hold with gentle drift, dissolution, and repetition. The controls provide static/reduced-motion behavior and disable. Any key or pointer activity dismisses the preview. It has no session, PAM, D-Bus, Hyprland, display-power, or lock integration.

A production secure integration is blocked pending a supported upstream mechanism that can render the animation inside Hyprlock without changing its authentication or session-lock role. Do not solve that by layering this prototype over the desktop or on top of Hyprlock.

## Verification record

| Check | Status | Evidence |
|---|---|---|
| Derived mask preserves original asset | PASS (static) | `assets/ws-ascii-mask.json` names the source and method; original asset is unmodified |
| Formation, drift, dissolution and repeat implemented | PASS (static) | `prototype/screensaver.html` has a 18-second `cycle` keyframe animation |
| Static/reduced-motion and disable controls | PASS (static) | control buttons plus `prefers-reduced-motion` rule |
| Existing secure lock and single idle authority retained | PASS (static) | `config/hypr/hypridle.conf`, `config/hypr/wilsof.lua`, and `bin/wilsof-lock` remain the only lock path |
| Real browser/VM visual capture | NOT TESTED | requires a graphical client; generated mockups are not evidence |
| Idle-inhibitor, real five-minute timeout, Super+L, locked input and PAM unlock | NOT TESTED | requires an authorized physical/client session; do not automate authentication or disruptive lock tests |
| Resource observation at target resolution | NOT TESTED | requires the running graphical client |

## Upstream references checked

- Hyprlock documentation: https://wiki.hypr.land/hypr-ecosystem/user/hyprlock/
- Hypridle documentation: https://wiki.hypr.land/hypr-ecosystem/user/hypridle/
- DMS IPC documentation: https://github.com/AvengeMedia/DankMaterialShell/blob/master/docs/IPC.md
