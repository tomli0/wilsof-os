# RC4 recovery boundaries

Status: **bounded virtual recovery PASS; physical Live boot FAIL reported**.
RC4 passed 66/66 virtual checks on November 13, 2026. Its exact image/source
identity is recorded in [Getting started](getting-started.md). On November 16,
2026, the owner reported a black screen after Live startup on MacBookPro11,1;
TTY2 remained accessible. The graphical cause is not yet established. Keep the
accepted image and its historical virtual evidence unchanged.

Wilsof recovery is not migration of another operating system. This document does
not authorize physical disk access, firmware changes, installation or repair.

## Live console credentials and black-screen diagnosis

The accepted RC4 ISO does not contain a static Live password. The boot-only
`live-console-setup` creates user `live`, generates `secrets.token_hex(6)` (12
hexadecimal characters), sets it through `chpasswd` on stdin, then writes this
line to `/etc/issue` for the TTY2 login banner:

```text
Username: live    This boot only password: <generated for this boot>
```

Use that displayed password, not an empty password or the word `live`. Password
input is hidden. It changes on a fresh boot; do not send it or an uncropped banner
photo in a report. Root remains locked, remote login is not enabled, and the
installed-user authentication policy is unchanged. If the password line is not
visible, report that fact rather than guessing or changing authentication.

TTY2 explicitly Requires/After `wilsof-live-console.service`; graphical setup
also requires that service but the console does not require graphical setup.
The Live desktop has an initial `live` session on greetd VT1; after that session
ends, greetd falls back to tuigreet. Both call `wilsof-session` →
`start-hyprland`. The normal wrapper journals output as `wilsof-session`; the
boot-menu diagnostics entry instead leaves it on the originating console.
A running greetd service is not proof of a running or rendered compositor.

Next physical test, without rewriting the USB or accessing internal storage:

1. Boot the existing verified RC4 USB using **Wilsof OS diagnostics - boot logs,
   no splash**. Do not change graphics parameters for this baseline.
2. Switch to Ctrl+Alt+F2 and log in as `live` using the password displayed there.
3. Run `sudo /usr/local/bin/wilsof-live-recover` and retain sanitized output or a
   cropped photo, excluding the credential banner. Capture the original failure
   before using `--restart`.
4. Also retain any readable Hyprland crash report from `~/.cache/hyprland/` and
   the diagnostics VT1 error. An absent report is not proof that Hyprland ran.

The helper shipped in **RC4** queries only Live setup/greetd units; it can miss
compositor, user-shell and kernel graphics failures. The subsequent source fix
adds separate bounded current-boot queries for `wilsof-session`, Dux and kernel
graphics, retaining query failures/timeouts. That fix is **not in RC4** and is not
a verified black-screen repair. A derivative must refresh the actual privileged
Live executable, not just an embedded source copy, and pass its own immutable
and runtime gates before delivery. Never overlay or rewrite the accepted ISO.

Read-only inspection of RC4 found the `i915` module, Mesa's `crocus_dri.so`, the
KMS initramfs hook and no i915 blacklist/renderer override in the inspected boot
configuration. Presence is not evidence of device binding, successful EGL
initialization or physical rendering. Without the failing hardware's boot and
session logs, neither an Intel driver defect nor a compositor/configuration
failure is confirmed. Do not add `nomodeset`, force a different Mesa driver or
apply unrelated GPU workarounds merely because the screen is black.

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
