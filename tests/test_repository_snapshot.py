"""Repository-policy behavior only: synthetic trees, never host package operations."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    helper = ROOT / 'runtime/repository-snapshot.py'
    assert helper.is_file(), 'Missing shared build/live/target snapshot contract'
    return runpy.run_path(str(helper))


def test_preparer_uses_identical_dated_build_and_live_policy(tmp_path):
    upstream = tmp_path / 'releng'
    shutil.copytree(ROOT / 'tests/fixtures/archiso92', upstream)
    output = tmp_path / 'profile'
    runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare'](upstream, output, ROOT, 'a' * 40)
    live = output / 'airootfs'
    config = (live / 'etc/pacman.conf').read_text()
    assert config == (output / 'pacman.conf').read_text()
    assert 'https://archive.archlinux.org/repos/2026/11/01/$repo/os/$arch' in config
    assert 'Include' not in config and 'file://' not in config
    assert '[core]' in config and '[extra]' in config and '[multilib]' not in config
    assert 'SigLevel = Required TrustedOnly DatabaseOptional' in config
    record = api()['read'](live)
    assert record['date'] == '2026-11-01'
    assert record['repositories'] == ['core', 'extra']
    assert record['pacman_conf_sha256'] == hashlib.sha256(config.encode()).hexdigest()
    assert 'repository-snapshot.py' in (live / 'usr/share/wilsof/source/runtime/image-files.txt').read_text()

@pytest.mark.parametrize('change', ['missing-record', 'corrupt-record', 'rolling', 'mixed-date', 'weak-signatures', 'mirror-drift', 'symlink'])
def test_required_snapshot_cannot_disappear_or_escape_to_other_repositories(tmp_path, change):
    m = api(); root = tmp_path / 'root'; m['stage'](root)
    conf = root / 'etc/pacman.conf'; manifest = root / m['MANIFEST']
    if change == 'missing-record': manifest.unlink()
    elif change == 'corrupt-record': manifest.write_text('{}')
    elif change == 'rolling': conf.write_text(conf.read_text().replace('archive.archlinux.org/repos/2026/11/01', 'geo.mirror.pkgbuild.com'))
    elif change == 'mixed-date': conf.write_text(conf.read_text().replace('2026/11/01', '2026/11/02', 1))
    elif change == 'weak-signatures': conf.write_text(conf.read_text().replace('Required TrustedOnly', 'Never TrustAll'))
    elif change == 'mirror-drift': (root / 'etc/pacman.d/mirrorlist').write_text('Server = https://example.invalid')
    else:
        original = root / 'original'; conf.rename(original); conf.symlink_to(original)
    with pytest.raises(ValueError): m['read'](root)


@pytest.mark.parametrize('relative', ['etc', 'etc/pacman.conf', 'usr/share/wilsof/REPOSITORY-SNAPSHOT.json'])
def test_staging_rejects_symlinks_before_any_write(tmp_path, relative):
    m = api(); root = tmp_path / 'root'; external = tmp_path / 'external'
    external.mkdir(); sentinel = external / 'sentinel'; sentinel.write_bytes(b'preserve')
    link = root / relative; link.parent.mkdir(parents=True)
    link.symlink_to(external)
    with pytest.raises(ValueError): m['stage'](root)
    assert sentinel.read_bytes() == b'preserve'
    assert not (root / 'etc/pacman.d/mirrorlist').exists()


def test_running_host_cannot_be_materialized(monkeypatch):
    with pytest.raises(ValueError, match='running system'): api()['stage'](Path('/'))


def test_target_preflight_verifies_complete_constraints_without_host_state_changes(tmp_path, monkeypatch):
    m = api(); live = tmp_path / 'live'; m['stage'](live)
    keyring = tmp_path / 'keys'; keyring.mkdir()
    for name in ('pubring.gpg', 'trustdb.gpg'): (keyring / name).write_bytes(name.encode())
    calls = []
    def command(argv):
        calls.append(argv)
        assert argv[:3] == ['pacman-conf', '--config', str(live / 'etc/pacman.conf')]
        return str(keyring) + '\n'
    monkeypatch.setitem(m['preflight'].__globals__, 'command', command)
    def verify(config, targets, cache, db, keys, private):
        assert config == live / 'etc/pacman.conf'
        assert targets == ['base', 'aquamarine', 'libaquamarine.so=14-64']
        assert (keys / 'pubring.gpg').read_bytes() == b'pubring.gpg'
        assert str(tmp_path) in str(cache) and db != Path('/var/lib/pacman')
        assert private['name'] == 'hyprland-as02-private'
        return [{'name': 'base', 'version': '1-1'}]
    original = runpy.run_path
    monkeypatch.setattr(runpy, 'run_path', lambda path, *a, **k: {'verify_transaction': verify} if str(path).endswith('package-preflight.py') else original(path, *a, **k))
    result = m['preflight'](live, ['base', 'aquamarine'], {'name': 'hyprland-as02-private', 'dependency_constraints': ['libaquamarine.so=14-64']}, directory=tmp_path)
    assert result['snapshot'] == m['read'](live)
    assert result['packages'] == [{'name': 'base', 'version': '1-1'}]
    assert len(calls) == 1


def test_target_preflight_policy_drift_aborts_before_package_tool(tmp_path, monkeypatch):
    m = api(); live = tmp_path / 'live'; m['stage'](live)
    (live / 'etc/pacman.conf').write_text('rolling')
    monkeypatch.setitem(m['preflight'].__globals__, 'command', lambda argv: pytest.fail('No package tool on rejected policy'))
    with pytest.raises(ValueError): m['preflight'](live, ['base'], None, directory=tmp_path)


@pytest.mark.parametrize('wrong_version', [False, True])
def test_installed_target_must_match_preformat_repository_transaction(tmp_path, monkeypatch, wrong_version):
    m = api(); target = tmp_path / 'target'; m['stage'](target)
    receipt = {'snapshot': m['read'](target), 'packages': [{'name': 'base', 'version': '1-1'}]}
    calls = []
    def command(argv):
        calls.append(argv)
        assert argv == ['arch-chroot', '-r', str(target), 'pacman', '-Q', '--', 'base']
        return 'base ' + ('2-1' if wrong_version else '1-1') + '\n'
    monkeypatch.setitem(m['verify_installed'].__globals__, 'command', command)
    if wrong_version:
        with pytest.raises(ValueError, match='transaction'): m['verify_installed'](target, receipt)
        assert not (target / 'usr/share/wilsof/REPOSITORY-INPUTS.json').exists()
    else:
        m['verify_installed'](target, receipt)
        assert json.loads((target / 'usr/share/wilsof/REPOSITORY-INPUTS.json').read_text()) == receipt
    assert len(calls) == 1
