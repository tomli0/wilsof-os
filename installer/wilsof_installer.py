"""Internal, interactive-only Wilsof adapter. Importing this module is read-only."""
import argparse
import copy
from contextlib import contextmanager, ExitStack
import getpass
import platform
import sys
import warnings
import hashlib
import json
import os
import stat
import subprocess
import re
from pathlib import Path
import runpy

from jsonschema import Draft202012Validator

from installer.accounts import validate_username

ROOT = Path(__file__).resolve().parents[1]
snapshot = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
wireless = runpy.run_path(str(ROOT / 'runtime/broadcom-wl.py'))
ARCHINSTALL_VERSION = '4.5'
LSBLK = ['lsblk', '--json', '--bytes', '--paths', '--output',
         'PATH,KNAME,TYPE,SIZE,MAJ:MIN,RO,WWN,SERIAL,MODEL,VENDOR,TRAN,RM,PTTYPE,FSTYPE,MOUNTPOINTS']
# JSON trees are not implicit when NAME is absent from the requested columns.
REPLACEMENT_LSBLK = [LSBLK[0], '--tree', *LSBLK[1:-1], LSBLK[-1] + ',PARTTYPE,UUID']


def read_json(argv):
    return json.loads(subprocess.run(argv, check=True, capture_output=True,
                                     text=True, timeout=60).stdout)


def verify_blank(stream, size):
    remaining = size
    while remaining:
        block = stream.read(min(8 * 1024**2, remaining))
        if not block or block.count(0) != len(block):
            raise Refusal('Target is not entirely zero-filled (or read was incomplete)')
        remaining -= len(block)
    if stream.read(1):
        raise Refusal('Target size changed during blank check')


def check_block_and_blank(path, size):
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        if not stat.S_ISBLK(os.fstat(stream.fileno()).st_mode):
            raise Refusal('Target is not a block device')
        verify_blank(stream, size)


def has_holders(path):
    holders = Path('/sys/class/block') / Path(path).name / 'holders'
    return bool(list(holders.iterdir()))


def probe_disk(path):
    before = assess_inventory(path, read_json(LSBLK))
    if has_holders(path):
        raise Refusal('Target is in use by a block-device holder')
    signatures = read_json(['wipefs', '--no-act', '--json', path])
    if signatures['signatures']:
        raise Refusal('Target contains existing signatures')
    check_block_and_blank(path, before['size_bytes'])
    after = assess_inventory(path, read_json(LSBLK))
    if before != after or has_holders(path):
        raise Refusal('Target changed while probing')
    return after


class Refusal(Exception):
    """A boundary check failed; do not continue installation."""


def check_live_capacity(directory=Path('/var/tmp'), memory=Path('/proc/meminfo')):
    """Fail before package preflight/disk input when the live RAM budget is unsafe.

    The frozen closure currently needs about 1283 MiB compressed. Leave at
    least 509 MiB for the fresh DB, signatures and overlay growth. A larger
    tmpfs limit alone does not establish that there is actual RAM behind it.
    """
    try:
        values = {}
        for line in memory.read_text().splitlines():
            key, _, value = line.partition(':')
            if key not in ('MemTotal', 'MemAvailable'):
                continue
            fields = value.split()
            if key in values or len(fields) != 2 or fields[1] != 'kB' or not fields[0].isdecimal():
                raise ValueError('Invalid memory accounting')
            values[key] = int(fields[0]) * 1024
        total, available = values['MemTotal'], values['MemAvailable']
        if not 0 < available <= total:
            raise ValueError('Invalid memory accounting')
        space = os.statvfs(directory)
        free = space.f_bavail * space.f_frsize
        if free < 1792 * 1024**2:
            raise Refusal('Insufficient temporary writable capacity: need 1792 MiB free in /var/tmp; '
                          'use the current live image, without disabling package preflight')
        # Firmware/kernel reservations mean nominal 4 GiB machines expose less.
        if total < 3584 * 1024**2 or available < 2304 * 1024**2:
            raise Refusal('Insufficient RAM for installation: use at least 4 GiB installed RAM '
                          'and leave 2304 MiB available; close applications before retrying')
    except (OSError, KeyError, ValueError) as error:
        raise Refusal('Cannot verify live RAM/writable capacity; no package or disk operation started') from error


def review_digest(plan):
    """SHA-256 of sorted, compact ASCII JSON, excluding review_digest itself."""
    payload = {key: value for key, value in plan.items() if key != 'review_digest'}
    return 'sha256-' + hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
        allow_nan=False,
    ).encode('utf-8')).hexdigest()


def validate_plan(plan):
    schema = json.loads((ROOT / 'schemas/installation-plan.schema.json').read_text())
    if not Draft202012Validator(schema).is_valid(plan):
        raise Refusal('Installation plan fails schema validation')
    if plan['review_digest'] != review_digest(plan):
        raise Refusal('Canonical review digest mismatch')
    if plan['executor']['adapter_version'] != ARCHINSTALL_VERSION:
        raise Refusal('Only archinstall 4.5 is supported')
    mode = plan.get('installation_mode', 'blank')
    if ((mode == 'blank' and (not plan['target']['expected_empty'] or 'existing' in plan['target'])) or
            (mode == 'replace-existing' and (plan['target']['expected_empty'] or not plan['target'].get('existing')))):
        raise Refusal('Installation mode and reviewed target do not match')
    if plan['bootloader'] != 'systemd-boot':
        raise Refusal('Only systemd-boot is supported')
    try:
        validate_username(plan['account']['username'])
    except ValueError as error:
        raise Refusal(str(error)) from error
    if plan['optional_packages'] or plan['codecs'] not in ({}, {'selected': False}):
        raise Refusal('Optional packages and codec selection are not supported')
    return plan


def read_manifest(path):
    packages = [line.strip() for line in Path(path).read_text().splitlines()
                if line.strip() and not line.lstrip().startswith('#')]
    if not packages or any(not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9@._+\-]*', p)
                           for p in packages):
        raise Refusal('Manifest must contain one plain package name per line')
    return list(dict.fromkeys(packages))


def check_arch_import_environment(inventory, plugins):
    # DeviceHandler.__init__ scans ALL disks and mounts unmounted Btrfs partitions.
    # Refuse before importing it rather than modifying upstream or touching other disks.
    def check(items):
        for item in items:
            if item.get('fstype') == 'btrfs':
                raise Refusal('Btrfs devices are present; archinstall global probing is unsafe here')
            check(item.get('children', []))
    check(inventory['blockdevices'])
    if plugins:
        raise Refusal('Third-party archinstall plugins are not supported')


def guest_policy(channel_present=None):
    result = subprocess.run(['systemd-detect-virt', '--vm'], capture_output=True,
                            text=True, timeout=10, check=False)
    is_qemu = result.returncode == 0 and result.stdout.strip() in {'qemu', 'kvm'}
    if channel_present is None:
        channel_present = Path('/dev/virtio-ports/org.qemu.guest_agent.0').exists()
    return (['qemu-guest-agent'] if is_qemu else [], bool(is_qemu and channel_present))


def verify_archinstall_metadata():
    # Distribution metadata does not import DeviceHandler or touch any disk.
    from importlib.metadata import PackageNotFoundError, version
    try:
        if version('archinstall') != ARCHINSTALL_VERSION:
            raise Refusal('Installed archinstall must be exactly 4.5 before any erasure')
    except PackageNotFoundError as error:
        raise Refusal('Required archinstall backend is missing; no erasure permitted') from error


def load_archinstall():
    # Never import archinstall.main, args, scripts, or its CLI entrypoint.
    from importlib.metadata import entry_points, version
    from types import SimpleNamespace
    verify_archinstall_metadata()
    check_arch_import_environment(read_json(LSBLK),
                                  list(entry_points().select(group='archinstall.plugin')))
    from archinstall.lib.disk.device_handler import device_handler
    from archinstall.lib.disk.default_layouts import suggest_single_disk_layout
    from archinstall.lib.disk.filesystem import FilesystemHandler
    from archinstall.lib.installer import Installer
    from archinstall.lib.models.bootloader import Bootloader
    from archinstall.lib.models.device import (
        DiskEncryption, DiskLayoutConfiguration, DiskLayoutType, EncryptionType, FilesystemType, Unit)
    from archinstall.lib.models.locale import LocaleConfiguration
    from archinstall.lib.models.users import Password, User
    return SimpleNamespace(**{key: value for key, value in locals().items()
                              if key not in {'version', 'SimpleNamespace'}})


def check_target_mount(path):
    try:
        path = Path(path)
        canonical = path.resolve(strict=True)
        if (not path.is_absolute() or canonical != path
                or any(part.is_symlink() for part in (path, *path.parents))
                or not canonical.is_dir() or any(canonical.iterdir())):
            raise Refusal('Target mount directory must be empty and canonical, without symlinks')
        # Canonicalize table entries too: lexical aliases must not hide a mount.
        mounts = read_json(['findmnt', '--json', '--list', '--output', 'TARGET'])
        for item in mounts['filesystems']:
            mounted = Path(item['target']).resolve()
            if mounted == canonical or canonical in mounted.parents:
                raise Refusal('Target mount directory already contains a mount')
    except (OSError, RuntimeError) as error:
        raise Refusal('Target mount directory cannot be safely resolved') from error


class ArchinstallExecutor:
    def __init__(self, manifest=Path('/usr/share/wilsof/desktop-packages.txt'),
                 provision=Path('/usr/local/lib/wilsof/provision-target'),
                 target=Path('/mnt/wilsof'), guest=((), False), *, defer_api=False, encrypt=False):
        self.encrypt = encrypt
        self.guest_enabled = guest[1]
        self.packages = list(dict.fromkeys([
            'base', 'linux', 'linux-firmware', 'mkinitcpio', 'networkmanager', 'sudo', 'greetd',
            # Include upstream bootloader/microcode/accessibility additions in review.
            'efibootmgr', 'dosfstools', 'e2fsprogs', 'intel-ucode', 'amd-ucode',
            'brltty', 'espeakup', 'alsa-utils',
            *(['cryptsetup'] if encrypt else []), *read_manifest(manifest), *guest[0],
        ]))
        private = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'runtime/private-hyprland.py'))
        self.private_record = private['embedded'](Path('/usr/share/wilsof'))
        self.packages = private['selection'](self.packages, self.private_record)
        self.repository_inputs = snapshot['preflight'](Path('/'), self.packages, self.private_record)
        self.manifest_digest = self.package_review_digest()
        self.provision = Path(provision)
        self.target = Path(target)
        if not self.provision.is_file() or not os.access(self.provision, os.X_OK):
            raise Refusal('Required provision-target executable is missing')
        check_target_mount(self.target)
        if defer_api:
            verify_archinstall_metadata()
        self.api = None if defer_api else load_archinstall()

    def package_review_digest(self):
        return 'sha256-' + hashlib.sha256(
            json.dumps({'packages': self.packages, 'encryption': self.encrypt,
                        'repository_inputs': self.repository_inputs,
                        'private_hyprland': None if self.private_record is None else {
                            k: self.private_record[k] for k in
                            ('name', 'version', 'architecture', 'sha256', 'binary_sha256')}},
                       separators=(',', ':'), sort_keys=True).encode()).hexdigest()

    def execute(self, plan, password, guard, *, encryption_password=None):
        import asyncio
        if plan['encryption']['enabled'] != self.encrypt:
            raise Refusal('Encryption choice differs from reviewed executor')
        if self.encrypt and (not isinstance(encryption_password, str) or
                             len(encryption_password) < 12 or
                             not encryption_password.strip() or encryption_password == password or
                             any(not 32 <= ord(c) <= 126 for c in encryption_password)):
            raise Refusal('Encryption requires a separate nonblank printable ASCII passphrase of at least 12 characters')
        if not self.encrypt and encryption_password is not None:
            raise Refusal('Unexpected encryption passphrase for an unencrypted plan')
        private = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'runtime/private-hyprland.py'))
        if private['embedded'](Path('/usr/share/wilsof')) != self.private_record:
            raise Refusal('Private Hyprland policy changed after package review')
        if snapshot['read'](Path('/')) != self.repository_inputs['snapshot']:
            raise Refusal('Repository snapshot changed after review')
        validate_plan(plan)
        if self.package_review_digest() != self.manifest_digest or plan.get('plan_id') != self.manifest_digest:
            raise Refusal('Reviewed package manifest differs from executor')
        check_target_mount(self.target)
        final_guard = guard
        if plan.get('installation_mode') == 'replace-existing':
            if self.api is not None:
                raise Refusal('Replacement requires a deferred, read-only backend')
            guard()
            # All package/source/target preconditions above precede the first wipe.
            erased = erase_replacement(plan)
            self.api = load_archinstall()
            def erased_guard():
                if probe_replacement(plan['target']['path']) != erased:
                    raise Refusal('Erased target changed before filesystem operations')
            final_guard = erased_guard
        api = self.api
        if api is None:
            raise Refusal('Blank installation requires the validated backend')
        # Reuse the import-time read-only inventory; do not rescan/mount unrelated disks.
        device = api.device_handler.get_device(Path(plan['target']['path']))
        if device is None:
            raise Refusal('Archinstall did not find the selected disk')
        info = device.device_info
        if (device.partition_infos or info.read_only or
                str(info.path) != plan['target']['path'] or
                info.total_size.convert(api.Unit.B).value != plan['target']['size_bytes']):
            raise Refusal('Archinstall cached inventory differs from the reviewed empty disk')
        modification = asyncio.run(api.suggest_single_disk_layout(
            device, filesystem_type=api.FilesystemType.EXT4, separate_home=False))
        parts = modification.partitions
        if len(parts) != 2 or [(p.mountpoint, p.fs_type) for p in parts] != [
            (Path('/boot'), api.FilesystemType.FAT32), (Path('/'), api.FilesystemType.EXT4),
        ]:
            raise Refusal('Archinstall proposed an unsupported layout')
        config = api.DiskLayoutConfiguration(
            config_type=api.DiskLayoutType.Default, device_modifications=[modification])
        if self.encrypt:
            config.disk_encryption = api.DiskEncryption(
                encryption_type=api.EncryptionType.LUKS,
                encryption_password=api.Password(plaintext=encryption_password),
                partitions=[parts[1]], hsm_device=None)
        handler = api.FilesystemHandler(config)
        final_guard()  # Reprobe reviewed or erased state after all interactive input.
        # The full-disk scan may be lengthy: revalidate the destination last too.
        check_target_mount(self.target)
        if snapshot['read'](Path('/')) != self.repository_inputs['snapshot']:
            raise Refusal('Repository snapshot changed before disk operations')
        handler.perform_filesystem_operations()
        if self.encrypt:
            # Never continue installing if the backend silently skipped encryption.
            subprocess.run(['cryptsetup', 'isLuks', '--type', 'luks2', str(parts[1].safe_dev_path)],
                           check=True, capture_output=True, timeout=30)
        with api.Installer(self.target, config, base_packages=list(self.packages),
                           kernels=['linux']) as installation:
            installation.mount_ordered_layout()
            locale = api.LocaleConfiguration('us', 'en_US.UTF-8', 'UTF-8')
            # 4.5 minimal_installation discards set_locale's result, and set_locale
            # is not idempotent. Perform one checked locale call after base install.
            installation.minimal_installation(mkinitcpio=False, hostname='wilsof', locale_config=None)
            # pacstrap consumes the live config; persist it explicitly instead of
            # inheriting the package's moving-mirror defaults in the fresh target.
            snapshot['stage'](self.target)
            snapshot['verify_installed'](self.target, self.repository_inputs)
            # Pacman's DKMS hook failure need not fail the package transaction.
            # Require the installed module and policy before the final initramfs.
            wireless['stage'](self.target)
            wireless['verify'](self.target)
            installation.set_vconsole(locale)
            if not installation.set_locale(locale):
                raise Refusal('Target locale generation failed')
            user = api.User(plan['account']['username'], api.Password(plaintext=password), True)
            installation.create_users(user)
            # create_users ignores set_user_password's False result in 4.5; check explicitly.
            if not installation.set_user_password(user):
                raise Refusal('Target account password could not be set')
            if not installation.mkinitcpio(['-P']):
                raise Refusal('Target initramfs generation failed')
            installation.add_bootloader(api.Bootloader.Systemd)
            # bootctl creates EFI/BOOT/BOOTX64.EFI; do not misuse the GRUB-only removable flag.
            installation.arch_chroot('bootctl --no-variables --esp-path=/boot install')
            subprocess.run([str(self.provision), str(self.target), plan['account']['username']],
                           check=True, timeout=1800)
            installation.enable_service(['NetworkManager', 'greetd'])
            if self.guest_enabled:
                installation.enable_service('qemu-guest-agent')
            installation.genfstab()
            if installation.post_install_check():
                raise Refusal('Archinstall reports incomplete installation steps')
            if not (self.target / 'boot/EFI/BOOT/BOOTX64.EFI').is_file():
                raise Refusal('UEFI fallback boot file is missing')


def interactive(executor, *, mode='blank', probe=None, ask=input, secret=getpass.getpass, output=print):
    if mode not in ('blank', 'replace-existing'):
        raise Refusal('Unknown installation mode')
    encrypt = getattr(executor, 'encrypt', False)
    probe = probe or (probe_disk if mode == 'blank' else probe_replacement)
    path = ask('Target whole-disk path (no default; e.g. /dev/vda): ')
    output('Checking that every byte of the target is zero; this can take time.' if mode == 'blank'
           else 'Replacement mode: inspecting existing filesystems without modifying them.')
    target = probe(path)
    username = ask('New administrator username: ')
    plan = {
        'schema': 'wilsof.install-plan/v1', 'plan_id': executor.manifest_digest,
        'target': target,
        'layout': {'mode': 'whole-disk', 'table': 'gpt', 'firmware': 'uefi',
                   'partitions': ['ESP', 'root']},
        'bootloader': 'systemd-boot',
        'account': {'username': username, 'password_in_plan': False},
        'encryption': {'enabled': encrypt}, 'optional_packages': [],
        'codecs': {'selected': False},
        'executor': {'adapter': 'archinstall', 'adapter_version': ARCHINSTALL_VERSION},
    }
    if mode == 'replace-existing':
        plan['installation_mode'] = mode
    plan['review_digest'] = review_digest(plan)
    validate_plan(plan)
    password = secret('New account password (hidden): ')
    confirmation = secret('Confirm password (hidden): ')
    if not password or '\x00' in password or '\n' in password or password != confirmation:
        raise Refusal('Passwords must be nonempty, single-line and match')
    del confirmation
    encryption_password = None
    if encrypt:
        output('Disk unlock uses the US keyboard layout. Keep the disk passphrase separately backed up; there is no automatic recovery key.')
        encryption_password = secret('New disk encryption passphrase (hidden): ')
        confirmation = secret('Confirm disk encryption passphrase (hidden): ')
        if (len(encryption_password) < 12 or
                not encryption_password.strip() or
                any(not 32 <= ord(c) <= 126 for c in encryption_password) or
                encryption_password != confirmation or encryption_password == password):
            raise Refusal('Disk passphrases must match, differ from the account password, and contain at least 12 printable ASCII characters')
        del confirmation
    output('Whole-disk installation erases all data, including Windows, on the selected disk.')
    output('Internal installer: LUKS2-encrypted ext4 root; unencrypted 1 GiB FAT32 ESP at /boot; no automatic reboot.'
           if encrypt else 'Internal installer: unencrypted ext4 root, 1 GiB FAT32 ESP at /boot; no automatic reboot.')
    output('Packages: ' + ', '.join(executor.packages))
    output(json.dumps(plan, sort_keys=True, indent=2, ensure_ascii=True))
    phrase = f'ERASE {path}'
    if mode == 'replace-existing':
        output('REPLACEMENT DESTROYS ALL existing operating systems, Omarchy and ALL personal data on this disk. No rollback or secure data sanitization is provided.')
        phrase = f"REPLACE {path} {plan['review_digest']}"
    if ask(f'Type {phrase} exactly to proceed: ') != phrase:
        raise Refusal('Disk confirmation did not match; cancelled')

    def guard():
        validate_plan(plan)
        if probe(path) != plan['target']:
            raise Refusal('Target identity or size changed since review')

    try:
        if encrypt:
            executor.execute(plan, password, guard, encryption_password=encryption_password)
        else:
            executor.execute(plan, password, guard)
    finally:
        # Python strings cannot be securely zeroized. Never serialize this value.
        password = None
        encryption_password = None
    output('Installation completed. Target remains mounted; inspect before manually rebooting.')


def check_firmware(efi=Path('/sys/firmware/efi')):
    if (efi / 'fw_platform_size').read_text().strip() != '64':
        raise Refusal('Only 64-bit UEFI firmware is supported')
    for variable in (efi / 'efivars').glob('SecureBoot-*'):
        value = variable.read_bytes()
        if len(value) != 5 or value[4] != 0:
            raise Refusal('Secure Boot must be disabled; this installer does not sign kernels')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Internal Wilsof interactive installer (archinstall 4.5)')
    parser.add_argument('--validate', metavar='PLAN', help='Read-only schema/digest/runtime validation; no probing')
    parser.add_argument('--replace-existing', action='store_true',
                        help='Explicit full-disk replacement; requires exact target-and-plan confirmation')
    parser.add_argument('--encrypt', action='store_true',
                        help='Explicit encrypted-root intent (already mandatory for installation); ESP stays unencrypted')
    args = parser.parse_args(argv)
    if args.validate and (args.replace_existing or args.encrypt):
        parser.error('--validate cannot be combined with installation options')
    try:
        if args.validate:
            validate_plan(json.loads(Path(args.validate).read_text()))
            print('Plan valid (schema, canonical digest and supported runtime choices only; disk not probed).')
            return 0
        if not sys.stdin.isatty() or not sys.stdout.isatty() or os.geteuid() != 0:
            raise Refusal('Installation requires root and an interactive terminal')
        check_platform(platform.machine(), Path('/sys/firmware/efi').is_dir())
        check_firmware()
        # copytoram unmounts bootmnt; the immutable live root remains mounted.
        if not Path('/run/archiso/airootfs').is_mount():
            raise Refusal('Installation is available only from booted Archiso live media')
        check_live_capacity()
        # Keep target parents traversable regardless of the invoking shell's
        # umask. Password/key directories retain their explicit private modes.
        previous_umask = os.umask(0o022)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', getpass.GetPassWarning)
                # Owner policy: every new interactive installation requires encryption.
                # --encrypt is retained as explicit intent, not an optional downgrade gate.
                if args.replace_existing:
                    interactive(ArchinstallExecutor(guest=guest_policy(), defer_api=True, encrypt=True), mode='replace-existing')
                else:
                    interactive(ArchinstallExecutor(guest=guest_policy(), encrypt=True))
        finally:
            os.umask(previous_umask)
        return 0
    except (KeyboardInterrupt, EOFError):
        print('Cancelled. If disk operations started, the target may be partially installed.', file=sys.stderr)
        return 130
    except Refusal as exc:
        print(f'Stopped: {exc}. No automatic retry or reboot.', file=sys.stderr)
        return 1
    except Exception:
        # Never print arbitrary backend exceptions: they can contain transient inputs.
        print('Installation/validation failed. Inspect local backend logs; a target may be partially installed. '
              'No automatic retry or reboot.', file=sys.stderr)
        return 1


def check_platform(architecture, uefi):
    if architecture != 'x86_64' or not uefi:
        raise Refusal('Only x86_64 UEFI installations are supported')


def assess_inventory(path, inventory):
    if not re.fullmatch(r'/dev/[a-zA-Z0-9_-]+', path):
        raise Refusal('Select an explicit canonical whole-disk /dev path')
    nodes = []

    def visit(items):
        for item in items:
            nodes.append(item)
            visit(item.get('children', []))

    visit(inventory['blockdevices'])
    matches = [node for node in nodes if node['path'] == path]
    if len(matches) != 1:
        raise Refusal('Disk not uniquely present in inventory')
    node = matches[0]
    if node['type'] != 'disk' or node['ro'] or node.get('children'):
        raise Refusal('Target must be a writable whole disk with no child devices')
    if node.get('pttype') or node.get('fstype'):
        raise Refusal('Target has an existing partition table or filesystem')
    aliases = [item for item in nodes if item.get('maj:min') == node['maj:min']]
    if any(any(item.get('mountpoints', [])) for item in aliases):
        raise Refusal('Mounted disks (including live media) are never targets')
    if int(node['size']) < 16 * 1024**3:
        raise Refusal('Target must be at least 16 GiB')
    if not (node.get('wwn') or node.get('serial')):
        raise Refusal('Target requires a stable WWN or serial identifier')
    identity = [node.get(key) for key in ('wwn', 'serial', 'model', 'maj:min')]
    return {
        'path': path, 'size_bytes': int(node['size']), 'expected_empty': True,
        'identity': 'sha256-' + hashlib.sha256(json.dumps(identity).encode()).hexdigest(),
        # Public review labels are separate from the private stable identifier.
        # They also participate in the final probe equality and plan digest.
        'display': {
            'manufacturer': node.get('vendor') or 'not reported',
            'model': node.get('model') or 'not reported',
            'transport': node.get('tran') or 'not reported',
            'removable': node.get('rm'),
        },
    }


def assess_replacement(path, inventory):
    """Review only; retain blank-mode identity/mount/size guards unchanged."""
    flat = []
    def visit(items):
        for item in items:
            flat.append(item)
            visit(item.get('children', []))
    visit(inventory['blockdevices'])
    matches = [item for item in flat if item.get('path') == path]
    if len(matches) != 1:
        raise Refusal('Replacement target is not uniquely present')
    disk = matches[0]
    # Only direct physical partitions are supported. Never erase active RAID,
    # device mapper, encryption or nested mappings through this workflow.
    children = disk.get('children', [])
    if (disk.get('pttype') not in (None, '', 'gpt', 'dos') or
            any(p.get('type') != 'part' or p.get('children') for p in children)):
        raise Refusal('Unsupported or active replacement partition layout')
    selected = [disk, *children]
    majors = [p.get('maj:min') for p in selected]
    if len(set(majors)) != len(majors) or any(not isinstance(m, str) or not re.fullmatch(r'\d+:\d+', m) for m in majors):
        raise Refusal('Ambiguous replacement device numbers')
    for item in selected:
        name = item.get('path', '')
        if (not re.fullmatch(r'/dev/[A-Za-z0-9_-]+', name) or
                item.get('ro') or item.get('fstype') in ('iso9660', 'udf') or
                any(item.get('mountpoints', [])) or
                any(any(p.get('mountpoints', [])) for p in flat if p.get('maj:min') == item['maj:min'])):
            raise Refusal('Mounted, read-only or installation-media targets are forbidden')
        # A second occurrence means an ambiguous tree or an active mapping.
        if sum(p.get('maj:min') == item['maj:min'] for p in flat) != 1:
            raise Refusal('Replacement device has ambiguous aliases or mappings')
    for other in inventory['blockdevices']:
        if other is disk:
            continue
        if any(disk.get(k) and disk.get(k) == other.get(k) for k in ('serial', 'wwn')):
            raise Refusal('Replacement target has a duplicated stable identifier')
    sanitized = copy.deepcopy(inventory)
    target = next(p for p in sanitized['blockdevices'] if p.get('path') == path)
    target.pop('children', None)
    target['pttype'] = target['fstype'] = None
    result = assess_inventory(path, sanitized)
    result['expected_empty'] = False
    result['existing'] = [{
        'path': p['path'], 'device_number': p['maj:min'],
        'size_bytes': int(p['size']), 'table': p.get('pttype'),
        'filesystem': p.get('fstype'), 'partition_type': p.get('parttype'),
        'efi': str(p.get('parttype', '')).lower() == 'c12a7328-f81f-11d2-ba4b-00a0c93ec93b',
    } for p in selected]
    return result


def live_device_uuids():
    # copytoram can unmount bootmnt: retain the kernel-selected media identity.
    import shlex
    return {token.split('=', 1)[1] for token in shlex.split(Path('/proc/cmdline').read_text())
            if token.startswith(('archisosearchuuid=', 'archisodeviceuuid='))}


def device_fingerprint(row):
    """Read-only bounded header identity; reject links, wrong dev_t and sizes."""
    import fcntl
    import struct
    path = Path(row['path'])
    if path.resolve(strict=True) != path or any(p.is_symlink() for p in (path, *path.parents)):
        raise Refusal('Replacement device path is not canonical')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC), 'rb') as stream:
        info = os.fstat(stream.fileno())
        number = f'{os.major(info.st_rdev)}:{os.minor(info.st_rdev)}'
        if not stat.S_ISBLK(info.st_mode) or number != row['device_number']:
            raise Refusal('Replacement device node identity changed')
        size = struct.unpack('Q', fcntl.ioctl(stream.fileno(), 0x80081272, bytes(8)))[0]  # BLKGETSIZE64
        if size != row['size_bytes'] or size < 131072:
            raise Refusal('Replacement device size changed')
        data = os.pread(stream.fileno(), 65536, 0) + os.pread(stream.fileno(), 65536, size - 65536)
        if len(data) != 131072:
            raise Refusal('Incomplete replacement device header read')
        return hashlib.sha256(data).hexdigest()


def probe_replacement(path):
    argv = REPLACEMENT_LSBLK
    def capture():
        inventory = read_json(argv)
        result = assess_replacement(path, inventory)
        uuids = live_device_uuids()
        flat = []
        def visit(items):
            for item in items:
                flat.append(item)
                visit(item.get('children', []))
        visit(inventory['blockdevices'])
        for row in result['existing']:
            item = next(p for p in flat if p['path'] == row['path'])
            if item.get('uuid') and item['uuid'] in uuids:
                raise Refusal('Running live installation medium is never a target')
            if has_holders(row['path']):
                raise Refusal('Replacement target has an active block-device holder')
            signatures = read_json(['wipefs', '--no-act', '--json', row['path']])['signatures']
            if not isinstance(signatures, list):
                raise Refusal('Invalid replacement signature inventory')
            if any(p.get('type') in ('iso9660', 'udf') or p.get('uuid') in uuids for p in signatures):
                raise Refusal('Live-media signature cannot be a replacement target')
            row['signatures'] = sorted([{k: p.get(k) for k in ('type', 'offset', 'uuid')}
                                        for p in signatures], key=lambda p: json.dumps(p, sort_keys=True))
            row['header_sha256'] = device_fingerprint(row)
        return result
    before, after = capture(), capture()
    if before != after:
        raise Refusal('Replacement identity, layout or signatures changed during probe')
    return after




@contextmanager
def open_reviewed_devices(rows):
    """Claim the whole disk exclusively; pin every write to an open block inode."""
    import fcntl
    import struct
    with ExitStack() as stack:
        handles = {}
        for index, row in enumerate(rows):
            path = Path(row['path'])
            if path.resolve(strict=True) != path or any(p.is_symlink() for p in (path, *path.parents)):
                raise Refusal('Replacement path changed before exclusive claim')
            flags = os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW
            if index == 0:
                flags |= os.O_EXCL
            stream = stack.enter_context(os.fdopen(os.open(path, flags), 'rb'))
            fd = stream.fileno()
            info = os.fstat(fd)
            size = struct.unpack('Q', fcntl.ioctl(fd, 0x80081272, bytes(8)))[0]
            if (not stat.S_ISBLK(info.st_mode) or
                    f'{os.major(info.st_rdev)}:{os.minor(info.st_rdev)}' != row['device_number'] or
                    size != row['size_bytes']):
                raise Refusal('Replacement block identity changed before exclusive claim')
            data = os.pread(fd, 65536, 0) + os.pread(fd, 65536, size - 65536)
            if len(data) != 131072 or hashlib.sha256(data).hexdigest() != row['header_sha256']:
                raise Refusal('Replacement headers changed before exclusive claim')
            handles[row['path']] = stream
        yield handles


def load_blkid():
    """Bind only documented libblkid APIs; no pathname-based destructive reopen."""
    import ctypes
    try:
        lib = ctypes.CDLL('libblkid.so.1', use_errno=True)
        pointer, integer = ctypes.c_void_p, ctypes.c_int
        signatures = {
            'blkid_new_probe': (pointer, []),
            'blkid_free_probe': (None, [pointer]),
            'blkid_probe_set_device': (integer, [pointer, integer, ctypes.c_longlong, ctypes.c_longlong]),
            'blkid_probe_enable_superblocks': (integer, [pointer, integer]),
            'blkid_probe_set_superblocks_flags': (integer, [pointer, integer]),
            'blkid_probe_enable_partitions': (integer, [pointer, integer]),
            'blkid_probe_set_partitions_flags': (integer, [pointer, integer]),
            'blkid_do_probe': (integer, [pointer]),
            'blkid_do_wipe': (integer, [pointer, integer]),
        }
        for name, (result, args) in signatures.items():
            function = getattr(lib, name)
            function.restype, function.argtypes = result, args
        return lib
    except (OSError, AttributeError) as error:
        raise Refusal('Required descriptor-bound libblkid API is unavailable') from error


def wipe_bound_fd(fd):
    """Wipe signatures on the validated open object, never its mutable path.

    libblkid blkid_probe_set_device retains the supplied descriptor. do_wipe
    writes that descriptor; unlike wipefs CLI it cannot canonicalize /proc/fd
    and reopen a different disk. Whole-disk/block/identity gates are the caller's.
    """
    lib = load_blkid()
    probe = lib.blkid_new_probe()
    if not probe:
        raise Refusal('Cannot allocate signature probe; target may be partially erased')
    try:
        for status in (lib.blkid_probe_set_device(probe, fd, 0, 0),
                       lib.blkid_probe_enable_superblocks(probe, 1),
                       lib.blkid_probe_set_superblocks_flags(probe, (1 << 9) | (1 << 10)),
                       lib.blkid_probe_enable_partitions(probe, 1),
                       lib.blkid_probe_set_partitions_flags(probe, (1 << 3) | (1 << 1))):
            if status != 0:
                raise Refusal('Cannot initialize bound signature erasure')
        for _ in range(256):
            status = lib.blkid_do_probe(probe)
            if status == 1:
                os.fsync(fd)
                return
            if status != 0 or lib.blkid_do_wipe(probe, 0) != 0:
                raise Refusal('Bound signature erasure failed; target may be partially erased')
        raise Refusal('Signature erasure iteration limit; target may be partially erased')
    finally:
        lib.blkid_free_probe(probe)


def reread_partition_table(fd):
    import errno
    import fcntl
    import time
    # BLKRRPART stays bound to the selected open disk. Short-lived raw readers
    # (including udev probes) can keep old partitions open after signatures go.
    # Retry only this idempotent kernel notification, never erasure/installation.
    for attempt in range(10):
        try:
            fcntl.ioctl(fd, 0x125f)
            return
        except OSError as error:
            if error.errno != errno.EBUSY or attempt == 9:
                raise
            time.sleep(0.2)


def erase_replacement(plan):
    """Irreversible only after exact confirmation and complete fresh review equality.

    Remove child signatures before their partition table so archinstall's global
    import cannot auto-mount old Btrfs. Other Btrfs devices remain a hard refusal.
    This destroys data access, not every old data byte; it is not secure erasure.
    """
    validate_plan(plan)
    if plan.get('installation_mode') != 'replace-existing':
        raise Refusal('Erasure requires explicit replacement mode')
    verify_archinstall_metadata()
    load_blkid()  # Check the real native API before the first destructive call.
    target = plan['target']
    path = target['path']
    if probe_replacement(path) != target:
        raise Refusal('Replacement review changed before erasure')
    from importlib.metadata import entry_points
    inventory = read_json(REPLACEMENT_LSBLK)
    other = {'blockdevices': [p for p in inventory['blockdevices'] if p['path'] != path]}
    check_arch_import_environment(other, list(entry_points().select(group='archinstall.plugin')))
    with open_reviewed_devices(target['existing']) as handles:
        if probe_replacement(path) != target:
            raise Refusal('Replacement review changed after exclusive claim')
        for row in reversed(target['existing']):
            stream = handles[row['path']]
            fd = stream.fileno()
            wipe_bound_fd(fd)
            if row['path'] == path:
                reread_partition_table(fd)
            # Close children before the disk's explicit BLKRRPART.
            stream.close()
    subprocess.run(['udevadm', 'settle', '--timeout=30'], check=True, capture_output=True, timeout=35)
    erased = probe_replacement(path)
    if (any(erased[k] != target[k] for k in ('path', 'size_bytes', 'identity', 'display')) or
            len(erased['existing']) != 1 or any(erased['existing'][0][k] for k in ('table', 'filesystem', 'signatures'))):
        raise Refusal('Target erasure is incomplete; do not retry automatically')
    return erased
