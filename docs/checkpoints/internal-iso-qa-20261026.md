# Internal ISO QA checkpoint — 2026-10-26

## Identity and scope

- Integration PR: https://github.com/tomli0/wilsof-os/pull/27 (draft, not merge approval).
- Image source: `21214fc4c0674775918cb5b36099616ef1bcedb5`.
- Composition: [exact included PR heads and conflict decisions](internal-iso-integration.json).
- Artifact: `wilsof-internal-2026.10.26-x86_64.iso`.
- Size: `2533040128` bytes.
- SHA-256: `82a26c119b51446123b44116689319bb5e1f5dfddedafe56a30b695a874b12d9`.
- Archiso 91; installed archinstall API 4.5; tested image packages include DMS 1.6.3-2, Quickshell 0.3.2-1 and Qt 6.12.0-3.
- Post-image documentation commits do not change the above image source or its bytes.

This is a local/internal engineering artifact, not a release or a statement that all desktop/hardware checks passed. No PR was merged, issue closed or feature marked Done. PR #26's worker/Terra changes are excluded. Proxmox and the existing VM 113 were not modified.

## Execution and spending boundary

The live parent session and six independent-review child sessions report `openai-codex`, `gpt-6.1-sol`, `subscription_included`. Parent reasoning is `medium`; stored OAuth mode is `chatgpt`. Auxiliary routes are explicitly pinned to the subscription model with empty fallback chains. Delegation inherits this route. No OpenRouter/Terra reviewer command was executed.

Scheduled job `8df95a6101e7` remains disabled/paused; existing worker control remains `paused=true`, `stop_requested=false`. The OpenRouter budget gate, approval rules, worker locking/retry/time limits and existing spending limits were not replaced. Do not invoke the worker's `--status` under a no-OpenRouter-contact boundary: that implementation contacts its budget endpoint.

## Automated and source verification

- 145 local pytest tests passed on the image source.
- ShellCheck passed for the build/profile/user-config/doctor/update wrappers; `git diff --check` and repository JSON parsing passed.
- GitHub validation for exact image source succeeded: run `40343856847`.
- Independent security review passed after target containment and live-only lock policy corrections.
- Independent installer re-review passed after checking the actual archinstall 4.5 locale behavior. `minimal_installation(locale_config=None)`, explicit vconsole setup and one checked locale call avoid the previous deterministic duplicate-call failure.
- The ISO was built from a clean `git archive` export, not the mutable development directory.
- The immutable rootfs was inspected separately from the runtime VM: expected source marker and root-owned executable installer/update entrypoints are present. The path scan found no SSH authorization/private-key files, GPG private-key files, development-account paths, auth files or Git metadata. This is a scoped artifact inspection, not a universal malware/security audit.

## Actual boot/install results

All VM observations below used a newly created, dedicated local QEMU/OVMF machine, TCG, four virtual CPUs and 4096 MiB RAM. No host directory, physical disk, existing VM disk, SSH key or host credential was attached. No SSH forwarding was configured.

### Live ISO

- Candidate 3 booted 64-bit UEFI from optical emulation.
- Live greetd, NetworkManager and guest agent were active.
- Approved WS wallpaper was returned by owning DMS IPC and visually observed.
- GNOME automatic volume mounting was confirmed disabled.
- Installer/update entrypoints were root-owned mode 755.

### Installation

- The only target was the new 24 GiB virtual disk `/dev/vda`, synthetic serial `WILSOF-QA-20261026`.
- Read-only preflight verified its identity, size, absent partitions/signatures/mounts and the live environment before the installer was invoked.
- The stock installer rechecked the zero-filled disk and repeated its identity/blankness guard immediately before formatting.
- Five interactive prompts were answered through a synthetic PTY, including explicit `ERASE /dev/vda` confirmation. This is not a physical keyboard test.
- A unique private QA password was supplied privately on stdin, not in arguments or a plan. Transcript inspection found no plaintext password.
- Installation completed with exit code 0. Locale, initramfs, systemd-boot fallback, account, configuration, services and fstab phases completed.
- Preboot checks confirmed a locked root account, a normal UID-1000 user with a password hash, no live/development accounts, no autologin, no copied SSH credentials, a distinct machine-id state and `EFI/BOOT/BOOTX64.EFI`.

### Installed-disk-only boot

- The VM was powered off and restarted with the installed disk only: no ISO and fresh factory OVMF variables.
- Root was `/dev/vda2 ext4`, kernel `7.2.11-arch1-1`; live Archiso mount was absent.
- greetd, NetworkManager and guest agent became active without post-install enablement or repair.
- Normal greeter password authentication into a UID-1000 Hyprland session succeeded twice using synthetic keyboard input. This was not root `runuser` substitution for login.
- Actual mapped Firefox and GNOME Text Editor clients were observed. Firefox rendered a clearly identified local HTML test fixture; it was not fabricated live web content.
- DMS Notepad visibly rendered the actual generated Wilsof shortcut help.
- The launcher visibly found Firefox as an application; synthetic Enter closed the launcher. Existing Firefox windows remained, so a newly spawned browser process is not claimed for that action.

### Raw USB mass-storage emulation

- The exact durable ISO was booted again using a read-only `usb-storage` device, not a CD-ROM, with fresh OVMF variables and no target/installed disk attached.
- Live root started in 64-bit UEFI. `/run/archiso/bootmnt` was `/dev/sda1`, `iso9660`, read-only; the only disk reported USB transport and read-only state.
- greetd/network services and the approved wallpaper were confirmed again.
- The live account's exact passwordless installer permission was checked with `sudo -n -l /usr/local/bin/wilsof-install`.
- This proves emulated USB boot, not any physical USB stick, firmware or PC.

## Updates and limited recovery actually exercised

On the installed system:

1. `pacman -Syu --noconfirm --color never` completed with exit 0; databases synchronized and the result was `there is nothing to do`. No package-version upgrade is claimed.
2. `wilsof-config-update /usr/share/wilsof/source` ran as the normal desktop user, without sudo.
3. An explicitly altered Wilsof-owned helper was restored to its reviewed content; an actual personal `clockFormat=24h` setting was preserved byte-for-byte.
4. The changed helper's timestamped backup was checked against the pre-update content.
5. Manual per-file recovery from that backup was exercised, then the reviewed update was reapplied successfully.

These are configuration-file backups, not transactional OS rollback, boot rollback or package rollback. See the [test/update runbook](../internal-test-runbook.md).

## Remaining issues and honest limits

- GTK default software rendering in the TCG VM produced a mapped but largely blank editor surface. Text was observed with a temporary, per-process `GSK_RENDERER=cairo` diagnostic. The image's default renderer was not changed; do not call its default editor rendering passed.
- Automatic idle locking and the branded Hyprlock surface were observed. Synthetic QEMU password input did not produce a verified unlock; one actual PAM failure was recorded. The same private password subsequently authenticated successfully through an unprivileged `su` check, without plaintext output. Cause of the GUI unlock failure is not isolated. A test-only session was administratively logged out before the second normal greeter login; do not misreport that as an unlock.
- First-launch DMS changelog had a blank body under software rendering. It was dismissed by a synthetic pointer click after closing an overlapping launcher. Cold GUI initialization and repainting were slow; successful IPC alone is not visual evidence.
- Representative core apps/help/launcher were observed, but this is not comprehensive application usability testing.
- No physical keyboard, Mac/PC modifier mapping, audio, Wi-Fi/Bluetooth, GPU driver, suspend/resume, physical USB firmware boot or spare-PC installation was verified.
- Local KVM and a host render node were unavailable; existing Proxmox access was unreachable. These limitations do not establish the cause of every GUI failure.

## Durable handoff

The ISO, SHA256SUMS, manifest, runbook and selected sanitized evidence are retained outside ephemeral scratch in the internal artifact directory. The installed disposable disk and firmware checkpoints remain preserved separately. QA credentials are not shipped with the artifact.

Both test VMs were cleanly powered off. No scheduled development should be resumed automatically.

Next: investigate/retest GTK default rendering and normal Hyprlock input/unlock on a suitable accelerated disposable VM or controlled physical live session. Require separate explicit approval before writing any USB or installing on the spare PC. Do not repeat a full build/install merely to reproduce a GUI observation; use the preserved checkpoints and the same verified ISO where applicable.
