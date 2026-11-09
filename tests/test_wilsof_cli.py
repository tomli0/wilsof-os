"""The update layer delegates full package transactions and fails closed."""
import json
import os
from pathlib import Path
import runpy
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'bin/wilsof'


def load():
    assert CLI.is_file(), 'Missing working Wilsof command entrypoint'
    return runpy.run_path(str(CLI))


def test_version_distinguishes_image_source_from_user_configuration(tmp_path):
    m = load()
    source = tmp_path / 'usr/share/wilsof/source'; source.mkdir(parents=True)
    (source / 'SOURCE_COMMIT').write_text('a' * 40 + '\n')
    data = m['identity'](tmp_path)
    assert data['image_source_commit'] == 'a' * 40
    assert data['version'] == 'Development snapshot'
    assert data['atomic_rollback'] is False
    (source / 'SOURCE_COMMIT').write_text('not-a-commit\n')
    with pytest.raises(ValueError, match='identity'):
        m['identity'](tmp_path)


@pytest.fixture
def installed(tmp_path):
    m = load()
    (tmp_path / 'usr/share/wilsof/source').mkdir(parents=True)
    (tmp_path / 'usr/share/wilsof/source/SOURCE_COMMIT').write_text('a' * 40 + '\n')
    (tmp_path / 'usr/lib').mkdir(parents=True)
    (tmp_path / 'usr/lib/os-release').write_text('ID=arch\n')
    policy = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
    policy['stage'](tmp_path)
    # Model normal root-owned 0755 policy ancestors, not the host's group umask.
    for p in tmp_path.rglob('*'):
        if p.is_dir():
            p.chmod(0o755)
        else:
            p.chmod(0o644)
    return m, tmp_path, policy


def test_preflight_refuses_changed_repository_before_running_any_package_tool(installed):
    m, root, policy = installed
    (root / 'etc/pacman.conf').write_text('SigLevel = Never\n')
    calls = []
    with pytest.raises(ValueError, match='snapshot'):
        m['preflight'](root, policy=policy, run=lambda *a, **k: calls.append(a))
    assert calls == []


def test_package_update_uses_only_interactive_full_upgrade_and_reports_noop():
    m = load(); calls = []
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, 'base 1\n', '')
    assert m['package_update'](run=run) == 0
    assert [a for a, _ in calls] == [
        ['/usr/bin/pacman', '-Q'], ['/usr/bin/sudo', '--', '/usr/bin/pacman', '-Syu'],
        ['/usr/bin/pacman', '-Q']]
    assert calls[1][1].get('stdin') is None
    assert 'capture_output' not in calls[1][1]
    assert all('--noconfirm' not in a for a, _ in calls)


def test_package_failure_is_preserved_without_config_migration_or_retry():
    m = load(); calls = []
    def run(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 23 if '/usr/bin/sudo' in argv else 0, 'base 1\n', '')
    assert m['package_update'](run=run) == 23
    assert len(calls) == 2


def test_valid_offline_preflight_runs_only_local_database_check(installed):
    m, root, policy = installed
    calls = []
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, '', '')
    assert m['preflight'](root, policy=policy, run=run)['date'] == policy['DATE']
    assert [a for a, _ in calls] == [['/usr/bin/pacman', '-Dk']]
    assert calls[0][1]['stdin'] == subprocess.DEVNULL


@pytest.mark.parametrize('defect', ['lock','symlink','writable-policy','no-space','database-error','live'])
def test_preflight_refuses_unsafe_state_without_any_transaction(installed, defect):
    m, root, policy = installed
    from collections import namedtuple
    usage = namedtuple('usage', 'free')
    space = lambda path: usage(8 * 1024**3)
    if defect == 'lock':
        p = root / 'var/lib/pacman/db.lck'; p.parent.mkdir(parents=True); p.touch()
    elif defect == 'symlink':
        p = root / 'etc/pacman.conf'; data = p.read_bytes(); p.unlink()
        external = root / 'external'; external.write_bytes(data); p.symlink_to(external)
    elif defect == 'writable-policy':
        (root / 'etc/pacman.conf').chmod(0o666)
    elif defect == 'no-space':
        space = lambda path: usage(1024)
    elif defect == 'live':
        (root / 'run/archiso/airootfs').mkdir(parents=True)
    calls = []
    def run(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 1 if defect == 'database-error' else 0, '', '')
    with pytest.raises(ValueError):
        m['preflight'](root, policy=policy, run=run, space=space)
    assert calls == ([['/usr/bin/pacman', '-Dk']] if defect == 'database-error' else [])


def test_cli_refuses_unattended_update_and_does_not_expose_future_commands():
    import sys
    r = subprocess.run([sys.executable, str(CLI), 'update'], capture_output=True, text=True)
    assert r.returncode == 78
    assert 'interactive terminal' in r.stderr
    r = subprocess.run([sys.executable, str(CLI), 'rollback'], capture_output=True, text=True)
    assert r.returncode == 2


def test_untrusted_installed_policy_is_not_executed(installed):
    m, root, _ = installed
    helper = root / 'usr/share/wilsof/source/runtime/repository-snapshot.py'
    helper.parent.mkdir(mode=0o755)
    helper.write_text('raise RuntimeError("untrusted policy executed")\n')
    helper.chmod(0o666)
    with pytest.raises(ValueError, match='safely owned'):
        m['preflight'](root)
