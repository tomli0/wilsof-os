# RC4 recovery boundaries

Status: **bounded virtual recovery PASS; physical recovery not established**.
RC4 passed 66/66 virtual checks on November 13, 2026. Its exact image/source
identity is recorded in [Getting started](getting-started.md). The owner is
currently evaluating physical Live behavior; no individual physical recovery
result has been reported. Keep the accepted image unchanged.

Wilsof recovery is not migration of another operating system. This document does
not authorize physical disk access, firmware changes, installation or repair.

## Layout and trust

Normal RC4 installation uses a **LUKS2-encrypted ext4 root**, a separate
**unencrypted FAT32 EFI System Partition** mounted at `/boot`, and systemd-boot.
A disk-unlock passphrase is separate from the account password. Root encryption
does not authenticate the ESP or provide Secure Boot trust. No TPM unlock,
automatic recovery key, A/B system or atomic OS rollback is claimed.

The image and private runtime inputs remain **TEST ONLY**. A verified checksum,
working boot or successful repair does not approve production signing/trust.

## What the exact RC4 image actually passed

The retained acceptance evidence covers these distinct synthetic scenarios:

- Encrypted-root recovery with read-only access and preserved data.
- Deliberate loss of both EFI loader files on a disposable installed system;
  real disk-only firmware boot failure was observed before repair.
- Repair of the loader files from the exact Live image using the installed
  system's bootctl through the prepared chroot boundary, followed by a fresh
  encrypted disk-only boot, normal PAM login and user-data checks.
- A genuine kernel-hook update interruption with an incomplete transaction.
  The shipped recovery helper refused missing initramfs with exit 78 and did not
  promote repository policy or report completion.
- A separately reviewed, explicit full-set repair, followed by successful
  completed-set recovery and a new encrypted boot/login with persistence checks.

These are bounded virtual results, not arbitrary power-loss coverage, a guarantee
for every damaged filesystem, physical-device acceptance or automatic rollback.
Historical RC2/source-overlay/synthetic-package results remain in Git history;
they must not be substituted for this image's evidence.

## Read-only diagnosis first

For an explicitly authorized recovery of a dedicated test installation:

1. Preserve the exact failure and boot only verified, trusted recovery media.
2. Identify the selected disk, LUKS root and ESP unambiguously. Record private
   device identifiers locally; never copy a lab's `/dev/vda*` names to hardware.
3. Use the normal local passphrase surface. Do not put passphrases in command
   arguments, logs, reports or chat. A login password cannot recover a lost
   disk-unlock passphrase.
4. Establish read-only access before inspecting data. For ext4, avoid journal
   replay during a non-writing examination. An encrypted mapping and a mounted
   filesystem have separate access modes; read-only must apply to both.
5. Preserve relevant boot/package logs, policy, inventory and user data before
   selecting any repair. Stop for an unexpected layout, ambiguous identity,
   failing non-writing checks or missing trusted repair inputs.

Do not weaken encryption, signatures, dependency checks or firmware policy to
force a successful result.

## EFI-loader repair is not system restoration

The accepted lab repaired only the two known loader files using the installed
`bootctl --no-variables --esp-path=/boot install` through the API-prepared chroot.
A future physical repair requires separate exact-target/write approval, reviewed
mounts, safe access to the installed root and trusted bootloader files.

Compare repaired bytes with the expected references, sync/unmount cleanly, then
verify a real disk-only boot, unlock and ordinary login. Exit 0 from a repair
command alone is not recovery acceptance. Loader repair does not restore lost
user files, undo an upgrade or reconstruct an overwritten operating system.

## Interrupted package transactions

Preserve the proposal, detached signature, package cache, pacman logs and
`/var/lib/wilsof-release-update/transaction.json`. Do not retry blindly, remove a
lock automatically, disable dependencies or mix individual library/kernel sets.
Verify whether the recorded transaction and package tools still own the lock.

`wilsof-release-update --recover DIRECTORY` is **completed-set verification**, not
package repair. It requires the same recorded signed plan, the intended complete
package inventory, valid database and usable kernel/initramfs artifacts. Only
then may it promote the recorded policy/completion state. The actual native
transaction is repaired separately, explicitly and with the reviewed full set.

A complete inventory or successful `pacman -Dk` alone does not prove bootability.
See [the update/recovery contract](update-transition.md) and
[signing requirements](package-signing.md). No automatic retry or hidden initramfs
rebuild is part of normal recovery.

## Data and physical limits

Managed-file backups support explicit per-file restoration, not whole-system
rollback. Independent data backups and trusted recovery media remain necessary
before destructive work on any installation. Any real restore method must be
rehearsed on a separately approved disposable target; this review performs none.
Physical Live checks are tracked in [the checklist](physical-test-checklist.md).
