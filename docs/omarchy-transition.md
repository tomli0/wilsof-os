# Omarchy to Wilsof: gated backup, hardware and recovery procedure

Status on 9 November 2026: **replacement NO-GO**. This procedure authorizes
neither USB writing nor any change to the MacBook's internal disk. Keep Omarchy
intact. The Private3 image has passed its 18 basic virtual functional gates, but
has a reproducible portal crash on logout and unresolved maintenance, installer,
license-inclusion and physical-acceptance gates. Use the accompanying exact-image
acceptance report, not historical Private2 results.

## 1. Decisions required before replacement

1. Resolve the portal teardown crash and retest repeated session exits/logins.
2. Deliver a separately authorized image containing the reviewed installer target
   identification correction; source changes do not update the frozen ISO.
3. Implement and test a physical replacement policy. The current installer only
   accepts an entirely zero-filled disk and refuses visible Btrfs before importing
   archinstall. It cannot directly replace an existing Omarchy disk. Do not bypass
   those guards, erase Omarchy externally, or infer approval from this document.
4. Resolve future coherent snapshot/security-update delivery and tested recovery.
   The tested updater maintains only the 2026-11-01 snapshot; two successful
   no-ops are not future-version upgrades or automatic rollback.
5. Verify required license/notice inclusion. Broadcom notices are present; Dux's
   package file list contains no standalone license file. Its MIT metadata alone
   does not resolve inclusion or redistribution review.
6. Complete live hardware tests, independent verified backups and an owner-reviewed
   restore/recovery plan. Actual internal-disk replacement needs separate approval.

## 2. Backup selection: owner-only future work

No personal files were read or transferred during this sprint. The owner should
inventory and select, rather than copy the whole Omarchy home indiscriminately:

- Documents, Downloads, pictures/media and other chosen personal directories.
- Development projects, uncommitted and untracked files, local-only Git branches,
  submodules and any locally stored databases. Stop writers before backing up.
- Browser bookmarks and the profiles actually used. Close browsers; record browser
  versions and test restoration in a separate profile before trusting it.
- SSH keys, SSH configuration, Git configuration and signing/recovery material.
  Keep private keys private, preserve permissions and use encrypted backup storage.
- Application settings that the owner needs; record installed applications and
  explicitly selected package lists for clean reinstallation, not a blind replay.
- Network-related user settings and any required NetworkManager profiles. Treat
  saved network secrets as sensitive; do not publish them or copy them into an ISO.
- Password-manager recovery/export material only through its documented encrypted
  workflow, with owner control. Do not place plaintext exports in QA evidence.

Do not automatically restore Omarchy's Hyprland, DMS, systemd-user, shell startup,
autostart, desktop scripts or package/repository configuration into Wilsof. Keep
these in a separate reference backup if needed; compare and migrate selected
settings after the clean Wilsof desktop has passed acceptance.

## 3. Backup verification and selective restoration

- Have at least two independently stored, verified copies before any owner-approved
  destructive transition. A second directory, tar file or snapshot on the same
  internal disk is not an independent backup.
- Keep an owner-private manifest of selected paths, byte sizes and SHA256 values.
  Read the backup back from its actual destination and compare it with that
  manifest. Protect sensitive filenames and key metadata as private data too.
- Preserve metadata appropriate to each selected item. Test Unicode names,
  symbolic links and private-key modes, not just total archive size.
- Restore into an empty staging directory as an ordinary user first. Inspect
  archive paths and symbolic-link targets before selectively copying anything
  into the new home. Never extract an unreviewed archive as root over `/`.
- Open representative documents, test a disposable browser profile, verify project
  integrity and check that restored private keys are owned by the intended user
  with restrictive permissions. Keep old backups until this validation succeeds.

The sprint's executed synthetic tar round-trip preserved five invented files,
a Unicode filename, a symbolic link without dereferencing, a user xattr and SSH
0700/0600 modes, while excluding an invented Omarchy Hyprland configuration. This
is a method check on one filesystem, not a verified backup of the owner's data,
an ACL-matrix test or a full-system restore.

## 4. Live USB first: checklist, all physical rows NOT RUN

Only after the candidate's release gates permit it should the owner receive a
private bundle with ISO filename, exact byte size, SHA256, frozen source and the
acceptance report. Verify the transferred file's SHA256 against that independent
manifest. The owner identifies an expendable USB by actual model, serial and
capacity before using an image writer; no agent writes a physical block device.
Follow the [existing owner USB runbook](internal-test-runbook.md#usb-preparation-performed-by-the-owner).

Boot **Try Wilsof OS** through the Mac's UEFI menu, keeping the USB attached.
Do not run installation or mount personal volumes read-write. Do not silently
change firmware security settings. If boot fails, use the diagnostic entry or
record the exact error without photographing generated live credentials.

| Physical acceptance | Required observation | Status |
| --- | --- | --- |
| UEFI/live | Correct candidate boots, usable live desktop | NOT RUN |
| Display/graphics | i915, internal 2560x1600 panel, readable scale 2.0, no corruption | NOT RUN |
| Keyboard | Normal text, modifiers, function/brightness keys and shortcuts | NOT RUN |
| Trackpad | Pointer, click, scroll and intended gestures | NOT RUN |
| Wi-Fi binding | PCI 14e4:43a0 actually bound to wl; wireless interface in NetworkManager | NOT RUN |
| Wi-Fi connectivity | Scan, owner-private WPA connection, DNS/Internet, reconnect and reboot | NOT RUN |
| Bluetooth | btusb, adapter discovery, actual pairing and reconnect | NOT RUN |
| Audio | Speakers/headphones and microphone with PipeWire | NOT RUN |
| Suspend/resume | Repeated manual and lid-triggered cycles, on AC and battery | NOT RUN |
| Power | Brightness, battery reporting, charging and thermal behavior | NOT RUN |
| Lifecycle | Normal reboot/shutdown; USB remains usable for recovery | NOT RUN |

QEMU had virtual Ethernet, dummy-only audio and no Bluetooth adapter. Its service
or UI results do not pass these physical rows. The wl module's presence, ABI and
virtual load likewise do not prove BCM4360 initialization or WPA connectivity.
The observed Broadcom security-mitigation warning must be reviewed, not suppressed
through disabled mitigations or signature checks.

## 5. Recovery before installation is approved

- Retain a known bootable Omarchy recovery/install USB and the separately verified
  backup. Keep the Wilsof candidate and independent checksum on another device.
- Verify recovery media actually boots before relying on it. Record how to select
  the firmware boot device and regain a local console, without changing disks.
- The current Wilsof layout is unencrypted ext4 with a 1 GiB FAT32 ESP at `/boot`,
  no Btrfs subvolumes, no filesystem snapshots and no automatic system rollback.
  Decide whether this meets the owner's security/recovery needs before approval.
- For a failed update, stop repeated attempts. Preserve `/var/log/pacman.log`,
  package identities and the exact repository snapshot. Inspect the owner of an
  existing package lock; never delete it automatically or perform a partial upgrade.
- If the desktop breaks, preserve the failure and use the recovery console/media.
  Mount/repair targets only after a fresh explicit disk-identity review in the
  separately approved recovery session. This document supplies no generic format,
  partition, chroot or bootloader-repair command for an unknown physical disk.
- A Wilsof managed-file backup under `~/.local/state/wilsof-os/backups/` permits
  manual restoration of the selected file. Test that file and reapply the reviewed
  local configuration when appropriate. This is not transactional OS rollback.
- Returning to Omarchy after an approved full-disk overwrite would require a
  separately tested reinstall/data-restoration or full-image restore procedure;
  it is not guaranteed by a home-directory backup or this sprint.

## 6. Post-install acceptance: separate owner approval first

Recheck ordinary password login, rejected wrong password, native lock/unlock,
automatic idle lock, menu/shortcuts, all selected applications, hardware, updates,
configuration persistence and recovery. Reboot and cold-boot again. Restore only
selected data after the clean system passes. Keep the old backups and recovery
media; approve daily-driver use only with explicit evidence for every required
physical and maintenance gate.
