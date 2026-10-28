# Internal image build — 2026-10-28

Milestone B completed; runtime milestone C is NOT implied by this record.

- Image: `wilsof-internal-2026.10.28-internal1-x86_64.iso`
- Exact image source: `98bda89c453365b9fc51a0b40ad4174c40b4af8a`
- Bytes: 2545111040
- SHA256: `ab78770ce5c4c5fe8b7b913263ade47e4f2d8830a4ffbb6a38c935c9e9a45e83`
- Internal path: `/home/tommy_ai/wilsof-assets/internal-test-20261028-internal1/`
- Directory contains ISO, `SHA256SUMS`, `manifest.json`; no public release/upload.
- Previous images preserved. No merge to main/arch-install, physical disk/USB write or Proxmox change.

## Source and safety gates

171 tests pass, ShellCheck and diff checks pass; exact-head CI `40661163327` passes. Installer still requires explicit canonical empty whole disk, stable identity, complete zero scan, no signatures/partitions/holders/mounts, matching hidden passwords and exact ERASE confirmation with immediate reprobe. No installer storage guard was relaxed.

#30 migration source e38902b and package manifest alignment2739e4a are included. The already-built Hypridle0.1.8-2.1 artifact from milestone A is checksum pinned, installed in the live build, embedded separately and installed by target provisioning. No Hypridle rebuild.

## Actual build execution and bounded recovery

Only one ISO/version was produced. Clean git archive exported read-only into isolated Archiso91 root; separate minimal private proc/dev/run and read-only sysfs, no host home/credentials/physical block devices. Initial package integrity attempts failed with GPGME inappropriate-ioctl/signature messages; isolated single-package GPG and pacman succeeded. The originating tmux cgroup showed TasksMax976 and 689 rejected processes, with simultaneous tool thread-creation errors. A transient scope bounded to TasksMax1800/MemoryMax8GiB allowed the complete 784-package transaction to pass with unchanged signature policy. No persistent system limit modified.

Customization then correctly failed CheckSpace because the nested image root was not a mountpoint, NOT because storage was full. In a new private mount namespace the same prepared root was bind-mounted to itself and the same work/profile resumed. Native pinned package install, initramfs, squashfs and xorriso completed; final exit0. Resumed work retained; full logs/checkpoints private under `/home/tommy_ai/.local/state/wilsof-qa/session-20261028/`. No signature verification bypass, speculative source patch or concurrent build.

## Immutable artifact audit

Inspected the finished ISO's actual squashfs without mounting. Source marker, #30 code, package hash and running-executable hash pins match. Root is locked, machine-id uninitialized, no static live password/QA account; privileged entrypoints root-owned0755. Build customization script removed. Filename scan found only an empty root/.ssh directory, no contained credentials/files; system service accounts in shadow are expected. This is a scoped content/mode/filename check, not a comprehensive security audit.

Build process/supervisor exited before starting C; shared lock is free between protected operations. Scheduler disabled/paused and automatic worker paused. Next: test these exact bytes as read-only USB media in one disposable UEFI guest, then install to one new dedicated virtual disk and boot disk-only. Physical acceptance remains NOT TESTED.
