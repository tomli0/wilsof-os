"""Isolated authentication lifecycle regressions; no real session actions."""
import importlib.util
import os
from pathlib import Path
import re
import shutil
import json
import signal
import socket
import subprocess
import sys
import time
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_fresh_manifest_payload_provisions_all_idle_commands(tmp_path):
    payload = tmp_path / 'payload'
    for relative in (ROOT / 'runtime/image-files.txt').read_text().splitlines():
        dest = payload / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, dest)
    spec = importlib.util.spec_from_file_location('fresh_desktop', payload / 'runtime/desktop.py')
    assert spec is not None and spec.loader is not None
    desktop = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(desktop)
    home = tmp_path / 'installed-home'
    (home / '.config/hypr').mkdir(parents=True)
    (home / '.config/hypr/hyprland.lua').write_text('-- generated fixture base\n')
    desktop.install_user(payload, home)
    config = (home / '.config/hypr/hypridle.conf').read_text()
    commands = re.findall(r'=\s*\$HOME/\.local/bin/([\w-]+)', config)
    assert commands
    for name in commands:
        assert os.access(home / '.local/bin' / name, os.X_OK), name
        assert (payload / 'bin' / name).is_file(), name
    assert re.search(r'timeout = 180\s+on-timeout = \$HOME/\.local/bin/wilsof-idle', config)
    assert re.search(r'timeout = 300\s+on-timeout = \$HOME/\.local/bin/wilsof-lock', config)
    assert (home / '.config/hypr/hyprlock-idle.conf').is_file()
    assert (home / '.config/hypr/hyprlock.conf').is_file()
    assert (home / '.config/systemd/user/graphical-session.target.wants/hypridle.service').is_symlink()


@pytest.fixture
def lock_env(tmp_path):
    runtime = tmp_path / 'run'
    runtime.mkdir(mode=0o700)
    display = socket.socket(socket.AF_UNIX)
    fd = os.open(runtime, os.O_RDONLY | os.O_DIRECTORY)
    try:
        display.bind(f'/proc/self/fd/{fd}/wayland-1')
    finally:
        os.close(fd)
    (tmp_path / '.config/hypr').mkdir(parents=True)
    (tmp_path / '.config/hypr/hyprlock-idle.conf').write_text('# fixture idle config\n')
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    log = tmp_path / 'events'
    config = tmp_path / 'fixture.json'
    config.write_text(json.dumps({'exit': 0, 'pid': os.getpid(), 'session': '42', 'user': os.getuid(), 'type': 'wayland'}))
    fake = r"""#!/usr/bin/env python3
import json, os, pathlib, signal, sys, time
name = pathlib.Path(sys.argv[0]).name
cfg = json.loads(pathlib.Path(os.environ['FIXTURE']).read_text())
with open(os.environ['EVENTS'], 'a') as out:
    out.write(json.dumps([name, *sys.argv[1:]]) + '\n')
if name == 'pgrep': sys.exit(1)
if name == 'hyprctl':
    print(json.dumps([{'instance': 'instance-one', 'wl_socket': 'wayland-1', 'pid': cfg['pid']}]))
elif name == 'busctl':
    if cfg.get('dbus_fail'): sys.exit(1)
    if 'GetSessionByPID' in sys.argv: print('o "/org/freedesktop/login1/session/c42"')
    elif 'get-property' in sys.argv: print('s "' + cfg['session'] + '"')
elif name == 'loginctl' and 'show-session' in sys.argv:
    print('Id=' + cfg['session'] + '\nUser=' + str(cfg['user']) + '\nType=' + cfg['type'] + '\nClass=user\nState=active')
elif name == 'hyprlock':
    if cfg.get('hold'):
        pathlib.Path(os.environ['STARTED']).write_text(str(os.getpid()))
        while not pathlib.Path(os.environ['RELEASE']).exists(): time.sleep(.01)
    if cfg.get('signal'): os.kill(os.getpid(), cfg['signal'])
    sys.exit(cfg['exit'])
"""
    for name in ('hyprlock', 'pgrep', 'loginctl', 'hyprctl', 'busctl'):
        p = bindir / name
        p.write_text(fake)
        p.chmod(0o755)
    env = {'PATH': str(bindir) + ':' + os.environ['PATH'], 'HOME': str(tmp_path),
                        'XDG_RUNTIME_DIR': str(runtime), 'XDG_SESSION_ID': '42',
                        'HYPRLAND_INSTANCE_SIGNATURE': 'instance-one', 'WAYLAND_DISPLAY': 'wayland-1',
                        'FIXTURE': str(config), 'EVENTS': str(log),
                        'STARTED': str(tmp_path / 'started'), 'RELEASE': str(tmp_path / 'release')}
    yield env, config, log
    display.close()


def events(log):
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


def configure(config, **values):
    data = json.loads(config.read_text())
    config.write_text(json.dumps(data | values))


@pytest.mark.parametrize('wrapper', ['wilsof-lock', 'wilsof-idle'])
@pytest.mark.parametrize('code,signum', [(0, 0), (23, 0), (0, signal.SIGTERM), (0, signal.SIGKILL)])
def test_process_exit_never_claims_authenticated_unlock(lock_env, wrapper, code, signum):
    env, config, log = lock_env
    configure(config, exit=code, signal=signum)
    result = subprocess.run([str(ROOT / 'bin' / wrapper)], env=env, capture_output=True, text=True, timeout=8)
    assert result.returncode == (128 + signum if signum else code)
    assert any(call[0] == 'hyprlock' for call in events(log))
    assert not any('unlock-session' in call or ('SetLockedHint' in call and call[-1] == 'false') for call in events(log))


@pytest.mark.parametrize('action', ['secured', 'released'])
def test_uncoordinated_event_hooks_are_not_enabled(lock_env, action):
    env, _, log = lock_env
    p = subprocess.run([str(ROOT / 'bin/wilsof-lock-session'), action], env=env, capture_output=True, timeout=8)
    assert p.returncode == 64
    assert events(log) == []
    conf = (ROOT / 'config/hypr/hypridle.conf').read_text()
    assert 'on_unlock_cmd' not in conf
    assert 'on_lock_cmd' not in conf


@pytest.mark.parametrize('mutation', ['missing_session', 'other_user', 'not_wayland', 'stale_session', 'dbus_failure', 'unsafe_runtime'])
def test_unverifiable_identity_or_bus_fails_before_locker(lock_env, mutation):
    env, config, log = lock_env
    if mutation == 'missing_session':
        env.pop('XDG_SESSION_ID')  # resolved from compositor PID instead, not required
        configure(config, dbus_fail=True)
    elif mutation == 'other_user': configure(config, user=os.getuid() + 1)
    elif mutation == 'not_wayland': configure(config, type='tty')
    elif mutation == 'stale_session': env['XDG_SESSION_ID'] = '99'
    elif mutation == 'dbus_failure': configure(config, dbus_fail=True)
    elif mutation == 'unsafe_runtime': Path(env['XDG_RUNTIME_DIR']).chmod(0o777)
    p = subprocess.run([str(ROOT / 'bin/wilsof-lock')], env=env, capture_output=True, text=True, timeout=8)
    assert p.returncode != 0
    assert not any(call[0] == 'hyprlock' for call in events(log))



def wait_until(predicate):
    deadline = time.monotonic() + 5
    while not predicate():
        assert time.monotonic() < deadline, 'fixture synchronization timed out'
        time.sleep(.01)


def test_concurrent_wrappers_share_one_session_lifecycle(lock_env):
    env, config, log = lock_env
    configure(config, hold=True)
    owner = subprocess.Popen([str(ROOT / 'bin/wilsof-lock')], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    second = None
    try:
        wait_until(lambda: Path(env['STARTED']).exists())
        second = subprocess.Popen([str(ROOT / 'bin/wilsof-idle')], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wait_until(lambda: second.poll() is not None or len([c for c in events(log) if c[0] == 'hyprlock']) > 1)
    finally:
        Path(env['RELEASE']).touch()
        owner.communicate(timeout=8)
        if second: second.communicate(timeout=8)
    assert second is not None
    assert second.returncode == 75, 'duplicate must report busy, not claim a secured lock'
    assert len([c for c in events(log) if c[0] == 'hyprlock']) == 1
    assert len([c for c in events(log) if 'lock-session' in c]) == 1


@pytest.mark.parametrize('death', [signal.SIGTERM, signal.SIGKILL])
def test_supervisor_death_keeps_guard_in_locker_and_stale_file_can_be_reused(lock_env, death):
    env, config, log = lock_env
    configure(config, hold=True)
    owner = subprocess.Popen([str(ROOT / 'bin/wilsof-lock')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_until(lambda: Path(env['STARTED']).exists())
        owner.send_signal(death)
        owner.wait(timeout=8)
        duplicate = subprocess.Popen([str(ROOT / 'bin/wilsof-lock')], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wait_until(lambda: duplicate.poll() is not None or len([c for c in events(log) if c[0] == 'hyprlock']) > 1)
    finally:
        Path(env['RELEASE']).touch()
    duplicate.communicate(timeout=8)
    assert duplicate.returncode == 75
    configure(config, hold=False)
    # The old child eventually closes its inherited descriptor. Never unlink the inode.
    deadline = time.monotonic() + 5
    while True:
        retry = subprocess.run([str(ROOT / 'bin/wilsof-lock')], env=env, capture_output=True, timeout=8)
        if retry.returncode != 75: break
        assert time.monotonic() < deadline
        time.sleep(.01)
    assert retry.returncode == 0
    assert not any('unlock-session' in c for c in events(log))


def test_different_session_does_not_share_guard(lock_env):
    env, config, log = lock_env
    configure(config, hold=True)
    owner = subprocess.Popen([str(ROOT / 'bin/wilsof-lock')], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        wait_until(lambda: Path(env['STARTED']).exists())
        other = config.with_name('other.json')
        other.write_text(json.dumps(json.loads(config.read_text()) | {'session': '43', 'hold': False}))
        p = subprocess.run([str(ROOT / 'bin/wilsof-lock')], env=env | {'FIXTURE': str(other), 'XDG_SESSION_ID': '43'}, capture_output=True, timeout=8)
        assert p.returncode == 0
        assert len([c for c in events(log) if c[0] == 'hyprlock']) == 2
    finally:
        Path(env['RELEASE']).touch()
        owner.communicate(timeout=8)


def test_absent_environment_session_is_resolved_from_compositor_pid(lock_env):
    env, _, log = lock_env
    env.pop('XDG_SESSION_ID')
    p = subprocess.run([str(ROOT / 'bin/wilsof-lock')], env=env, capture_output=True, timeout=8)
    assert p.returncode == 0
    assert ['loginctl', 'lock-session', '42'] in events(log)


@pytest.mark.parametrize('bad', ['symlink', 'hardlink', 'mode'])
def test_unsafe_guard_is_rejected_without_touching_target(lock_env, bad):
    import hashlib
    env, _, log = lock_env
    key = hashlib.sha256(('42' + ':' + 'instance-one').encode()).hexdigest()
    guard = Path(env['XDG_RUNTIME_DIR']) / ('wilsof-lock-' + key + '.lock')
    victim = Path(env['HOME']) / 'untouched'
    victim.write_text('fixture data')
    if bad == 'symlink': guard.symlink_to(victim)
    elif bad == 'hardlink': os.link(victim, guard)
    else: guard.write_text(''); guard.chmod(0o666)
    p = subprocess.run([str(ROOT / 'bin/wilsof-lock')], env=env, capture_output=True, timeout=8)
    assert p.returncode != 0
    assert victim.read_text() == 'fixture data'
    assert not any(c[0] == 'hyprlock' for c in events(log))


@pytest.mark.parametrize('code', [0, 23])
def test_repeated_completed_or_failed_invocation_never_clears_state(lock_env, code):
    env, config, log = lock_env
    configure(config, exit=code)
    for _ in range(2):
        p = subprocess.run([str(ROOT / 'bin/wilsof-lock')], env=env, capture_output=True, timeout=8)
        assert p.returncode == code
    assert len([c for c in events(log) if c[0] == 'hyprlock']) == 2
    assert not any('unlock-session' in c for c in events(log))
