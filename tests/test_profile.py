"""Headless contract tests for the standalone, stdlib-only profile CLI."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'bin/wilsof-profile'
PROFILES = ('clean', 'study', 'development', 'everyday')


def invoke(home, *args):
    assert CLI.is_file(), 'wilsof-profile CLI is missing'
    env = os.environ | {'HOME': str(home), 'PYTHONDONTWRITEBYTECODE': '1'}
    for key in ('DISPLAY', 'WAYLAND_DISPLAY', 'DBUS_SESSION_BUS_ADDRESS',
                'HYPRLAND_INSTANCE_SIGNATURE'):
        env.pop(key, None)
    return subprocess.run([sys.executable, '-B', str(CLI), *args], env=env,
                          capture_output=True, text=True, timeout=10)


def state_file(home):
    return home / '.local/state/wilsof-os/profile.json'


def seed(home, raw):
    path = state_file(home)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # A valid-state fixture must not inherit the host's group-writable umask.
    (home / '.local').chmod(0o700)
    (home / '.local/state').chmod(0o700)
    path.write_bytes(raw)
    path.chmod(0o600)
    return path


def test_missing_state_is_clean_without_any_writes(tmp_path):
    result = invoke(tmp_path, 'get')
    assert (result.returncode, result.stdout, result.stderr) == (0, 'clean\n', '')
    assert list(tmp_path.iterdir()) == []


def test_list_is_stable_and_does_not_access_state(tmp_path):
    seed(tmp_path, b'broken')
    result = invoke(tmp_path, 'list')
    assert (result.returncode, result.stdout, result.stderr) == (
        0, '\n'.join(PROFILES) + '\n', '')


@pytest.mark.parametrize('profile', PROFILES)
def test_valid_state_selects_each_profile_without_rewriting(tmp_path, profile):
    raw = json.dumps({'schema_version': 1, 'profile': profile}).encode()
    path = seed(tmp_path, raw)
    result = invoke(tmp_path, 'get')
    assert (result.returncode, result.stdout, result.stderr) == (0, profile + '\n', '')
    assert path.read_bytes() == raw


@pytest.mark.parametrize('profile', PROFILES)
def test_set_persists_versioned_private_state(tmp_path, profile):
    result = invoke(tmp_path, 'set', profile)
    assert (result.returncode, result.stdout, result.stderr) == (0, profile + '\n', '')
    path = state_file(tmp_path)
    assert json.loads(path.read_text()) == {'schema_version': 1, 'profile': profile}
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700
    assert (path.parent / '.profile.lock').stat().st_mode & 0o777 == 0o600
    assert invoke(tmp_path, 'get').stdout == profile + '\n'


@pytest.mark.parametrize('raw', [
    b'{broken', b'', b'\xff', b'null', b'[]', b'{}',
    b'{"schema_version":2,"profile":"study"}',
    b'{"schema_version":true,"profile":"study"}',
    b'{"schema_version":1.0,"profile":"study"}',
    b'{"schema_version":1}', b'{"profile":"study"}',
    b'{"schema_version":1,"profile":null}',
    b'{"schema_version":1,"profile":[]}',
    b'{"schema_version":1,"profile":"STUDY"}',
    b'{"schema_version":1,"profile":"other"}',
    b'{"schema_version":1,"profile":"study","extra":1}',
    b'{"schema_version":1,"profile":"study","profile":"clean"}',
    b'{"schema_version":NaN,"profile":"study"}', b' ' * 4097,
])
def test_invalid_state_is_clean_with_error_and_preserved_bytes(tmp_path, raw):
    path = seed(tmp_path, raw)
    result = invoke(tmp_path, 'get')
    assert result.returncode == 1
    assert result.stdout == 'clean\n'
    assert 'CLEAN fallback' in result.stderr
    assert 'profile.json' in result.stderr
    assert path.read_bytes() == raw


@pytest.mark.parametrize('args', [(), ('other',), ('get', 'study'),
                                  ('list', 'clean'), ('set',),
                                  ('set', 'invalid'), ('set', 'CLEAN'),
                                  ('set', '../clean'), ('set', 'study', 'extra')])
def test_strict_arguments_do_not_create_state(tmp_path, args):
    result = invoke(tmp_path, *args)
    assert result.returncode == 2
    assert result.stdout == ''
    assert result.stderr
    assert list(tmp_path.iterdir()) == []
