"""Filesystem fault injection and real competing-process profile tests."""
import json
import os
from pathlib import Path
import runpy
import select
import stat
import subprocess
import sys

import pytest
from test_profile import CLI, PROFILES, invoke, seed, state_file


def load_cli():
    return runpy.run_path(str(CLI))


def test_set_refuses_corruption_until_user_archives_it(tmp_path):
    raw = b'{keep original evidence'
    path = seed(tmp_path, raw)
    result = invoke(tmp_path, 'set', 'study')
    assert result.returncode == 1 and result.stdout == ''
    assert 'refusing overwrite' in result.stderr
    assert path.read_bytes() == raw
    saved = path.with_name('profile.corrupt.saved')
    path.rename(saved)  # Explicit owner action, never automatic CLI repair.
    assert invoke(tmp_path, 'set', 'study').returncode == 0
    assert saved.read_bytes() == raw


@pytest.mark.parametrize('stage', ['write', 'file_sync', 'replace'])
def test_precommit_failures_preserve_previous_bytes_and_clean_temp(tmp_path, monkeypatch, stage):
    api = load_cli()
    assert invoke(tmp_path, 'set', 'study').returncode == 0
    path = state_file(tmp_path)
    before = path.read_bytes()
    def fail(*args, **kwargs):
        raise OSError('injected ' + stage)
    if stage == 'write':
        monkeypatch.setattr(api['json'], 'dump', fail)
    else:
        monkeypatch.setattr(api['os'], 'fsync' if stage == 'file_sync' else 'replace', fail)
    with api['state_directory'](tmp_path) as directory:
        with pytest.raises(OSError, match='injected'):
            api['write_profile'](directory, 'development')
    assert path.read_bytes() == before
    assert set(p.name for p in path.parent.iterdir()) == {'profile.json', '.profile.lock'}


def test_atomic_replace_sync_order_and_old_open_reader(tmp_path, monkeypatch):
    api = load_cli()
    assert invoke(tmp_path, 'set', 'study').returncode == 0
    path = state_file(tmp_path)
    events = []
    real_sync, real_replace = os.fsync, os.replace
    def sync(fd):
        events.append('dir_sync' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'file_sync')
        return real_sync(fd)
    def replace(src, dst, **kwargs):
        events.append('replace')
        assert kwargs['src_dir_fd'] == kwargs['dst_dir_fd']
        assert json.loads(path.read_text())['profile'] == 'study'
        return real_replace(src, dst, **kwargs)
    monkeypatch.setattr(api['os'], 'fsync', sync)
    monkeypatch.setattr(api['os'], 'replace', replace)
    with path.open('rb') as old_reader:
        with api['state_directory'](tmp_path) as directory:
            api['write_profile'](directory, 'development')
        assert json.load(old_reader)['profile'] == 'study'
    assert json.loads(path.read_text())['profile'] == 'development'
    assert events == ['file_sync', 'replace', 'dir_sync']


def test_directory_sync_failure_reports_committed_but_uncertain_state(tmp_path, monkeypatch, capsys):
    api = load_cli()
    assert invoke(tmp_path, 'set', 'study').returncode == 0
    real_sync = os.fsync
    def sync(fd):
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError('injected directory sync')
        return real_sync(fd)
    monkeypatch.setattr(api['os'], 'fsync', sync)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setattr(sys, 'argv', ['wilsof-profile', 'set', 'everyday'])
    assert api['main']() == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert 'durability unknown' in captured.err
    assert 'file preserved' not in captured.err
    assert 'CLEAN fallback' not in captured.err
    assert json.loads(state_file(tmp_path).read_text())['profile'] == 'everyday'


def paused_writer(home, profile):
    """Pause the real writer immediately before rename with the lock held."""
    script = '''import os, runpy, sys
api = runpy.run_path(sys.argv[1])
replace = os.replace
def pause(*args, **kwargs):
    print('ready', flush=True)
    sys.stdin.readline()
    return replace(*args, **kwargs)
os.replace = pause
sys.argv = [sys.argv[1], 'set', sys.argv[2]]
raise SystemExit(api['main']())
'''
    process = subprocess.Popen([sys.executable, '-B', '-c', script, str(CLI), profile],
                               env=os.environ | {'HOME': str(home)}, text=True,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdout is not None
    if not select.select([process.stdout], [], [], 5)[0]:
        process.kill()
        process.communicate(timeout=5)
        pytest.fail('writer did not reach rename')
    assert process.stdout.readline() == 'ready\n'
    return process


def test_sigkill_before_rename_keeps_old_state_and_does_not_reuse_orphan(tmp_path):
    assert invoke(tmp_path, 'set', 'study').returncode == 0
    path = state_file(tmp_path)
    before = path.read_bytes()
    process = paused_writer(tmp_path, 'development')
    try:
        assert path.read_bytes() == before
        process.kill()
        process.communicate(timeout=5)
        assert process.returncode < 0
        assert path.read_bytes() == before
        orphans = list(path.parent.glob('.profile-*.tmp'))
        assert len(orphans) == 1
        orphan_bytes = orphans[0].read_bytes()
        assert invoke(tmp_path, 'set', 'everyday').returncode == 0
        assert orphans[0].read_bytes() == orphan_bytes
        assert invoke(tmp_path, 'get').stdout == 'everyday\n'
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)


def test_concurrent_writers_are_serialized_and_last_commit_wins(tmp_path):
    assert invoke(tmp_path, 'set', 'clean').returncode == 0
    first = paused_writer(tmp_path, 'study')
    second = subprocess.Popen([sys.executable, '-B', str(CLI), 'set', 'development'],
                              env=os.environ | {'HOME': str(tmp_path)},
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        # First owns the lock; second cannot complete until it is released.
        assert second.stdout is not None
        assert not select.select([second.stdout], [], [], 0.1)[0]
        assert invoke(tmp_path, 'get').stdout == 'clean\n'
        out1, err1 = first.communicate('\n', timeout=5)
        out2, err2 = second.communicate(timeout=5)
        assert (first.returncode, out1, err1) == (0, 'study\n', '')
        assert (second.returncode, out2, err2) == (0, 'development\n', '')
        assert invoke(tmp_path, 'get').stdout == 'development\n'
    finally:
        for process in (first, second):
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)


def test_busy_lock_times_out_without_modifying_state(tmp_path):
    assert invoke(tmp_path, 'set', 'clean').returncode == 0
    first = paused_writer(tmp_path, 'study')
    try:
        result = invoke(tmp_path, 'set', 'development')
        assert result.returncode == 1 and result.stdout == ''
        assert 'busy' in result.stderr
        assert invoke(tmp_path, 'get').stdout == 'clean\n'
    finally:
        first.kill()
        first.communicate(timeout=5)


@pytest.mark.parametrize('name', ['profile.json', '.profile.lock'])
def test_rejects_leaf_symlink_without_touching_target(tmp_path, name):
    outside = tmp_path / 'outside'
    outside.write_bytes(b'private unrelated bytes')
    path = seed(tmp_path, b'{"schema_version":1,"profile":"study"}')
    target = path.parent / name
    if target.exists():
        target.unlink()
    target.symlink_to(outside)
    result = invoke(tmp_path, 'set', 'everyday')
    assert result.returncode == 1
    assert outside.read_bytes() == b'private unrelated bytes'
    assert target.is_symlink()


@pytest.mark.parametrize('relative', ['.local', '.local/state', '.local/state/wilsof-os'])
def test_rejects_directory_symlinks_without_external_writes(tmp_path, relative):
    home, outside = tmp_path / 'home', tmp_path / 'outside'
    home.mkdir()
    outside.mkdir()
    link = home / relative
    link.parent.mkdir(parents=True, exist_ok=True)
    for parent in (home / '.local', home / '.local/state'):
        if parent.is_dir():
            parent.chmod(0o700)
    link.symlink_to(outside, target_is_directory=True)
    for args in [('get',), ('set', 'study')]:
        assert invoke(home, *args).returncode == 1
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize('kind', ['mode', 'hardlink', 'fifo', 'directory'])
def test_unsafe_file_is_rejected_without_repair(tmp_path, kind):
    path = seed(tmp_path, b'{"schema_version":1,"profile":"study"}')
    if kind == 'mode':
        path.chmod(0o644)
    elif kind == 'hardlink':
        os.link(path, path.with_name('also-user-data'))
    else:
        path.unlink()
        os.mkfifo(path, 0o600) if kind == 'fifo' else path.mkdir()
    before = path.lstat()
    get = invoke(tmp_path, 'get')
    assert get.returncode == 1 and get.stdout == 'clean\n'
    assert invoke(tmp_path, 'set', 'clean').returncode == 1
    assert path.lstat().st_ino == before.st_ino
    assert path.lstat().st_mode == before.st_mode


def test_no_changes_outside_state_directory(tmp_path):
    home = tmp_path / 'home'
    home.mkdir()
    for relative in ('.config/dms/settings.json', '.config/hypr/hyprland.lua',
                     '.local/share/wilsof-os/dashboard/tasks.db', 'Documents/work.txt'):
        p = home / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'unrelated user work\x00')
    (home / '.local').chmod(0o700)
    before = {p.relative_to(home): (p.read_bytes(), p.stat().st_mode, p.stat().st_mtime_ns)
              for p in home.rglob('*') if p.is_file()}
    for profile in PROFILES:
        assert invoke(home, 'set', profile).returncode == 0
    assert invoke(home, 'list').returncode == 0
    for relative, unchanged in before.items():
        p = home / relative
        assert (p.read_bytes(), p.stat().st_mode, p.stat().st_mtime_ns) == unchanged
    added = {p.relative_to(home) for p in home.rglob('*') if p.is_file()} - set(before)
    assert added == {Path('.local/state/wilsof-os/profile.json'),
                     Path('.local/state/wilsof-os/.profile.lock')}
