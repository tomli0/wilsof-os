# Internal installer runtime

This is an **internal interactive adapter, not a release or hardware-support claim**.
`bin/wilsof-install --validate PLAN.json` only reads the plan and schema. It does
not import archinstall, probe disks, or authorize execution. With no arguments,
installation requires a root terminal on booted Archiso, x86-64 and 64-bit UEFI.
Known-enabled Secure Boot is refused; no keys are enrolled or firmware settings
changed. Firmware without a SecureBoot variable is accepted, not certified.

## API authority and pin

The implementation was checked against the installed **archinstall 4.5** source
and its `archinstall-4.5.dist-info/METADATA` (Python >=3.14), not an older online
example. Runtime metadata must equal `4.5`, not merely a compatible major version.
The relevant upstream modules and calls are:

- `lib.disk.device_handler.device_handler.get_device(Path)`; reuse its initial
  inventory rather than rescanning other disks after review.
- `lib.disk.default_layouts.suggest_single_disk_layout(device,
  filesystem_type=FilesystemType.EXT4, separate_home=False)`, an async function.
  With UEFI this proposes GPT, a 1 GiB FAT32 ESP starting at 1 MiB mounted at
  `/boot`, and an ext4 `/` using the remaining GPT-aligned space. No swap/home
  partition, LVM, subvolumes, encryption, or custom partitioner is introduced.
- `DiskLayoutConfiguration(config_type=DiskLayoutType.Default,
  device_modifications=[modification])`, then
  `FilesystemHandler(config).perform_filesystem_operations()`.
- `Installer(target, config, base_packages=packages, kernels=['linux'])` as a
  context manager; `mount_ordered_layout()`, `minimal_installation(...)`,
  `set_locale(LocaleConfiguration('us', 'en_US.UTF-8', 'UTF-8'))`,
  `create_users(User(name, Password(plaintext=secret), True))`,
  `set_user_password(user)`, `mkinitcpio(['-P'])`,
  `add_bootloader(Bootloader.Systemd)`, `arch_chroot(...)`, `enable_service(...)`,
  `genfstab()`, and `post_install_check()`.

The explicit password call is necessary because 4.5's `create_users()` discards
its password setter's failure result. Password/hash input reaches `chpasswd
--encrypted` on stdin via archinstall's `lib.command.run`, not argv or config.
No archinstall CLI/config handler is imported; no credentials/config are saved.
Python cannot guarantee secret-memory zeroization. Backend logs remain local.

Systemd-boot uses upstream configuration plus `bootctl --no-variables
--esp-path=/boot install`; success requires `/boot/EFI/BOOT/BOOTX64.EFI`.
The `bootloader_removable` flag is deliberately not used: upstream's flag is for
GRUB/Limine, not systemd-boot. Boot, console login, DNS and session behavior still
need disposable-VM verification.

## Safety boundary

The user enters a canonical whole-disk `/dev/NAME` path with no default, a username,
and matching hidden passwords. Review displays packages, unencrypted layout, the
entire non-secret canonical plan, and a whole-disk data-loss warning. Only the exact
text `ERASE /dev/NAME` permits continuation. There is no unattended execution or
execute-saved-plan option, automatic retry, SSH setup or automatic reboot.

Schema: `schemas/installation-plan.schema.json`. The digest is `sha256-` plus the
hex SHA-256 of UTF-8 JSON with sorted keys, compact separators, ASCII escaping and
no NaN, excluding only `review_digest`. `plan_id` binds the reviewed effective
package-list digest. Encryption-enabled plans, optional package choices and codec
selection are rejected rather than silently ignored.

The initial probe and final pre-filesystem guard both require:

- A writable block disk >=16 GiB, no children, partition table, filesystem,
  wipefs signatures, mounts (including live media), or block-device holders.
- A WWN or serial; its private hash also binds model and kernel major/minor.
  Identity, size and path must still equal the reviewed target.
- **Every byte must be zero**, verified with an O_RDONLY/O_NOFOLLOW full scan.
  Merely deleting partitions does not make a disk eligible. Short reads abort.
  Large disks can take considerable time; cancellation before formatting is safe.
- An empty, non-symlink, unmounted `/mnt/wilsof` target directory.

The last probe is directly before `perform_filesystem_operations()`, with no
further prompt. This is not an atomic protection against privileged concurrent
writers, hotplug or adversarial device replacement; do not change storage during
installation. Once filesystem operations begin, there is no rollback guarantee.
Failures stop, leave mounts for inspection, and never reboot automatically.

**Upstream side effect discovered:** importing `device_handler` instantiates a
handler that scans all disks and can mount unmounted Btrfs partitions. This
adapter refuses any visible Btrfs filesystem before importing archinstall and
refuses third-party archinstall plugin entry points. Keep unrelated disks absent
from the disposable VM. No physical-disk test was performed.

## Parent-owned ISO handoff

The parent build must supply, root-owned and not writable by live users:

1. `/usr/share/wilsof/source`: sanitized payload including `bin/wilsof-install`,
   `installer/__init__.py`, `installer/wilsof_installer.py` and `schemas/`.
   A copied `/usr/local/bin/wilsof-install` resolves this fixed payload; a
   root-owned symlink into the payload also works. Do not copy tests,
   `.git`, build roots, host credentials/`.ssh`, or the old VM-specific installer.
2. `/usr/share/wilsof/desktop-packages.txt`: one official-repository package name
   per line; blank lines and whole-line `#` comments are supported. No options,
   repository-qualified names, URLs or shell syntax. It must include all core
   desktop, greeter/frontend and DMS dependencies. The adapter adds base, linux,
   linux-firmware, mkinitcpio, networkmanager, sudo and greetd. Online official
   repositories/mirrors must work; offline package availability is not promised.
3. Executable `/usr/local/lib/wilsof/provision-target TARGET USER [--live]`.
   The adapter calls exactly `provision-target /mnt/wilsof USER` after the account
   exists and before enabling services/final success. **No `--live` for installed
   targets.** The script must operate only inside TARGET, copy the sanitized
   payload, install root-owned entrypoints and greetd config, and configure DMS
   and the user's files as USER offline without needing a user bus. Exit nonzero
   on any incomplete step; never accept passwords or install credentials.
4. Create empty `/mnt/wilsof`; provide Python >=3.14, python-jsonschema,
   archinstall exactly 4.5 and its dependencies, util-linux and installation
   tools. Present a fresh zero-filled disposable disk with a stable serial/WWN.

`systemd-detect-virt --vm` reporting qemu/kvm adds `qemu-guest-agent`; its service
is enabled only when `/dev/virtio-ports/org.qemu.guest_agent.0` exists. No network
administration or SSH is used. NetworkManager and greetd are enabled, not started
in the target chroot. Host network credentials are not copied.

## Verification and limits

`python -m pytest tests/test_installer_runtime.py -q` exercises fixture inventory,
full blank checks on memory streams, review/confirmation/password rejection,
identity/size/mount changes, schema/digest restrictions, package names, lazy
imports, safe read-only CLI, firmware and mocked archinstall success/failure paths.
No test calls a real partitioner or filesystem operation. Real Arch dependency
imports and installation need the parent's isolated-chroot helper/disposable VM;
they are not validated by mocked tests. This work changes no build profile,
desktop provisioning code, updates code, scheduler or public release state.
