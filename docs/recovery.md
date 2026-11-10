# Recovery scope: ext4, systemd-boot and a frozen package baseline

Status, 10 November 2026: manual EFI-loader repair PASSED in a disposable
source-overlay QEMU lab. Future package-version progression remains BLOCKED.
There is no automatic system rollback, and no physical recovery acceptance.
The [owner transition checklist](omarchy-transition.md) remains a replacement NO-GO.

## Executed recovery gate

The retained lab installation used ext4 root and a 1 GiB FAT32 ESP at `/boot`.
A new QCOW2 COW image referenced the independently verified, stopped installation;
the original disk and firmware were never booted writable again.

1. Verify the synthetic target's exact serial, size and root mount. Rename both
   `EFI/BOOT/BOOTX64.EFI` and `EFI/systemd/systemd-bootx64.efi` inside the COW only.
2. Shut down the OS. Cold-boot without installation media. Firmware records
   `Linux Boot Manager ... Not Found` and cannot boot the installed OS. This is
   the expected controlled fault, not a newly discovered product failure.
3. Quit that firmware-only guest and boot the unchanged, checksum-verified live
   image against the same COW disk. Revalidate the synthetic disk identity.
4. `sfdisk --verify` and unmounted `e2fsck -f -n` exit 0. The latter declines a
   nonessential extent-tree optimization; no repair/write flag was used.
5. Mount only the selected root and ESP. Run the installed system's `bootctl
   --no-variables --esp-path=/boot install` through the API-prepared
   `arch-chroot -r` boundary. Restore both loader binaries without a network
   transaction, package downgrade or change to production repository policy.
6. Verify both restored EFI hashes match their original bytes, then sync/unmount
   and shut down live media. Cold-boot disk-only and perform genuine normal
   greeter password/PAM authentication. This gate PASSED.
7. `pacman -Dk` exits 0 with no database errors. The synthetic document, actual
   QA user's Dux settings, image-source marker and repository configuration retain
   their exact pre-fault hashes. These are recovery persistence checks, not proof
   of update migration or mid-transaction recovery.
8. All four owned QEMU lifetimes exit 0. Offline QCOW2 validation passes. Original
   backing disk/firmware and both read-only sentinel images retain their hashes;
   the exclusive QA lock is available.

Private evidence group: `wilsof-stabilization-20261109T2232Z`, including
`recovery-broken-boot.json`, `recovery-native-repair.json`,
`recovery-reboot-final.json` and `recovery-offline-closure.json`.
Do not copy the lab's `/dev/vda*` names into a physical recovery session.

## Owner-controlled physical recovery procedure

This document does not authorize disk access or modification. Before an approved
physical installation, verify independent selected-data backups and bootable
recovery media. If whole-system restoration is required, test an independent
full-system image/reinstall-and-restore method separately; home-directory backups
and a COW chain on one host are not substitutes.

For a future owner-approved EFI-loader recovery:

- Boot the separately verified recovery image and preserve the exact failure.
  Re-identify every attached disk, the selected model/serial/size/transport and
  the root/ESP filesystem UUIDs. Refuse ambiguous identities or active mounts.
- Review the selected unmounted root with a non-writing filesystem check. Stop
  for an unexpected filesystem, encryption, damaged data, changed geometry or
  failed check. The tested method is not a general filesystem-repair procedure.
- Mount only the freshly reviewed root and its ESP. Inspect the installed kernel,
  boot entries and trusted installed bootloader files. Obtain the required
  destructive/recovery authorization before overwriting any physical EFI file.
- Use the installed tool through an API-prepared chroot with the actual reviewed
  mountpoint. The lab-tested command is the `bootctl` invocation above, not a
  generic partition, format, firmware-reset or GRUB recovery recipe.
- Verify restored bytes, sync/unmount cleanly, boot without media and test real
  password login, desktop, applications and all required physical hardware.
  Do not claim success from the repair command's exit code alone.

## Failed or interrupted package transactions

Preserve the package inventory, exact repository policy and pacman journal. Do
not delete a lock automatically, repeat a transaction blindly, ignore dependencies,
create SONAME compatibility links or mix individual library/kernel versions.
Resolve lock ownership and inspect consistency from an approved recovery context.

Planning against coherent official snapshot 2026-11-08 was refused because
`hyprland-as02-private` requires `libaquamarine.so=14-64` and
`libhyprgraphics.so=4-64`, incompatible with its proposed providers. The real
installed database and policy stayed unchanged. No future transaction was run.
A compatible, signature-verified complete closure is required before advancing.

## Additional executed synthetic transaction gate

A separate, network-isolated single-ID mapped-root lab exercised real pacman and
libalpm, not substituted package commands. Two harmless signed test packages
started at `1.0-1`. During a transaction to `2.0-1`, a controlled SIGKILL of the
exact owned process group occurred inside package A's real `post_upgrade`, before
package B was upgraded. Inventory was then A `2.0-1`, B `1.0-1`; `pacman -Dk`
returned 0. Database consistency did not mean the transaction was complete or
that the package set was coherent. The stale lock and interrupted database were
preserved, not silently removed.

Only after confirming the owned process group had exited and copying the fixture
database did the explicit lab recovery remove that fixture's stale lock, reinstall
the entire exact signed test set and verify both versions `2.0-1`, matching payload
bytes, database check 0 and no remaining lock. The host package database,
configuration, public keyring and trust database retained their hashes. Test keys
were removed and namespace mounts disappeared after exit. Nothing in the runtime
update controller automatically removes locks or retries transactions.

Two earlier lab attempts failed before fault injection because the disposable
chroot lacked an executable interpreter and then the native libalpm-configured
`/usr/bin/bash` path. Their failures are retained. Correcting the lab and proving
the actual shell prerequisite preceded the successful third attempt; they are not
production update failures or accepted interruption tests.

This proves a synthetic package-transaction failure/recovery seam, not a real
future Wilsof update, kernel/DKMS migration, boot after package recovery, full-system
restore or atomic rollback. The complete OS transition remains blocked as described
in [the coherent update plan](update-transition.md).

Full OS mid-transaction interruption/recovery, full-system backup restoration and
future update/reboot/application acceptance remain NOT RUN. Existing versioned
Wilsof managed-file backups support explicit per-file restoration only, not
transactional OS rollback.
