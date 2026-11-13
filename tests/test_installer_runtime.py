"""No real block devices or Arch APIs are used in these tests."""
import copy
import hashlib
import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def runtime():
    assert (ROOT / 'installer/wilsof_installer.py').exists(), 'runtime adapter missing'
    return importlib.import_module('installer.wilsof_installer')


def signed_plan():
    plan = {
        'schema': 'wilsof.install-plan/v1',
        'target': {'path': '/dev/vda', 'size_bytes': 32 * 1024**3,
                   'identity': 'sha256-disk', 'expected_empty': True},
        'layout': {'mode': 'whole-disk', 'table': 'gpt', 'firmware': 'uefi',
                   'partitions': ['ESP', 'root']},
        'bootloader': 'systemd-boot',
        'account': {'username': 'alice', 'password_in_plan': False},
        'encryption': {'enabled': False}, 'optional_packages': [],
        'codecs': {'selected': False},
        'executor': {'adapter': 'archinstall', 'adapter_version': '4.5'},
    }
    plan['review_digest'] = 'sha256-' + hashlib.sha256(
        json.dumps(plan, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
    ).hexdigest()
    return plan


def disk_inventory():
    return {'blockdevices': [{
        'path': '/dev/vda', 'kname': 'vda', 'type': 'disk',
        'size': 32 * 1024**3, 'maj:min': '254:0', 'ro': False,
        'wwn': None, 'serial': 'disposable-test-disk', 'model': 'VirtIO',
        'pttype': None, 'fstype': None, 'mountpoints': [None],
    }]}


def test_inventory_produces_private_stable_identity():
    m = runtime()
    target = m.assess_inventory('/dev/vda', disk_inventory())
    assert target['path'] == '/dev/vda'
    assert target['size_bytes'] == 32 * 1024**3
    assert target['expected_empty'] is True
    assert target['identity'].startswith('sha256-')
    assert 'disposable-test-disk' not in json.dumps(target)


@pytest.mark.parametrize('change', [
    {'children': [{'path': '/dev/vda1', 'mountpoints': [None]}]},
    {'mountpoints': ['/run/archiso/bootmnt']},
    {'mountpoints': ['/mnt']}, {'fstype': 'ext4'}, {'pttype': 'gpt'},
    {'ro': True}, {'type': 'loop'}, {'serial': None},
])
def test_inventory_rejects_used_or_unidentifiable_disks(change):
    m = runtime()
    inventory = disk_inventory()
    inventory['blockdevices'][0].update(change)
    with pytest.raises(m.Refusal):
        m.assess_inventory('/dev/vda', inventory)


@pytest.mark.parametrize('arch,uefi', [('aarch64', True), ('x86_64', False)])
def test_platform_rejects_unsupported_firmware_and_architecture(arch, uefi):
    m = runtime()
    with pytest.raises(m.Refusal):
        m.check_platform(arch, uefi)


def test_blank_check_reads_entire_disk_and_rejects_short_reads():
    import io
    m = runtime()
    m.verify_blank(io.BytesIO(bytes(1024)), 1024)
    for data, size in [(bytes(1023) + b'x', 1024), (bytes(2), 1024)]:
        with pytest.raises(m.Refusal):
            m.verify_blank(io.BytesIO(data), size)


def test_probe_uses_read_only_signature_inspection_and_final_inventory(monkeypatch):
    m = runtime()
    commands = []
    def command(argv):
        commands.append(argv)
        return disk_inventory() if argv[0] == 'lsblk' else {'signatures': []}
    monkeypatch.setattr(m, 'read_json', command)
    monkeypatch.setattr(m, 'check_block_and_blank', lambda path, size: None)
    monkeypatch.setattr(m, 'has_holders', lambda path: False)
    assert m.probe_disk('/dev/vda') == m.assess_inventory('/dev/vda', disk_inventory())
    assert commands[1] == ['wipefs', '--no-act', '--json', '/dev/vda']
    assert commands[0] == commands[-1]
    monkeypatch.setattr(m, 'read_json', lambda argv: disk_inventory() if argv[0] == 'lsblk' else {'signatures': [{'type': 'ext4'}]})
    with pytest.raises(m.Refusal):
        m.probe_disk('/dev/vda')


def test_interactive_review_precedes_confirmation_and_fresh_probe():
    m = runtime()
    events, output = [], []
    target = signed_plan()['target']
    class Executor:
        packages = ['base', 'hyprland']
        manifest_digest = 'sha256-fixture'
        def execute(self, plan, password, guard):
            events.append('prepare')
            guard()
            events.append('destructive')
            assert password == 'transient-only'
            assert 'transient-only' not in json.dumps(plan)
    answers = iter(['/dev/vda', 'alice', 'ERASE /dev/vda'])
    def probe(path):
        events.append('probe')
        return copy.deepcopy(target)
    def ask(prompt):
        if prompt.startswith('Type'):
            assert any('Whole-disk installation erases all data' in s for s in output)
            assert any('review_digest' in s for s in output)
        return next(answers)
    m.interactive(Executor(), probe=probe, ask=ask,
                  secret=lambda prompt: 'transient-only', output=output.append)
    assert events == ['probe', 'prepare', 'probe', 'destructive']
    assert 'transient-only' not in '\n'.join(output)


@pytest.mark.parametrize('problem', ['confirmation', 'password', 'identity', 'size', 'mounted'])
def test_interactive_aborts_before_backend_writes(problem):
    m = runtime()
    writes = []
    target = signed_plan()['target']
    count = 0
    def probe(path):
        nonlocal count
        count += 1
        result = copy.deepcopy(target)
        if count > 1:
            if problem == 'mounted':
                raise m.Refusal('Mounted target')
            if problem in {'identity', 'size'}:
                result['identity' if problem == 'identity' else 'size_bytes'] = 'changed'
        return result
    class Executor:
        packages = ['base']
        manifest_digest = 'sha256-fixture'
        def execute(self, plan, password, guard):
            guard()
            writes.append(True)
    answers = iter(['/dev/vda', 'alice', 'wrong' if problem == 'confirmation' else 'ERASE /dev/vda'])
    secrets = iter(['one', 'two' if problem == 'password' else 'one'])
    with pytest.raises(m.Refusal):
        m.interactive(Executor(), probe=probe, ask=lambda p: next(answers),
                      secret=lambda p: next(secrets), output=lambda s: None)
    assert not writes


def test_manifest_requires_package_names_not_options_or_shell(tmp_path):
    m = runtime()
    manifest = tmp_path / 'packages'
    manifest.write_text('# Core desktop\nhyprland\ngreetd\n')
    assert m.read_manifest(manifest) == ['hyprland', 'greetd']
    for contents in ['', '--overwrite\n', 'pkg;command\n', 'repo/pkg\n', 'pkg with space\n']:
        manifest.write_text(contents)
        with pytest.raises(m.Refusal):
            m.read_manifest(manifest)


@pytest.fixture
def fake_arch(tmp_path, monkeypatch):
    from types import SimpleNamespace as NS
    from unittest.mock import Mock
    events = []
    monkeypatch.setattr(runtime(), 'wireless', {
        'stage': lambda *a: events.append('wl-stage'),
        'verify': lambda *a: events.append('wl-verify'),
    }, raising=False)
    # External live-root/package boundary. Real policy behavior has separate tests.
    policy = {'date': '2026-11-01'}
    monkeypatch.setattr(runtime(), 'snapshot', {
        'preflight': lambda *a, **k: {'snapshot': dict(policy), 'packages': []},
        'read': lambda *a: dict(policy),
        'stage': lambda *a: dict(policy),
        'verify_installed': lambda *a: None,
    }, raising=False)
    boot = NS(mountpoint=Path('/boot'), fs_type='fat32')
    root = NS(mountpoint=Path('/'), fs_type='ext4', safe_dev_path=Path('/dev/vda2'))
    mod = NS(partitions=[boot, root])
    async def suggest(device, *, filesystem_type, separate_home):
        assert filesystem_type == 'ext4' and separate_home is False
        return mod
    session = Mock()
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=False)
    session.mkinitcpio.return_value = True

    locale_generated = False
    def generate_locale(locale):
        nonlocal locale_generated
        if locale_generated:
            return False  # archinstall 4.5 only matches commented locale.gen entries.
        locale_generated = True
        return True
    session.set_locale.side_effect = generate_locale
    def minimal_installation(**kwargs):
        if kwargs.get('locale_config') is not None:
            session.set_locale(kwargs['locale_config'])
    session.minimal_installation.side_effect = minimal_installation
    session.set_user_password.return_value = True
    session.post_install_check.return_value = []
    session.create_users.side_effect = lambda user: events.append('user')
    fs = Mock()
    fs.perform_filesystem_operations.side_effect = lambda: events.append('format')
    api = NS(
        device_handler=NS(load_devices=Mock(), get_device=lambda path: NS(
            partition_infos=[], device_info=NS(path=path, read_only=False,
                total_size=NS(convert=lambda unit: NS(value=32 * 1024**3))))),
        Unit=NS(B='bytes'),
        suggest_single_disk_layout=suggest,
        DiskLayoutConfiguration=lambda **kw: NS(**kw),
        DiskLayoutType=NS(Default='default'), FilesystemType=NS(EXT4='ext4', FAT32='fat32'),
        FilesystemHandler=Mock(return_value=fs), Installer=Mock(return_value=session),
        Bootloader=NS(Systemd='systemd'), LocaleConfiguration=lambda *args: args,
        Password=lambda **kw: NS(**kw), User=lambda *args: NS(args=args),
    )
    manifest = tmp_path / 'packages'
    manifest.write_text('hyprland\ngreetd\n')
    hook = tmp_path / 'provision-target'
    hook.write_text('#!/bin/sh\nexit 0\n')
    hook.chmod(0o755)
    target = tmp_path / 'target'
    target.mkdir()
    return NS(api=api, events=events, session=session, fs=fs,
              manifest=manifest, hook=hook, target=target)


@pytest.mark.parametrize('mutation', ['file', 'symlink', 'mount'])
def test_executor_rechecks_mount_destination_after_final_disk_scan(fake_arch, monkeypatch, mutation):
    m, f = runtime(), fake_arch
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    mounts = []
    monkeypatch.setattr(m, 'read_json', lambda argv: {'filesystems': mounts})
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target)
    plan = signed_plan()
    plan['plan_id'] = executor.manifest_digest
    plan['review_digest'] = m.review_digest(plan)
    def guard():
        if mutation == 'file':
            (f.target / 'unexpected').write_text('concurrent state')
        elif mutation == 'symlink':
            f.target.rmdir()
            f.target.symlink_to(f.target.parent, target_is_directory=True)
        else:
            mounts.append({'target': str(f.target)})
    with pytest.raises(m.Refusal, match='Target mount directory'):
        executor.execute(plan, 'transient-only', guard)
    f.fs.perform_filesystem_operations.assert_not_called()


@pytest.mark.parametrize('failure', [None, 'guard', 'password', 'initramfs', 'provision', 'postcheck'])
def test_arch_executor_orders_guard_and_propagates_failures(fake_arch, monkeypatch, failure):
    m = runtime()
    f = fake_arch
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    monkeypatch.setattr(m, 'check_target_mount', lambda path: None)
    def provision(argv, **kwargs):
        assert argv == [str(f.hook), str(f.target), 'alice']
        f.events.append('provision')
        if failure == 'provision':
            raise OSError('provision failed')
    monkeypatch.setattr(m.subprocess, 'run', provision)
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target)
    plan = signed_plan()
    plan['plan_id'] = executor.manifest_digest
    plan['review_digest'] = m.review_digest(plan)
    def guard():
        f.events.append('guard')
        if failure == 'guard':
            raise m.Refusal('changed disk')
    if failure == 'password':
        f.session.set_user_password.return_value = False
    if failure == 'initramfs':
        f.session.mkinitcpio.return_value = False
    if failure == 'postcheck':
        f.session.post_install_check.return_value = ['base']
    if failure:
        with pytest.raises((m.Refusal, OSError)):
            executor.execute(plan, 'transient-only', guard)
    else:
        # A real bootctl install creates this file; fixture only, never a disk.
        fallback = f.target / 'boot/EFI/BOOT/BOOTX64.EFI'
        fallback.parent.mkdir(parents=True)
        fallback.write_bytes(b'fixture')
        executor.execute(plan, 'transient-only', guard)
        assert f.events == ['guard', 'format', 'wl-stage', 'wl-verify', 'user', 'provision']
        f.session.add_bootloader.assert_called_once_with('systemd')
        f.session.enable_service.assert_called_once_with(['NetworkManager', 'greetd'])
        f.session.genfstab.assert_called_once()
        f.session.set_locale.assert_called_once()
        f.session.set_vconsole.assert_called_once_with(('us', 'en_US.UTF-8', 'UTF-8'))
        assert f.session.minimal_installation.call_args.kwargs['locale_config'] is None
        assert 'linux-firmware' in f.api.Installer.call_args.kwargs['base_packages']
        assert 'mkinitcpio' in f.api.Installer.call_args.kwargs['base_packages']
        assert 'efibootmgr' in executor.packages
        assert {'intel-ucode', 'amd-ucode', 'brltty', 'espeakup', 'alsa-utils'} <= set(executor.packages)
        f.api.device_handler.load_devices.assert_not_called()
    assert f.events[0] == 'guard'
    if failure == 'guard':
        f.fs.perform_filesystem_operations.assert_not_called()


@pytest.mark.parametrize('virt,channel,expected', [
    ('qemu', True, True), ('kvm', False, False), ('none', True, False),
])
def test_guest_agent_is_installed_for_qemu_but_enabled_only_with_channel(virt, channel, expected, monkeypatch):
    from types import SimpleNamespace
    m = runtime()
    monkeypatch.setattr(m.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout=virt+'\n'))
    assert m.guest_policy(channel) == (['qemu-guest-agent'] if virt in {'qemu', 'kvm'} else [], expected)


def test_arch_import_guard_rejects_btrfs_and_plugins_before_import(monkeypatch):
    m = runtime()
    inventory = disk_inventory()
    inventory['blockdevices'][0]['fstype'] = 'btrfs'
    with pytest.raises(m.Refusal, match='Btrfs'):
        m.check_arch_import_environment(inventory, [])
    with pytest.raises(m.Refusal, match='plugins'):
        m.check_arch_import_environment(disk_inventory(), ['untrusted-plugin'])


def test_read_only_cli_never_loads_backend_or_probes(tmp_path, monkeypatch, capsys):
    m = runtime()
    def forbidden(*args, **kwargs):
        pytest.fail('read-only CLI touched backend or disks')
    monkeypatch.setattr(m, 'load_archinstall', forbidden)
    monkeypatch.setattr(m, 'probe_disk', forbidden)
    plan_file = tmp_path / 'plan.json'
    plan_file.write_text(json.dumps(signed_plan()))
    assert m.main(['--validate', str(plan_file)]) == 0
    assert 'valid' in capsys.readouterr().out.lower()


def test_entrypoint_help_is_safe_and_import_is_lazy():
    import subprocess
    import sys
    m = runtime()
    result = subprocess.run([sys.executable, str(ROOT / 'bin/wilsof-install'), '--help'],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert '--validate' in result.stdout
    result = subprocess.run([sys.executable, '-c',
                             'import sys; import installer.wilsof_installer; '
                             'assert not any(s == "archinstall" or s.startswith("archinstall.") for s in sys.modules)'],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_interactive_cli_refuses_non_terminal(monkeypatch):
    m = runtime()
    monkeypatch.setattr(m.sys.stdin, 'isatty', lambda: False)
    assert m.main([]) != 0


def test_payload_package_is_not_shadowed_by_python_installer():
    assert (ROOT / 'installer/__init__.py').is_file(), 'payload must be a regular package'


@pytest.mark.parametrize('channel', [False, True])
def test_executor_guest_agent_service_policy(fake_arch, monkeypatch, channel):
    m = runtime()
    f = fake_arch
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    monkeypatch.setattr(m, 'check_target_mount', lambda path: None)
    monkeypatch.setattr(m.subprocess, 'run', lambda *args, **kw: None)
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target,
                                    guest=(['qemu-guest-agent'], channel))
    plan = signed_plan()
    plan['plan_id'] = executor.manifest_digest
    plan['review_digest'] = m.review_digest(plan)
    fallback = f.target / 'boot/EFI/BOOT/BOOTX64.EFI'
    fallback.parent.mkdir(parents=True)
    fallback.write_bytes(b'fixture')
    executor.execute(plan, 'transient-only', lambda: None)
    assert 'qemu-guest-agent' in executor.packages
    services = [call.args[0] for call in f.session.enable_service.call_args_list]
    assert ('qemu-guest-agent' in services) is channel


@pytest.mark.parametrize('state', ['nonempty', 'symlink', 'mounted'])
def test_target_mount_directory_refuses_unsafe_state(tmp_path, monkeypatch, state):
    m = runtime()
    target = tmp_path / 'target'
    target.mkdir()
    if state == 'nonempty':
        (target / 'existing').touch()
    if state == 'symlink':
        link = tmp_path / 'alias'
        link.symlink_to(target)
        target = link
    monkeypatch.setattr(m, 'read_json', lambda argv: {'filesystems': [{'target': str(target)}]})
    with pytest.raises(m.Refusal):
        m.check_target_mount(target)


@pytest.mark.parametrize('bits,secureboot', [('32', 0), ('64', 1)])
def test_firmware_refuses_32bit_uefi_and_enabled_secure_boot(tmp_path, bits, secureboot):
    m = runtime()
    (tmp_path / 'fw_platform_size').write_text(bits)
    variables = tmp_path / 'efivars'
    variables.mkdir()
    (variables / 'SecureBoot-fixture').write_bytes(bytes(4) + bytes([secureboot]))
    with pytest.raises(m.Refusal):
        m.check_firmware(tmp_path)


def test_firmware_accepts_64bit_uefi_without_secure_boot_capability(tmp_path):
    m = runtime()
    (tmp_path / 'fw_platform_size').write_text('64\n')
    m.check_firmware(tmp_path)


@pytest.mark.parametrize('stale', ['size', 'partitions'])
def test_backend_stale_inventory_cannot_trigger_writes(fake_arch, monkeypatch, stale):
    from types import SimpleNamespace as NS
    m = runtime()
    f = fake_arch
    device = f.api.device_handler.get_device(Path('/dev/vda'))
    if stale == 'size':
        device.device_info.total_size = NS(convert=lambda unit: NS(value=1))
    else:
        device.partition_infos = [NS()]
    f.api.device_handler.get_device = lambda path: device
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    monkeypatch.setattr(m, 'check_target_mount', lambda path: None)
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target)
    plan = signed_plan()
    plan['plan_id'] = executor.manifest_digest
    plan['review_digest'] = m.review_digest(plan)
    with pytest.raises(m.Refusal):
        executor.execute(plan, 'transient-only', lambda: None)
    f.fs.perform_filesystem_operations.assert_not_called()


def test_copied_entrypoint_resolves_fixed_iso_payload(tmp_path):
    import os
    import shutil
    import subprocess
    import sys
    copied = tmp_path / 'bin/wilsof-install'
    copied.parent.mkdir()
    shutil.copy2(ROOT / 'bin/wilsof-install', copied)
    stub = tmp_path / 'stub/installer'
    stub.mkdir(parents=True)
    (stub / '__init__.py').write_text('')
    (stub / 'wilsof_installer.py').write_text(
        'import sys\ndef main():\n'
        '    assert sys.path[0] == "/usr/share/wilsof/source", sys.path[0]\n'
        '    return 0\n')
    result = subprocess.run([sys.executable, str(copied)], capture_output=True, text=True,
                            env={**os.environ, 'PYTHONPATH': str(stub.parent)})
    assert result.returncode == 0, result.stderr


def test_read_only_validation_checks_schema_and_canonical_digest():
    m = runtime()
    plan = signed_plan()
    assert m.validate_plan(plan) == plan
    plan['target']['size_bytes'] += 1
    with pytest.raises(m.Refusal, match='digest'):
        m.validate_plan(plan)
    plan = signed_plan()
    plan['password'] = 'not-permitted'
    with pytest.raises(m.Refusal, match='schema'):
        m.validate_plan(plan)


@pytest.mark.parametrize('field,value', [
    ('bootloader', 'grub'),
    ('executor', {'adapter': 'archinstall', 'adapter_version': '4.4'}),
    ('account', {'username': 'root', 'password_in_plan': False}),
    ('account', {'username': 'a;touch /tmp/no', 'password_in_plan': False}),
    ('optional_packages', ['arbitrary-package']),
    ('codecs', {'selected': True}),
])
def test_valid_schema_does_not_imply_supported_runtime(field, value):
    m = runtime()
    plan = signed_plan()
    plan[field] = value
    plan['review_digest'] = m.review_digest(plan)
    with pytest.raises(m.Refusal):
        m.validate_plan(plan)


@pytest.mark.parametrize('failure', ['signature', 'dependency'])
def test_snapshot_failure_blocks_executor_before_formatting(fake_arch, monkeypatch, failure):
    import subprocess
    m, f = runtime(), fake_arch
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    monkeypatch.setattr(m, 'check_target_mount', lambda p: None)
    def reject(*args): raise subprocess.CalledProcessError(1, [failure])
    monkeypatch.setitem(m.snapshot, 'preflight', reject)
    with pytest.raises(subprocess.CalledProcessError): m.ArchinstallExecutor(f.manifest, f.hook, f.target)
    assert not f.events


def test_snapshot_drift_after_review_stops_before_disk_guard(fake_arch, monkeypatch):
    m, f = runtime(), fake_arch
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    monkeypatch.setattr(m, 'check_target_mount', lambda p: None)
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target)
    plan = signed_plan(); plan['plan_id'] = executor.manifest_digest; plan['review_digest'] = m.review_digest(plan)
    monkeypatch.setitem(m.snapshot, 'read', lambda *a: {'date': 'rolling'})
    with pytest.raises(m.Refusal, match='snapshot'):
        executor.execute(plan, 'transient', lambda: pytest.fail('No disk guard after policy rejection'))
    assert not f.events


def test_target_snapshot_is_persisted_and_verified_before_private_provisioning(fake_arch, monkeypatch):
    import runpy
    m, f = runtime(), fake_arch
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    monkeypatch.setattr(m, 'check_target_mount', lambda p: None)
    real = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
    def stage(target):
        f.events.append('snapshot-persist'); return real['stage'](target)
    def verify(target, receipt):
        assert real['read'](target)['date'] == '2026-11-01'
        f.events.append('snapshot-verified')
    monkeypatch.setitem(m.snapshot, 'stage', stage)
    monkeypatch.setitem(m.snapshot, 'verify_installed', verify)
    fallback = f.target / 'boot/EFI/BOOT/BOOTX64.EFI'; fallback.parent.mkdir(parents=True); fallback.write_bytes(b'EFI fixture')
    def provision(*args, **kwargs):
        assert 'snapshot-verified' in f.events
        assert real['read'](f.target)['date'] == '2026-11-01'
        f.events.append('provision')
    monkeypatch.setattr(m.subprocess, 'run', provision)
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target)
    plan = signed_plan(); plan['plan_id'] = executor.manifest_digest; plan['review_digest'] = m.review_digest(plan)
    executor.execute(plan, 'transient', lambda: None)
    assert f.events.index('snapshot-persist') < f.events.index('snapshot-verified') < f.events.index('provision')


def test_encrypted_executor_passes_luks_root_to_filesystem_and_installer(fake_arch, monkeypatch):
    from types import SimpleNamespace as NS
    m, f = runtime(), fake_arch
    f.api.DiskEncryption = lambda **kwargs: NS(**kwargs)
    f.api.EncryptionType = NS(LUKS='luks')
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    monkeypatch.setattr(m, 'check_target_mount', lambda path: None)
    monkeypatch.setattr(m.subprocess, 'run', lambda *args, **kwargs: None)
    fallback = f.target / 'boot/EFI/BOOT/BOOTX64.EFI'
    fallback.parent.mkdir(parents=True)
    fallback.write_bytes(b'fixture')
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target, encrypt=True)
    plan = signed_plan()
    plan['encryption']['enabled'] = True
    plan['plan_id'] = executor.manifest_digest
    plan['review_digest'] = m.review_digest(plan)
    phrase = 'synthetic-only-luks-passphrase'
    executor.execute(plan, 'synthetic-account-password', lambda: f.events.append('guard'),
                     encryption_password=phrase)
    config = f.api.FilesystemHandler.call_args.args[0]
    enc = config.disk_encryption
    assert enc.encryption_type == 'luks'
    assert enc.partitions == [config.device_modifications[0].partitions[1]]
    assert enc.encryption_password.plaintext == phrase
    assert enc.partitions[0].mountpoint == Path('/')
    assert config.device_modifications[0].partitions[0] not in enc.partitions
    assert f.api.Installer.call_args.args[1] is config
    assert 'cryptsetup' in executor.packages
    assert phrase not in json.dumps(plan)
    assert f.events.index('guard') < f.events.index('format')


def test_interactive_encrypted_review_keeps_distinct_secrets_out_of_plan():
    m = runtime()
    calls, output, prompts = [], [], []
    disk_secret = 'synthetic-only-disk-passphrase'
    class Executor:
        encrypt = True
        packages = ['base', 'cryptsetup']
        manifest_digest = 'sha256-encrypted-fixture'
        def execute(self, plan, password, guard, *, encryption_password):
            guard()
            calls.append(plan)
            assert plan['encryption'] == {'enabled': True}
            assert password == 'synthetic-account-password'
            assert encryption_password == disk_secret
            assert disk_secret not in json.dumps(plan)
    answers = iter(['/dev/vda', 'alice', 'ERASE /dev/vda'])
    secrets = iter(['synthetic-account-password'] * 2 + [disk_secret] * 2)
    def secret(prompt):
        prompts.append(prompt)
        return next(secrets)
    m.interactive(Executor(), probe=lambda path: signed_plan()['target'],
                  ask=lambda prompt: next(answers), secret=secret, output=output.append)
    assert len(calls) == 1
    assert len(prompts) == 4
    assert any('LUKS2' in line and 'unencrypted' in line and 'ESP' in line for line in output)
    assert disk_secret not in '\n'.join(output)
    assert 'synthetic-account-password' not in '\n'.join(output)


def test_encrypted_cli_is_explicit_and_read_only_help_remains_safe():
    import subprocess
    import sys
    result = subprocess.run([sys.executable, str(ROOT / 'bin/wilsof-install'), '--help'],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert '--encrypt' in result.stdout


@pytest.mark.parametrize('mode', ['blank', 'replace-existing'])
@pytest.mark.parametrize('explicit', [False, True])
def test_main_connects_encryption_flag_to_reviewed_executor(monkeypatch, mode, explicit):
    from types import SimpleNamespace as NS
    m = runtime()
    calls = []
    monkeypatch.setattr(m.sys.stdin, 'isatty', lambda: True)
    monkeypatch.setattr(m.sys.stdout, 'isatty', lambda: True)
    monkeypatch.setattr(m.os, 'geteuid', lambda: 0)
    monkeypatch.setattr(m, 'check_platform', lambda *a: None)
    monkeypatch.setattr(m, 'check_firmware', lambda *a: None)
    monkeypatch.setattr(m, 'check_live_capacity', lambda *a: None)
    monkeypatch.setattr(m.Path, 'is_mount', lambda p: True)
    monkeypatch.setattr(m, 'guest_policy', lambda: ([], False))
    monkeypatch.setattr(m, 'ArchinstallExecutor', lambda **kwargs: NS(**kwargs))
    monkeypatch.setattr(m, 'interactive', lambda ex, **kwargs: calls.append((ex, kwargs)))
    args = (['--encrypt'] if explicit else []) + (['--replace-existing'] if mode == 'replace-existing' else [])
    assert m.main(args) == 0
    assert calls[0][0].encrypt is True
    assert calls[0][1].get('mode', 'blank') == mode


def test_encrypted_executor_refuses_plaintext_backend_fallback(fake_arch, monkeypatch):
    import subprocess
    from types import SimpleNamespace as NS
    m, f = runtime(), fake_arch
    f.api.DiskEncryption = lambda **kwargs: NS(**kwargs)
    f.api.EncryptionType = NS(LUKS='luks')
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    monkeypatch.setattr(m, 'check_target_mount', lambda path: None)
    fallback = f.target / 'boot/EFI/BOOT/BOOTX64.EFI'
    fallback.parent.mkdir(parents=True)
    fallback.write_bytes(b'fixture')
    calls = []
    def command(argv, **kwargs):
        calls.append(argv)
        if argv[0] == 'cryptsetup':
            assert argv == ['cryptsetup', 'isLuks', '--type', 'luks2', '/dev/vda2']
            assert kwargs['check'] is True
            raise subprocess.CalledProcessError(1, argv)
    monkeypatch.setattr(m.subprocess, 'run', command)
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target, encrypt=True)
    plan = signed_plan()
    plan['encryption']['enabled'] = True
    plan['plan_id'] = executor.manifest_digest
    plan['review_digest'] = m.review_digest(plan)
    with pytest.raises(subprocess.CalledProcessError):
        executor.execute(plan, 'synthetic-account-password', lambda: None,
                         encryption_password='synthetic-disk-passphrase')
    f.api.Installer.assert_not_called()
    assert len(calls) == 1


@pytest.mark.parametrize('phrase', [None, '', 'short', 'line\nbreak-in-passphrase',
                                   'null\x00in-passphrase', 'unicode-æ-passphrase',
                                   ' ' * 20, 'synthetic-account-password'])
def test_invalid_encryption_secrets_stop_before_any_disk_operation(fake_arch, monkeypatch, phrase):
    from types import SimpleNamespace as NS
    m, f = runtime(), fake_arch
    f.api.DiskEncryption = lambda **kwargs: NS(**kwargs)
    f.api.EncryptionType = NS(LUKS='luks')
    monkeypatch.setattr(m, 'load_archinstall', lambda: f.api)
    monkeypatch.setattr(m, 'check_target_mount', lambda path: None)
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target, encrypt=True)
    plan = signed_plan()
    plan['encryption']['enabled'] = True
    plan['plan_id'] = executor.manifest_digest
    plan['review_digest'] = m.review_digest(plan)
    with pytest.raises(m.Refusal):
        executor.execute(plan, 'synthetic-account-password',
                         lambda: pytest.fail('Invalid secret reached disk guard'),
                         encryption_password=phrase)
    f.fs.perform_filesystem_operations.assert_not_called()


def test_read_only_encrypted_plan_validation_has_no_secret_or_backend(monkeypatch):
    m = runtime()
    plan = signed_plan()
    plan['encryption']['enabled'] = True
    plan['review_digest'] = m.review_digest(plan)
    monkeypatch.setattr(m, 'load_archinstall', lambda: pytest.fail('Read-only validation imported backend'))
    assert m.validate_plan(plan) == plan
    plan['encryption']['passphrase'] = 'must-not-be-serialized'
    plan['review_digest'] = m.review_digest(plan)
    with pytest.raises(m.Refusal, match='schema'):
        m.validate_plan(plan)


@pytest.mark.parametrize('defect', ['missing', 'mismatch', 'short', 'shared'])
def test_interactive_encryption_failure_never_calls_executor(defect):
    from types import SimpleNamespace as NS
    m = runtime()
    account = 'synthetic-account-password'
    phrase = {'missing': '', 'short': 'short', 'shared': account}.get(defect, 'synthetic-disk-passphrase')
    confirm = 'different-disk-passphrase' if defect == 'mismatch' else phrase
    secrets = iter([account, account, phrase, confirm])
    answers = iter(['/dev/vda', 'alice'])
    ex = NS(encrypt=True, manifest_digest='sha256-fixture', packages=['base'],
            execute=lambda *a, **kw: pytest.fail('Invalid encryption reached executor'))
    with pytest.raises(m.Refusal):
        m.interactive(ex, probe=lambda path: signed_plan()['target'],
                      ask=lambda prompt: next(answers), secret=lambda prompt: next(secrets),
                      output=lambda line: None)
