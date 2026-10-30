"""Exercise the real session wrapper with disposable executables, no compositor."""
import os
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_session_routes_normal_output_to_journal_and_preserves_diagnostics(tmp_path):
    wrapper = ROOT / 'bin/wilsof-session'
    assert wrapper.is_file(), 'Missing start-hyprland session entrypoint'
    log = tmp_path / 'argv'
    for name in ('start-hyprland', 'systemd-cat'):
        f = tmp_path / name
        f.write_text('#!/bin/sh\nprintf "%s\\n" "' + name + '" "$@" > "$PROBE_LOG"\nexit 17\n')
        f.chmod(0o755)
    env = os.environ | {'PATH': str(tmp_path), 'PROBE_LOG': str(log)}
    r = subprocess.run(['/bin/sh', str(wrapper)], env=env, capture_output=True)
    assert r.returncode == 17
    assert log.read_text().splitlines() == ['systemd-cat', '--identifier=wilsof-session', 'start-hyprland']
    r = subprocess.run(['/bin/sh', str(wrapper), '--diagnostics'], env=env, capture_output=True)
    assert r.returncode == 17
    assert log.read_text().splitlines() == ['start-hyprland']
    r = subprocess.run(['/bin/sh', str(wrapper), '--unknown'], env=env, capture_output=True)
    assert r.returncode == 2


def test_live_and_installed_greetd_use_same_reviewed_session(tmp_path):
    m = runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))
    upstream = tmp_path / 'upstream'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    out = tmp_path / 'profile'
    m['prepare'](upstream, out, ROOT, 'a' * 40)
    root = out / 'airootfs'
    config = (root / 'etc/greetd/config.toml').read_text()
    assert 'tuigreet --cmd /usr/local/bin/wilsof-session' in config
    assert 'command = "/usr/local/bin/wilsof-session"' in config
    assert (root / 'usr/local/bin/wilsof-session').read_bytes() == (ROOT / 'bin/wilsof-session').read_bytes()
    assert 'tuigreet --time --cmd /usr/local/bin/wilsof-session' in (ROOT / 'runtime/provision-target').read_text()
    assert '["/usr/local/bin/wilsof-session"]="0:0:755"' in (ROOT / 'iso/profiledef.sh').read_text()
