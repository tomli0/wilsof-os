#!/usr/bin/env python3
"""Opt-in rootless-container lab; native Arch tools, no host device/home mounts."""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import stat
import subprocess
import sys
import tarfile
import uuid

CAPABILITIES = (1 << 21) | (1 << 18) | (1 << 7) | (1 << 6) | (1 << 0)


def verify_isolation(info):
    mapping = [list(map(int, row.split())) for row in info['uid_map'].splitlines()]
    if (not mapping or mapping[0][0] != 0 or mapping[0][1] == 0
            or info['cap_eff'] != CAPABILITIES or info['block_nodes']
            or not info['root_readonly'] or info['network_interfaces'] != ['lo']):
        raise ValueError('Native lab isolation requirements not met')


def checked(argv, **kwargs):
    return subprocess.run(argv, check=True, capture_output=True, text=True, timeout=60, **kwargs)


def block_nodes(root):
    return [str(p) for p in root.rglob('*') if stat.S_ISBLK(p.lstat().st_mode)]


def inside_info():
    status = Path('/proc/self/status').read_text()
    effective = re.search(r'^CapEff:\s*([0-9a-f]+)', status, re.M)
    if effective is None:
        raise ValueError('Native lab isolation capability state unavailable')
    return {'uid_map': Path('/proc/self/uid_map').read_text(),
            'cap_eff': int(effective[1], 16),
            'block_nodes': block_nodes(Path('/dev')),
            'root_readonly': bool(os.statvfs('/').f_flag & os.ST_RDONLY),
            'network_interfaces': sorted(p.name for p in Path('/sys/class/net').iterdir())}


def lab_mount(args):
    # This shim is NOT shipped in the ISO. Keep the upstream script unmodified,
    # but bind Docker's already isolated devices/sysfs rather than global devtmpfs.
    verify_isolation(inside_info())
    if not Path('/work/isolation-ok').is_file() or len(args) < 2:
        raise ValueError('Native lab isolation marker missing')
    target = Path(args[1])
    if not target.is_relative_to('/work/target') or '..' in target.parts:
        raise ValueError('Mount outside disposable lab root')
    if len(args) > 3 and args[2:4] == ['-t', 'devtmpfs']:
        return subprocess.run(['/bin/mount', '--bind', '/dev', str(target)], check=False).returncode
    if len(args) > 3 and args[2:4] == ['-t', 'sysfs']:
        if os.environ.get('WILSOF_LAB_FAIL_SYSFS') == '1':
            return 32
        checked(['/bin/mount', '--bind', '/sys', str(target)])
        try:
            checked(['/bin/mount', '-o', 'remount,bind,ro,nodev,nosuid,noexec', str(target)])
        except Exception:
            checked(['/bin/umount', str(target)])
            raise
        return 0
    return subprocess.run(['/bin/mount', *args], check=False).returncode


def inside():
    info = inside_info()
    verify_isolation(info)  # Before any arch-chroot transaction or mount.
    Path('/work/isolation-ok').write_text('isolated rootless namespace\n')
    manifest = json.loads(Path('/fixture/manifest.json').read_text())
    source = Path('/fixture/root')
    for name, digest in manifest['files'].items():
        path = source / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Fixture file hash changed: ' + name)
    for name, target in manifest['links'].items():
        if os.readlink(source / name) != target:
            raise ValueError('Fixture link changed: ' + name)
    root = Path('/work/target')
    shutil.copytree(source, root, symlinks=True)
    checked(['/bin/mount', '--bind', str(root), str(root)])
    bindir = Path('/work/bin')
    bindir.mkdir()
    (bindir / 'mount').write_text('#!/bin/sh\nexec python3 /lab/arch_chroot_lab.py --mount "$@"\n')
    (bindir / 'mount').chmod(0o755)
    (bindir / 'arch-chroot').symlink_to(source / 'usr/bin/arch-chroot')
    chroot = shutil.which('chroot')
    if not chroot:
        raise ValueError('Container chroot tool unavailable')
    for name in ('pacman', 'vercmp'):
        (bindir / name).write_text(f'#!/bin/sh\nexec {chroot} /work/target /usr/bin/{name} "$@"\n')
        (bindir / name).chmod(0o755)
    os.environ['PATH'] = str(bindir) + os.pathsep + os.environ['PATH']
    live_resolver = Path('/run/systemd/resolve/stub-resolv.conf')
    live_resolver.parent.mkdir(parents=True)
    live_resolver.write_text('nameserver 192.0.2.2\n')
    pin = runpy.run_path('/source/pinned-package.py')
    verify_resolver = runpy.run_path('/source/provision-target')['verify_resolver']
    version = pin['verify_arch_chroot_support']()
    assert version == manifest['arch_install_scripts_version']
    resolver = root / 'etc/resolv.conf'
    resolver_data = (root / 'run/systemd/resolve/stub-resolv.conf').read_bytes()

    def mounts():
        return {line.split()[4] for line in Path('/proc/self/mountinfo').read_text().splitlines()
                if line.split()[4] == str(root) or line.split()[4].startswith(str(root) + '/')}

    baseline = mounts()
    assert baseline == {str(root)}

    def clean():
        assert mounts() == baseline, sorted(mounts() - baseline)
        verify_resolver(root)
        assert (root / 'run/systemd/resolve/stub-resolv.conf').read_bytes() == resolver_data
        assert block_nodes(root / 'dev') == []

    # Observe real mount topology and resolver contents from inside the transaction.
    observation = checked(pin['target_command'](root, '/bin/bash', '-c',
        'while IFS= read -r line; do printf "%s\\n" "$line"; done < /proc/self/mountinfo; '
        'for dev in /dev/*; do if [[ -b "$dev" ]]; then exit 99; fi; done; '
        'IFS= read -r resolver < /etc/resolv.conf; [[ "$resolver" == "nameserver 192.0.2.2" ]]'))
    active = {line.split()[4] for line in observation.stdout.splitlines()}
    assert {'/proc', '/sys', '/dev', '/dev/pts', '/dev/shm', '/run', '/tmp'} <= active
    clean()
    # Synthetic unsigned LOCAL fixture follows Arch's normal LocalFileSigLevel,
    # not a disabled signature policy. No network, dependencies, hooks or scripts.
    config = (root / 'etc/pacman.conf').read_text()
    assert re.search(r'^LocalFileSigLevel\s*=\s*Optional\s*$', config, re.M)
    assert re.search(r'^CheckSpace\s*$', config, re.M)
    package_dir = Path('/work/packages')
    package_dir.mkdir()
    package = package_dir / pin['PACKAGE_NAME']
    executable = b'#!/bin/sh\nexit 0\n'
    metadata = b'pkgname = wilsof-contract-fixture\npkgver = 1-1\npkgdesc = Disposable chroot contract fixture\narch = x86_64\nsize = 17\nbuilddate = 1\n'
    with tarfile.open(package, 'w') as archive:
        for name, data, mode in [('.PKGINFO', metadata, 0o644), ('usr/bin/hypridle', executable, 0o755)]:
            entry = tarfile.TarInfo(name)
            entry.size, entry.mode, entry.mtime = len(data), mode, 1
            archive.addfile(entry, io.BytesIO(data))
    pin['verified_package'].__globals__['PACKAGE_SHA256'] = hashlib.sha256(package.read_bytes()).hexdigest()
    pin['install_package'].__globals__['BINARY_SHA256'] = hashlib.sha256(executable).hexdigest()
    pin['install_package'](root, package_dir)  # Real native Pacman and real upstream -r.
    clean()
    assert (root / 'usr/bin/hypridle').read_bytes() == executable
    assert list((root / 'var/lib/pacman/local').glob('wilsof-contract-fixture-1-1'))
    invalid = root / 'invalid-package'
    invalid.write_bytes(b'not an Arch package')
    failed = subprocess.run(pin['target_command'](root, 'pacman', '-U', '--noconfirm', '/invalid-package'),
                            capture_output=True, text=True, timeout=30)
    assert failed.returncode != 0
    clean()
    command_failure = subprocess.run(pin['target_command'](root, '/bin/bash', '-c', 'exit 23'),
                                    capture_output=True, text=True, timeout=30)
    assert command_failure.returncode == 23
    clean()
    os.environ['WILSOF_LAB_FAIL_SYSFS'] = '1'
    try:
        pin['install_package'](root, package_dir)
        raise AssertionError('Injected API setup failure was swallowed')
    except subprocess.CalledProcessError as error:
        setup_exit = error.returncode
        assert setup_exit != 0
    finally:
        os.environ.pop('WILSOF_LAB_FAIL_SYSFS')
    clean()
    assert (root / 'usr/bin/hypridle').read_bytes() == executable
    checked(['/bin/umount', str(root)])
    assert mounts() == set()
    return {'isolation': info, 'dependency_version': version, 'fixture_version': manifest['arch_install_scripts_version'],
            'upstream_arch_chroot_sha256': hashlib.sha256((source / 'usr/bin/arch-chroot').read_bytes()).hexdigest(),
            'tested_runtime_sha256': {name: hashlib.sha256((Path('/source') / name).read_bytes()).hexdigest()
                                     for name in ('pinned-package.py', 'provision-target')},
            'api_mounts': True, 'physical_block_devices_exposed': False,
            'pacman_install_exit': 0, 'pacman_failure_exit': failed.returncode,
            'command_failure_exit': command_failure.returncode, 'setup_failure_exit': setup_exit,
            'resolver_preserved': True, 'cleanup_after_success_and_failures': True,
            'lab_limit': 'devtmpfs replaced by isolated Docker /dev bind; sysfs by read-only container /sys bind'}


def run_lab(fixture, image):
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', image):
        raise ValueError('An exact existing local Docker image ID is required')
    security = json.loads(checked(['docker', 'info', '--format', '{{json .SecurityOptions}}']).stdout)
    if 'name=rootless' not in security:
        raise ValueError('Native lab isolation requires rootless Docker')
    fixture = fixture.resolve(strict=True)
    manifest = json.loads((fixture / 'manifest.json').read_text())
    if manifest.get('format') != 'wilsof-native-chroot-fixture-v1':
        raise ValueError('Unrecognized fixture')
    here = Path(__file__).resolve().parent
    source = here.parents[1] / 'runtime'
    mounts = [(fixture, '/fixture'), (here, '/lab'),
              (source / 'pinned-package.py', '/source/pinned-package.py'),
              (source / 'provision-target', '/source/provision-target')]
    name = 'wilsof-34-' + uuid.uuid4().hex
    args = ['docker', 'create', '--pull=never', '--name', name, '--network=none', '--read-only',
            '--cap-drop=ALL', '--cap-add=SYS_ADMIN', '--cap-add=SYS_CHROOT', '--cap-add=SETUID', '--cap-add=SETGID', '--cap-add=CHOWN',
            '--security-opt', 'seccomp=unconfined', '--security-opt', 'apparmor=unconfined',
            '--pids-limit', '128', '--memory', '384m', '--cpus', '1',
            '--tmpfs', '/work:rw,exec,nosuid,nodev,size=192m', '--tmpfs', '/run:rw,nosuid,nodev,size=4m']
    for host, guest in mounts:
        args += ['--mount', f'type=bind,src={host},dst={guest},readonly']
    args += [image, 'python3', '/lab/arch_chroot_lab.py', '--inside']
    container = checked(args).stdout.strip()
    if not re.fullmatch(r'[0-9a-f]{64}', container):
        raise ValueError('Invalid created-container identity')
    try:
        config = json.loads(checked(['docker', 'inspect', container]).stdout)[0]
        host = config['HostConfig']
        if host['Privileged'] or not host['ReadonlyRootfs'] or host['NetworkMode'] != 'none' or host.get('Devices') or host.get('PidMode'):
            raise ValueError('Native lab isolation Docker settings not met')
        process = subprocess.run(['docker', 'start', '--attach', container], capture_output=True, text=True, timeout=120)
        if process.returncode:
            raise RuntimeError('Native lab failed:\n' + process.stdout + '\n' + process.stderr)
        report = json.loads(process.stdout.splitlines()[-1])
        verify_isolation(report['isolation'])
    finally:
        status = json.loads(checked(['docker', 'inspect', container]).stdout)[0]['State']
        if status['Running']:
            checked(['docker', 'stop', '--time', '3', container])
        checked(['docker', 'rm', container])
    absent = subprocess.run(['docker', 'inspect', container], capture_output=True, text=True, timeout=10)
    if absent.returncode == 0:
        raise RuntimeError('Owned lab container still exists')
    report['container_removed'] = True
    report['container_image'] = image
    return report


if __name__ == '__main__':
    if sys.argv[1:] == ['--inside']:
        try:
            print(json.dumps(inside()))
        except subprocess.CalledProcessError as error:
            error.add_note('Native tool stderr: ' + str(error.stderr))
            raise
    elif sys.argv[1:2] == ['--mount']:
        raise SystemExit(lab_mount(sys.argv[2:]))
    else:
        raise SystemExit('Use the opt-in pytest entry point, not privileged host execution')
