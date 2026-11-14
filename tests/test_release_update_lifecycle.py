"""Source/fixture lifecycle coverage; no ISO build or native package transaction."""
import hashlib
import json
import runpy
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UPDATER = 'wilsof-release-update'


def materialize(tmp_path, source=ROOT):
    upstream = tmp_path / 'releng'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare'](
        upstream, output, source, 'a' * 40)
    return output


def controlled_updater_ancestors(root):
    folder = root / 'usr/local/bin'
    folder.mkdir(parents=True, exist_ok=True)
    for path in (folder, *folder.parents):
        path.chmod(0o755)
        if path == root:
            break


def assert_updater(root):
    installed = root / 'usr/local/bin' / UPDATER
    bundled = root / 'usr/share/wilsof/source/bin' / UPDATER
    expected = (ROOT / 'bin' / UPDATER).read_bytes()
    assert installed.is_file(), 'required administrative updater was silently omitted'
    assert not installed.is_symlink()
    assert installed.read_bytes() == bundled.read_bytes() == expected
    assert installed.stat().st_mode & 0o7777 == 0o755
    import os
    assert (installed.stat().st_uid, installed.stat().st_gid) == (os.getuid(), os.getgid())
    # Installation must not enroll trust, plan, update, or create updater state.
    assert not (root / 'var/lib/wilsof-release-update').exists()


def test_materialization_installs_exact_executable_updater(tmp_path):
    output = materialize(tmp_path)
    root = output / 'airootfs'
    assert_updater(root)
    result = subprocess.run([str(root / 'usr/local/bin' / UPDATER), '--help'],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert '--plan' in result.stdout and '--recover' in result.stdout
    payload = root / 'usr/share/wilsof/source'
    checksums = json.loads((payload / 'FILES.sha256.json').read_text())
    assert checksums['bin/' + UPDATER] == hashlib.sha256((ROOT / 'bin' / UPDATER).read_bytes()).hexdigest()
    assert (payload / 'SOURCE_COMMIT').read_text() == 'a' * 40 + '\n'


@pytest.mark.parametrize('defect', ['unlisted', 'missing', 'symlink', 'parent-symlink', 'writable'])
def test_materialization_refuses_unreviewed_or_unsafe_updater_before_output(tmp_path, defect):
    source = tmp_path / 'source'
    for folder in ('runtime', 'bin', 'config', 'assets', 'schemas', 'iso', 'installer', 'scripts'):
        shutil.copytree(ROOT / folder, source / folder)
    updater = source / 'bin' / UPDATER
    updater.chmod(0o755)
    manifest = source / 'runtime/image-files.txt'
    if defect == 'unlisted':
        manifest.write_text(manifest.read_text().replace('bin/' + UPDATER + '\n', ''))
    elif defect == 'missing':
        updater.unlink()
    elif defect == 'symlink':
        updater.unlink()
        updater.symlink_to(ROOT / 'bin' / UPDATER)
    elif defect == 'parent-symlink':
        (source / 'bin').rename(source / 'real-bin')
        (source / 'bin').symlink_to(source / 'real-bin', target_is_directory=True)
    else:
        updater.chmod(0o777)
    with pytest.raises(ValueError, match='[Ii]mage|[Ss]ource|[Uu]pdater'):
        materialize(tmp_path, source)
    assert not (tmp_path / 'profile').exists(), 'bad updater input must fail before materialization writes'


def test_archiso_declares_updater_root_ownership_and_mode():
    result = subprocess.run([
        'bash', '-c', 'declare -A file_permissions; source "$1"; '
        'printf "%s" "${file_permissions[/usr/local/bin/wilsof-release-update]}"',
        '-', str(ROOT / 'iso/profiledef.sh'),
    ], env={'PATH': '/usr/bin:/bin', 'SOURCE_DATE_EPOCH': '1767225600'},
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout == '0:0:755'


def test_installed_provisioning_copies_materialized_updater_without_running_it(tmp_path, monkeypatch):
    from test_chroot_contract import provision_transaction

    output = materialize(tmp_path)
    payload = output / 'airootfs/usr/share/wilsof/source'
    main, _, calls, _, target = provision_transaction(tmp_path, monkeypatch)
    monkeypatch.setitem(main.__globals__, 'Path', lambda value:
                        payload if str(value) == '/usr/share/wilsof/source' else Path(value))
    # Reprovisioning an owned regular entrypoint normalizes its mode; no user
    # configuration or explicit schema migration belongs to this root operation.
    installed = target / 'usr/local/bin' / UPDATER
    controlled_updater_ancestors(target)
    installed.write_text('previous owned updater\n')
    installed.chmod(0o700)
    personal = target / 'home/demo/.config/personal'
    personal.parent.mkdir()
    personal.write_text('preserve personal data\n')
    main()
    assert_updater(target)
    assert personal.read_text() == 'preserve personal data\n'
    assert not (target / 'home/demo/.local/state/wilsof-os/config-version.json').exists()
    assert all(argv[0] in ('systemctl', 'arch-chroot') for argv, _ in calls)
    assert not any(UPDATER in str(arg) for argv, _ in calls for arg in argv)


def test_live_provisioning_installs_updater_from_its_existing_source_bundle(tmp_path, monkeypatch):
    import os
    import sys
    from test_chroot_contract import provision_transaction

    output = materialize(tmp_path)
    root = output / 'airootfs'
    payload = root / 'usr/share/wilsof/source'
    main, _, _, installed_packages, _ = provision_transaction(tmp_path, monkeypatch)
    (root / 'usr/lib').mkdir(parents=True)
    (root / 'usr/lib/os-release').write_text('ID=arch\n')
    (root / 'etc/passwd').write_text('live:x:1000:1000::/home/live:/bin/bash\n')
    (root / 'home/live').mkdir(parents=True)
    # Redirect the running/live root to scratch. Only external commands are
    # substituted; the real source-equals-destination and entrypoint copies run.
    def mapped(value):
        return {'/': root, '/usr/share/wilsof/source': payload,
                '/usr/share/wilsof': root / 'usr/share/wilsof'}.get(str(value), Path(value))
    monkeypatch.setitem(main.__globals__, 'Path', mapped)
    monkeypatch.setattr(Path, 'is_mount', lambda path: str(path) == '/run/archiso/airootfs')
    monkeypatch.setattr(os, 'geteuid', lambda: 0)
    monkeypatch.setattr(sys, 'argv', ['provision-target', '/', 'live', '--live'])
    calls = []
    def run(argv, **options):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0)
    monkeypatch.setattr(subprocess, 'run', run)
    # Make omission observable even though the live materializer also ships it.
    controlled_updater_ancestors(root)
    (root / 'usr/local/bin' / UPDATER).unlink()
    main()
    assert_updater(root)
    assert installed_packages == []
    assert len(calls) == 1 and calls[0][-1] == '--live'
    assert not any(UPDATER in str(arg) for arg in calls[0])


@pytest.mark.parametrize('defect', ['missing', 'symlink', 'parent-symlink', 'writable'])
def test_provisioning_refuses_unsafe_updater_source_before_package_or_target_writes(tmp_path, monkeypatch, defect):
    from test_chroot_contract import provision_transaction

    main, _, calls, installed_packages, target = provision_transaction(tmp_path, monkeypatch)
    source = tmp_path / 'source'
    updater = source / 'bin' / UPDATER
    if defect == 'missing':
        updater.unlink()
    elif defect == 'symlink':
        updater.unlink()
        updater.symlink_to(ROOT / 'bin' / UPDATER)
    elif defect == 'parent-symlink':
        (source / 'bin').rename(source / 'real-bin')
        (source / 'bin').symlink_to(source / 'real-bin', target_is_directory=True)
    else:
        updater.chmod(0o777)
    config = (target / 'etc/pacman.conf').read_bytes()
    with pytest.raises(ValueError, match='[Uu]pdater|[Ss]ymlink'):
        main()
    assert calls == installed_packages == []
    assert not (target / 'usr/share/wilsof/source').exists()
    assert not (target / 'usr/local/bin').exists()
    assert (target / 'etc/pacman.conf').read_bytes() == config


@pytest.mark.parametrize('defect', ['symlink', 'dangling-symlink', 'parent-symlink', 'hardlink', 'directory'])
def test_provisioning_refuses_unsafe_updater_destination_without_following_it(tmp_path, monkeypatch, defect):
    from test_chroot_contract import provision_transaction

    main, _, calls, installed_packages, target = provision_transaction(tmp_path, monkeypatch)
    updater = target / 'usr/local/bin' / UPDATER
    controlled_updater_ancestors(target)
    outside = tmp_path / 'outside'
    outside.write_text('preserve unrelated bytes\n')
    outside.chmod(0o600)
    if defect == 'symlink':
        updater.symlink_to(outside)
    elif defect == 'dangling-symlink':
        updater.symlink_to(tmp_path / 'absent')
    elif defect == 'parent-symlink':
        updater.parent.rmdir()
        updater.parent.symlink_to(tmp_path, target_is_directory=True)
    elif defect == 'hardlink':
        updater.hardlink_to(outside)
    else:
        updater.mkdir()
    with pytest.raises(ValueError, match='[Uu]pdater|[Ss]ymlink'):
        main()
    assert calls == installed_packages == []
    assert not (target / 'usr/share/wilsof/source').exists()
    assert outside.read_text() == 'preserve unrelated bytes\n'
    assert outside.stat().st_mode & 0o7777 == 0o600
    assert not (tmp_path / 'absent').exists()
    assert not (tmp_path / UPDATER).exists()


def test_provisioning_creates_controlled_new_updater_directories(tmp_path, monkeypatch):
    import os
    from test_chroot_contract import provision_transaction

    main, _, _, _, target = provision_transaction(tmp_path, monkeypatch)
    previous = os.umask(0o002)
    try:
        main()
    finally:
        os.umask(previous)
    for relative in ('usr/local', 'usr/local/bin'):
        assert (target / relative).stat().st_mode & 0o022 == 0
    assert_updater(target)


@pytest.mark.parametrize('relative,defect', [
    ('usr/local/bin/' + UPDATER, 'owner'),
    ('usr/local/bin/' + UPDATER, 'group'),
    ('usr/local/bin/' + UPDATER, 'writable'),
    ('usr/local/bin', 'owner'),
    ('usr/local/bin', 'writable'),
    ('usr/local', 'owner'),
    ('usr/local', 'writable'),
    ('usr', 'owner'),
    ('', 'writable'),
])
def test_provisioning_refuses_uncontrolled_updater_inode_and_ancestors(tmp_path, monkeypatch, relative, defect):
    import os
    from test_chroot_contract import provision_transaction

    main, _, calls, installed_packages, target = provision_transaction(tmp_path, monkeypatch)
    updater = target / 'usr/local/bin' / UPDATER
    controlled_updater_ancestors(target)
    updater.write_text('preserve unsafe updater until administrative review\n')
    updater.chmod(0o755)
    victim = target / relative
    if defect == 'writable':
        victim.chmod(0o777)
    else:
        original = Path.lstat
        def lstat(path):
            info = original(path)
            if path == victim:
                values = list(info)
                values[4 if defect == 'owner' else 5] += 1
                return os.stat_result(values)
            return info
        monkeypatch.setattr(Path, 'lstat', lstat)
    before = updater.read_bytes()
    with pytest.raises(ValueError, match='[Uu]pdater'):
        main()
    assert calls == installed_packages == []
    assert updater.read_bytes() == before
    assert not (target / 'usr/share/wilsof/source').exists()
