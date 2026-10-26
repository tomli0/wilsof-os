"""Internal, interactive-only Wilsof adapter. Importing this module is read-only."""
import argparse
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

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ARCHINSTALL_VERSION = '4.5'
LSBLK = ['lsblk', '--json', '--bytes', '--paths', '--output',
         'PATH,KNAME,TYPE,SIZE,MAJ:MIN,RO,WWN,SERIAL,MODEL,PTTYPE,FSTYPE,MOUNTPOINTS']


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
    if plan['encryption']['enabled']:
        raise Refusal('Encryption is not supported by this adapter')
    if plan['bootloader'] != 'systemd-boot':
        raise Refusal('Only systemd-boot is supported')
    name = plan['account']['username']
    if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', name) or name in {'root', 'greetd', 'nobody'}:
        raise Refusal('Unsupported username')
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


def load_archinstall():
    # Never import archinstall.main, args, scripts, or its CLI entrypoint.
    from importlib.metadata import entry_points, version
    from types import SimpleNamespace
    if version('archinstall') != ARCHINSTALL_VERSION:
        raise Refusal('Installed archinstall must be exactly 4.5')
    check_arch_import_environment(read_json(LSBLK),
                                  list(entry_points().select(group='archinstall.plugin')))
    from archinstall.lib.disk.device_handler import device_handler
    from archinstall.lib.disk.default_layouts import suggest_single_disk_layout
    from archinstall.lib.disk.filesystem import FilesystemHandler
    from archinstall.lib.installer import Installer
    from archinstall.lib.models.bootloader import Bootloader
    from archinstall.lib.models.device import DiskLayoutConfiguration, DiskLayoutType, FilesystemType, Unit
    from archinstall.lib.models.locale import LocaleConfiguration
    from archinstall.lib.models.users import Password, User
    return SimpleNamespace(**{key: value for key, value in locals().items()
                              if key not in {'version', 'SimpleNamespace'}})


def check_target_mount(path):
    if path.is_symlink() or not path.is_dir() or any(path.iterdir()):
        raise Refusal('Target mount directory must exist, be empty and not be a symlink')
    # findmnt lists the entire mount table, including mounts below an empty directory.
    mounts = read_json(['findmnt', '--json', '--list', '--output', 'TARGET'])
    if any(Path(item['target']) == path or path in Path(item['target']).parents
           for item in mounts['filesystems']):
        raise Refusal('Target mount directory already contains a mount')


class ArchinstallExecutor:
    def __init__(self, manifest=Path('/usr/share/wilsof/desktop-packages.txt'),
                 provision=Path('/usr/local/lib/wilsof/provision-target'),
                 target=Path('/mnt/wilsof'), guest=((), False)):
        self.guest_enabled = guest[1]
        self.packages = list(dict.fromkeys([
            'base', 'linux', 'linux-firmware', 'mkinitcpio', 'networkmanager', 'sudo', 'greetd',
            # Include upstream bootloader/microcode/accessibility additions in review.
            'efibootmgr', 'dosfstools', 'e2fsprogs', 'intel-ucode', 'amd-ucode',
            'brltty', 'espeakup', 'alsa-utils',
            *read_manifest(manifest), *guest[0],
        ]))
        self.manifest_digest = 'sha256-' + hashlib.sha256(
            json.dumps(self.packages, separators=(',', ':')).encode()).hexdigest()
        self.provision = Path(provision)
        self.target = Path(target)
        if not self.provision.is_file() or not os.access(self.provision, os.X_OK):
            raise Refusal('Required provision-target executable is missing')
        check_target_mount(self.target)
        self.api = load_archinstall()

    def execute(self, plan, password, guard):
        import asyncio
        validate_plan(plan)
        if plan.get('plan_id') != self.manifest_digest:
            raise Refusal('Reviewed package manifest differs from executor')
        check_target_mount(self.target)
        api = self.api
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
        handler = api.FilesystemHandler(config)
        guard()  # Reprobe identity/blankness after all interactive input.
        # The full-disk scan may be lengthy: revalidate the destination last too.
        check_target_mount(self.target)
        handler.perform_filesystem_operations()
        with api.Installer(self.target, config, base_packages=list(self.packages),
                           kernels=['linux']) as installation:
            installation.mount_ordered_layout()
            locale = api.LocaleConfiguration('us', 'en_US.UTF-8', 'UTF-8')
            # 4.5 minimal_installation discards set_locale's result, and set_locale
            # is not idempotent. Perform one checked locale call after base install.
            installation.minimal_installation(mkinitcpio=False, hostname='wilsof', locale_config=None)
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


def interactive(executor, *, probe=probe_disk, ask=input, secret=getpass.getpass, output=print):
    path = ask('Target whole-disk path (no default; e.g. /dev/vda): ')
    output('Checking that every byte of the target is zero; this can take time.')
    target = probe(path)
    username = ask('New administrator username: ')
    plan = {
        'schema': 'wilsof.install-plan/v1', 'plan_id': executor.manifest_digest,
        'target': target,
        'layout': {'mode': 'whole-disk', 'table': 'gpt', 'firmware': 'uefi',
                   'partitions': ['ESP', 'root']},
        'bootloader': 'systemd-boot',
        'account': {'username': username, 'password_in_plan': False},
        'encryption': {'enabled': False}, 'optional_packages': [],
        'codecs': {'selected': False},
        'executor': {'adapter': 'archinstall', 'adapter_version': ARCHINSTALL_VERSION},
    }
    plan['review_digest'] = review_digest(plan)
    validate_plan(plan)
    password = secret('New account password (hidden): ')
    confirmation = secret('Confirm password (hidden): ')
    if not password or '\x00' in password or '\n' in password or password != confirmation:
        raise Refusal('Passwords must be nonempty, single-line and match')
    del confirmation
    output('Whole-disk installation erases all data, including Windows, on the selected disk.')
    output('Internal installer: unencrypted ext4 root, 1 GiB FAT32 ESP at /boot; no automatic reboot.')
    output('Packages: ' + ', '.join(executor.packages))
    output(json.dumps(plan, sort_keys=True, indent=2, ensure_ascii=True))
    if ask(f'Type ERASE {path} exactly to proceed: ') != f'ERASE {path}':
        raise Refusal('Disk confirmation did not match; cancelled')

    def guard():
        validate_plan(plan)
        if probe(path) != plan['target']:
            raise Refusal('Target identity or size changed since review')

    try:
        executor.execute(plan, password, guard)
    finally:
        # Python strings cannot be securely zeroized. Never serialize this value.
        password = None
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
    args = parser.parse_args(argv)
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
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            interactive(ArchinstallExecutor(guest=guest_policy()))
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
    }
