# Private3 exact-image checkpoint — 9 November 2026

Status: **REPLACEMENT NO-GO; NOT QEMU ACCEPTED overall.** The completed Private3
ISO is no longer merely a build receipt: its exported bytes were independently
hashed/audited and all 18 basic virtual functional gates passed. A reproducible
portal SIGSEGV on normal logout fails additional stability acceptance.

## Immutable and source identities

- Frozen image source: `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261`.
- Filename: `wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso`.
- Size: 2,813,849,600 bytes.
- SHA256: `111c06b70cf6d909b3e815975f69bfa18f299af9dcfe9bbbfd5e197992c53a59`.
- Existing immutable provenance tool PASS: 64 independent payload files and 815
  package records. Exhaustive read of 154,754 regular SquashFS members PASS.
- Actual UEFI/EFI/kernel/initramfs, cowspace, executable modes, wl ABI/dependencies,
  policy/initramfs inclusion and absence of shared DKMS MOK files checked.
- Overall immutable completion is PARTIAL: full required-notice inclusion remains
  open, including a Dux package file list with no standalone license file.
- New source-only correction: `435e2cdca517ec8a6c33e1a83fb2098a07a031f3`, clearer
  manufacturer/model/transport/removable identity in destructive review. No
  eligibility relaxation; 786 source tests PASS / 3 opt-in SKIP; bounded independent
  AI-context review PASS. The frozen ISO does not contain this correction.

## Actual new-image runtime

New blank no-backing 24 GiB disk only, no historical installation disks or physical
block devices. Installer exit 0 after 443.045 seconds and five genuine prompts;
GPT, 1 GiB FAT32 ESP, ext4 root, systemd-boot fallback, ordinary administrator and
no autologin. All 18 basic functional gates PASS. Two disk-only cold-boot lifetimes,
normal reboot/fresh password login, ordinary logout/relogin, two manual native
locks and a 182.082-second observed idle lock were exercised.

Nine applications rendered. Keyboard/logo menu routes, search/navigation,
workspaces 1–9, window cycling, native wrong/correct-password controls and same-shell
menu recovery passed. Shortcut backend apply/read-back/real-key/default-restore
passed. Network, sound, Bluetooth, display and software interfaces rendered;
virtual sound was Dummy Output and Bluetooth had no adapter.

Installed version/doctor/update-preflight passed. Two actual sudo/PAM full updates
were no-ops on the unchanged 2026-11-01 snapshot. Native source/lock/signature
refusals, sudo interruption, optional signed package install/remove and seven
configuration/preservation/manual-recovery cases passed. Four persistence hashes
matched after reboot and second cold boot. No future-version progression,
mid-write interruption recovery or automatic/full-system rollback is claimed.

## Confirmed remaining blockers

- Portal SIGSEGV on normal logout at 20:20:48 UTC, reproduced at 20:24:37 after a
  fresh boot without new configuration mutation. Raw cores/stack/journals private;
  exact upstream C++ cause and a natively accepted correction are still pending.
- Hypridle reports an event-loop disconnect/nonzero exit on compositor teardown;
  this is not a Hyprland core and is not hidden by the healthy subsequent session.
- Blank-only installer/global Btrfs refusal cannot directly replace Omarchy.
  No encryption, Btrfs subvolumes or automatic rollback. Source review fix needs
  a separately authorized new build and exact-image testing.
- Frozen maintenance is not a future coherent security-update delivery path.
- Broadcom mitigation/return-thunk warning and required-notice/legal/security gates.
- Every physical MacBook gate and real owner backup/restore remain NOT RUN.
- Human independent security review pending; no exact-head CI checks reported.

## Preservation and controlled close-out

One live and two disk-only QEMU lifetimes were finite and sequential. Both installed
lifetimes ended through normal user poweroff with QEMU exit 0. All owned guests
were absent before the non-repairing offline QCOW2 check (exit 0) and final hashes.
QA lock independently available; 159 runtime evidence entries hash/size matched
after transfer. Candidate bundle excludes raw logs, cores, passwords and VM disks.
Actual paths, final project-lock release/probe, source/PR/issue read-back and exact
resource measurements are in the private handoff, not public server metadata.

No additional ISO build, physical modification, Omarchy removal, Proxmox change,
main merge, public release or worker/scheduler activation occurred.

Full [acceptance report](../development-reports/2026-11-09-private3-exact-image-acceptance.md)
and [backup/hardware/recovery procedure](../omarchy-transition.md).

Next engineering gate: a bounded exact-version portal teardown correction and
native repeated logout/relogin regression. Do not blindly upgrade the snapshot,
suppress the crash, rebuild privileged inputs or ask the owner to erase a disk.
A new ISO build requires its own owner-controlled authorization after remediation.
