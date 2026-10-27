# Next session — internal ISO and preserved VM 113 history

Updated: 2026-10-27 UTC

## Current entry point

- Use draft PR #27 and branch `integration/internal-iso-20261026`, not the historical branch below. Preserve unrelated work and acquire the existing worker lock before development.
- Read the [bounded close-out checkpoint](checkpoints/bounded-20261027.md) first; it supersedes active-work instructions in [post-reboot stabilization](checkpoints/post-reboot-20261027.md) and [earlier continuation](checkpoints/resume-20261027.md). Original candidate2 installation/shutdown/offline verification completed; do not query the obsolete installer PID or repeat installation.
- Existing disk-only boot, ordinary login, representative GUI/default GTK and genuine wrong/correct-password Hyprlock checks passed. Full package upgrade exposed issue #30; reviewed local-source fix `e38902b` passes actual config preservation/file recovery, but the immutable ISO still contains the original updater. Use the newest private checkpoint for VM ownership/shutdown/remaining gates before acting.
- Earlier [QA evidence](checkpoints/internal-iso-qa-20261026.md), [source composition](checkpoints/internal-iso-integration.json) and [runbook](internal-test-runbook.md) remain relevant history, not acceptance of the later artifact. Older-image GTK/Hyprlock evidence must not be promoted to final-candidate evidence.
- Reconcile the newest private checkpoint: original candidate2 is off; only the later owned diagnostic overlay/lock remain live pending human-operated shutdown. Do not bypass the tool power-operation block or attach the active overlay elsewhere. Next bounded code task: full-package validation and one real teardown test of the already-written Hypridle patch. No new broad investigation, default parallel agents or duplicate VM. Then one exact-source versioned internal ISO and actual artifact gates when necessary fixes are ready.
- Keep scheduled development paused and retain the original provider budget gate. Use only the verified subscription route; quota/auth failure means checkpoint/stop, not fallback.
- No merge, release, physical USB write or spare-PC installation is approved by this checkpoint. Obtain separate approval and verify disk ownership/identity before any such action.

## Historical VM 113 checkpoint — not today's test target

The observations below are retained from October 16 and must be reverified before use. Do not infer that the historical VM is reachable or unlocked now.

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
