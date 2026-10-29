# Candidate 2 installed-system stabilization — 2026-10-27

## Identity and preserved boundaries

- Continue draft PR #27, branch `integration/internal-iso-20261026`.
- Unchanged image source: `e2561399e5ac5add3711549f9c48e1bcab1486d1`.
- Existing ISO: `wilsof-internal-2026.10.26-stabilize2-x86_64.iso`, 2,539,565,056 bytes, SHA-256 `6c909c5f9e78c0326e999fc3977f66164157df19d320a86c6f136ae3f72aeebd`.
- The controlled-shutdown disk/ISO/firmware hashes matched before first boot. Read-only qcow2 check passed. Installation had exited 0 after five PTY prompts, with no plaintext password in captured terminal output; it was not repeated.
- Ubuntu restart resource check: approximately 16 GB configured RAM (15 GiB visible), 97 GB root filesystem, 50 GB available.
- Existing exclusive worker lock held throughout VM ownership. Scheduler disabled/paused and worker paused; budget/approval/retry controls unchanged.
- Parent and independent reviewer billing verified as `openai-codex` / `subscription_included`. No paid fallback.
- No ISO build, reinstall, merge, release, issue closure, Done transition, physical disk/USB or Proxmox/VM113 change.

## Actual candidate 2 installed boot and GUI evidence

The existing installed 24 GiB virtual disk was booted with no ISO attached and fresh factory OVMF variables. The original installed variables were separately preserved. QEMU used TCG, two vCPUs, 6144 MiB RAM and `Nehalem`, the earlier documented software-emulator workaround. No guest application renderer override was set; this does not validate the original `-cpu max` path or physical GPU behavior.

- Root `/dev/vda2` ext4; no Archiso live mount. Source marker exactly matches the image source. UEFI fallback present.
- Root locked, ordinary UID-1000 password account, no live account or greeter autologin. greetd, NetworkManager and guest agent active without repair. Network reports connected/full; external DNS resolves.
- Actual greeter username/password input opened an ordinary Hyprland user session; root `runuser` was not used as login evidence.
- DMS top bar and approved WS wallpaper visibly rendered. Cold software startup/repaint took minutes, with initial incomplete frames and temporary IPC timeouts; eventual owning state and screenshots were checked separately.
- Real synthetic Super+F1 displayed the generated shortcut help; Super+I displayed readable settings. Super+Space queried Ghostty, and synthetic Enter launched a new mapped Ghostty with a visible shell prompt.
- Text Editor rendered a local fixture including Norwegian characters using its default GTK renderer. Nautilus rendered the actual fixture directory. Their process environments had no renderer overrides.
- Actual Super+L started installed Hyprlock. A temporary crashed-lockscreen notice during cold initialization was followed by the normal branded password surface while the original locker remained alive; no coredump was found. A deliberately wrong password caused a PAM failure and left the locker running. The private correct password then exited that locker and restored the same session and applications, without killing the locker, clearing the crash state or logging out. Normal shortcut stdout/stderr was `/dev/null`, so no unavailable verbose success line is claimed.
- After the real package upgrade, a second ordinary greeter password login started the upgraded shell. Clock preference and WS wallpaper persisted. Actual Super+F1 rendered complete help with its visible close control under Dux 2.
- The upgraded power menu was visibly inspected, then closed by IPC without selecting any power action. This is not proof of keyboard hold-confirm behavior.

Private durable evidence includes named screenshots, owning-state outputs, authentication journal, artifact/check results and read-back GitHub records. QA credentials and disk images remain private and are not shipped with the ISO.

## Real package upgrade and compatibility failure

`pacman -Syu --noconfirm --color never` completed with exit 0. This was NOT a no-op: `dms-shell 1.6.3-2` was removed and `dux-shell 2.0.0-1` installed. No kernel change occurred. The running pre-upgrade shell and the later upgraded-shell session are separate evidence.

The Dux CLI migrated `.config/DankMaterialShell` to the literal relative symlink `dms`. The immutable image's `wilsof-config-update /usr/share/wilsof/source` failed at the existing symlink guard. Some earlier managed files had already been restored before that error; this updater is not transactional. Settings bytes were retained. Issue #30 records this final-artifact limitation.

The upgrade command accepted a major replacement without a separate transaction-preview/news gate. That is a QA procedure limitation; a successful package transaction is not a compatibility guarantee. Future tests should review the proposed replacements before noninteractive confirmation.

## Reviewed local-source recovery, not a rebuilt image

Source fix `e38902bee7b6efdc31ed137b34f16f4ac475d72d` selects the confined canonical settings path ONLY for the literal known `dms` alias. It does not allow arbitrary symlinks. Tests reject `./dms`, absolute aliases, external links, linked ancestors/canonical directories/settings. Migrated live settings retain unrelated preferences, receive all live lock-policy overrides and have their original canonical bytes backed up.

- Exact symptom regression observed RED before the fix, then GREEN.
- Full suite: 163 passed. Scoped static security scan and `git diff --check` passed.
- Independent security/logic review passed with no blocking findings; suggested test additions were included. Reviewer subscription billing was independently checked.
- Exact fix-head CI run `40573275214` passed.
- A clean archive of that committed source was transferred to a new user-owned local review directory. Initial oversized QGA exec transfer failed before extraction; bounded guest-file writes, hash verification and unprivileged safe extraction then succeeded. No host credentials or private test data were included.
- The ordinary desktop user ran the original `wilsof-config-update` command against that reviewed local source. It exited 0, restored an explicitly modified harmless owned helper, preserved the real `clockFormat=24h` settings bytes, and produced a byte-identical helper backup. Manual per-file recovery from the backup and reviewed reapplication both passed.
- Root-owned installed source marker remains the original image source. The ISO and immutable bundled updater have NOT been changed. This is verified local-source remediation of an installed system, not final-artifact acceptance or transactional rollback.

## Remaining verification and handoff

- Five-minute automatic idle lock activated without further QEMU input. A later branded surface appeared after prolonged TCG initialization and an emergency notice. Wrong password was rejected; correct password produced `auth: authenticated for hyprlock`, locker exit and the same session/Firefox desktop. This is a functional pass, not an acceptable-latency or physical-security certification.
- Firefox visibly rendered the explicitly labelled local HTML fixture; no live web-content claim.
- Preserved coredumps: hypridle SIGABRT during session teardown and `hyprland-update-screen` SIGSEGV during the next login. Issue #31 tracks these and cold TCG lock latency; root causes remain unproven. No hyprlock coredump was found. Final main shell/compositor/idle services were active.
- Final controlled guest poweroff was blocked before execution by the tool's unconditional shutdown/reboot policy. Do not bypass it. The owned QEMU guest and exclusive-lock supervisor remain running; a human must power off this guest from an external terminal. Do not attach/check its active disk elsewhere. Offline post-test qcow2 check and final disk/firmware hash remain pending until that exit is verified.
- The private checkpoint records the exact VM/supervisor PIDs, durable launch/sockets, disk, current firmware and completed evidence. The existing installation is preserved with the actual package/config test changes. Scheduler and worker remain paused.
- Candidate 2 is not unconditionally accepted: its bundled updater fails after the demonstrated major upstream migration. Source fix is available separately in draft PR #27; no new ISO build/install is authorized merely by this checkpoint.
- Physical USB/UEFI, keyboard/modifier mappings, GPU, Ethernet/Wi-Fi, audio/microphone, Bluetooth, suspend/resume and spare-PC installation remain unverified owner-only gates. Cold TCG performance and selected application checks are not a broad usability certification.
