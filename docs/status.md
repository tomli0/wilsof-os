# Status — Wilsof Arch prototype

Updated: 2026-10-28 UTC (autonomous session checkpoint added)

## Current bounded checkpoint — installer bug #34

- Draft PR #27 / `integration/internal-iso-20261026` contains the bounded target-chroot correction. Read [root cause and verification](checkpoints/pacman-chroot-fix-20261028.md). No merge or new ISO build in this correction task.
- Actual `2026.10.28-internal1` ISO source is `98bda89c453365b9fc51a0b40ad4174c40b4af8a`, 2545111040 bytes, SHA256 `ab78770ce5c4c5fe8b7b913263ade47e4f2d8830a4ffbb6a38c935c9e9a45e83`. Its installation FAILED with exit1; it does not contain this later correction and is not accepted for installation.
- Root cause is bare chroot without target API mounts: the intact `/etc/mtab -> ../proc/self/mounts` link cannot resolve. The correction uses `arch-chroot -r` for external target commands and executes directly in the already prepared live/build root. Storage/authentication/signature guards are unchanged.
- Code regression passed RED/GREEN; 175 tests and static checks pass. Real isolated native Pacman upgrade, API setup/teardown, injected setup failure and unprivileged execution-context checks pass. No full reinstall, new VM or artifact acceptance claimed; independent review remains pending.
- Previously completed Hypridle harness (14/14 normal and 14/14 UBSan) and actual daemon teardown are recorded in [milestone A](checkpoints/hypridle-regression-20261028.md). The native package was reused, not rebuilt. #31 remains open for its explicit remaining lifecycle/latency/artifact gates.
- Original failed-install guest and supervisor exited cleanly, target was safely unmounted, offline qcow2 check passed, and disk/firmware/ISO/logs are preserved. This task uses only a separate disposable chroot clone, never repairs the preserved disk.
- Next gate requires separate authorization: review the correction, build a new versioned internal ISO and validate its actual installation/disk-only boot/authentication. #30 installed updater/preservation and installed lock gates remain pending for that future image.
- Scheduler/automatic worker remain paused. No main/arch-install merge, release, paid fallback, physical disk/USB or Proxmox change. Engineering Standards is a separate documentation workstream and is not changed here.

Earlier dated sections below are historical observations, not current ISO acceptance.

### Session checkpoint — 2026-10-28 autonomous QA/build session

- Independent review of commit b3b8e74 by the configured reviewer route (Claude Sonnet 4.6 via OpenRouter) was dispatched and its findings are recorded in the private QA checkpoint (`~/.local/state/wilsof-qa/autonomous-20261028-1311/claude-qa-findings.json`); this status will be finalized when the review completes.
- Planned new versioned ISO build (intended `2026.10.28-internal2`) is BLOCKED on host storage: 5.6 GiB free versus the 25 GiB minimum in `docs/iso.md`. Zero build attempts were made; no QEMU guest was started. Earlier ISOs, disks, firmware and evidence are preserved unchanged.
- Engineering Standards documentation completed on `docs/engineering-standards-20261028` and opened as draft PR #35 targeting this branch; separate from integration work.

## Historical internal ISO checkpoint — 2026-10-27

- Continue draft integration PR #27 on `integration/internal-iso-20261026`; no shared branch was merged and no feature is marked Done.
- Current artifact remains candidate 2 from `e2561399e5ac5add3711549f9c48e1bcab1486d1`. Read the [controlled session close](checkpoints/session-close-20261027.md) first; earlier checkpoints remain history. No new ISO/reinstall occurred.
- A full native Hypridle verification package now builds and its packaged CLI/ELF/linking checks pass. Recipe/patch/provenance are preserved. The portable regression entry point is explicitly WIP and real-session teardown is unverified; #31 remains open. The session is closed, not dispatching more work.
- Existing-disk-only UEFI boot, ordinary greeter password login, WS desktop, synthetic help/settings/launcher/terminal and default GTK rendering passed. Installed Hyprlock rejected a wrong password and genuinely unlocked the same session with the correct one.
- Real full package upgrade replaced DMS 1.6.3 with Dux 2.0 and exposed a config-migration failure in the immutable bundled updater (#30). Separately reviewed source fix `e38902b` passed 163 tests, exact-head CI and actual local-source config preservation/backups/manual file recovery. The ISO does not contain that fix; it is not unconditionally accepted.
- Earlier-image and candidate1 results remain historical; candidate2 and post-upgrade evidence are separated in the checkpoint.
- Physical hardware/USB/keyboard/audio/Wi-Fi/suspend checks remain unverified. Five-minute automatic idle lock and genuine post-upgrade unlock passed functionally, with severe cold TCG rendering delay; upstream crash/latency follow-up #31 remains open.
- Both original candidate2 and the diagnostic overlay guest are now cleanly powered off. The diagnostic helper completed at 22:44 UTC, QEMU/supervisor exited 0, offline overlay check returned 0 and overlay/firmware hashes were verified. No protected test process remains; the supervisor released the exclusive lock. All artifacts are retained.
- Development scheduler and worker remain paused. The live session verified Codex subscription billing; no paid fallback or Proxmox/VM 113 change.

## Historical VM 113 baseline — 2026-10-16

The following records are historical observations, not assertions of current reachability, login state or deployment. The October 26 session could not reach the existing Proxmox environment and used a separate local disposable VM instead.

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
