"""Offline QGA/runuser/env/systemd/Bash argument preservation contracts."""
import json
import os
from pathlib import Path
import runpy
import shlex
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(ROOT / 'tests/integration/session_command.py'))


@pytest.mark.parametrize('command', [
    'printf literal-ok', '$HOME/.local/bin/wilsof-shortcuts list --json',
    '/usr/bin/printf absolute-ok', 'printf "%s" "$HOME"',
    'printf "%s" "quotes \' and spaces; $(printf nested)"',
])
def test_outer_qga_bash_preserves_each_boundary(tmp_path, command):
    tools = tmp_path / 'tools'
    tools.mkdir()
    # Substitute only privilege and user-manager boundaries. Execute the real
    # outer Bash, env and final Bash; record actual argv rather than shlex alone.
    for name, code in {
        'runuser': "assert sys.argv[1:4] == ['-u','fixture','--']; os.execvp(sys.argv[4],sys.argv[4:])",
        'systemd-run': "print(json.dumps({'argv':sys.argv[1:], 'runtime':os.environ['XDG_RUNTIME_DIR'], 'bus':os.environ['DBUS_SESSION_BUS_ADDRESS']}))",
    }.items():
        script = tools / name
        script.write_text('#!/usr/bin/env python3\nimport sys,os,json\n' + code + '\n')
        script.chmod(0o755)
    payload = API['user_command'](command, username='fixture', uid=1234)
    # Use non-login outer Bash to prevent host profile PATH changes in fixture.
    r = subprocess.run(['/bin/bash', '-c', payload], capture_output=True, text=True,
                       env=os.environ | {'PATH': str(tools) + ':' + os.environ['PATH']}, timeout=5)
    assert r.returncode == 0, r.stderr
    row = json.loads(r.stdout)
    assert row['argv'][-4:] == ['--', '/bin/bash', '-lc', command]
    assert row['runtime'] == '/run/user/1234'
    assert row['bus'] == 'unix:path=/run/user/1234/bus'
    assert '--expand-environment=no' in row['argv']


@pytest.mark.skipif(os.environ.get('WILSOF_NATIVE_SYSTEMD_ARGV') != '1',
                    reason='explicit opt-in: finite transient user services, no VM')
def test_real_systemd_does_not_drop_home_prefixed_bash_command(tmp_path):
    command = '$HOME/../' + Path.home().name + '/does-not-exist-wilsof-argv-probe'
    payload = API['user_command'](command, username='unused', uid=os.getuid())
    argv = shlex.split(payload)
    argv = argv[argv.index('systemd-run'):]
    argv.insert(1, '--property=RuntimeMaxSec=5')
    r = subprocess.run(argv, capture_output=True, text=True, timeout=15)
    # Missing target is intentional. Bash must receive the command and attempt
    # it (127), not lose the entire argument before Bash starts (2).
    assert r.returncode == 127, (r.returncode, r.stdout, r.stderr)
    assert 'option requires an argument' not in r.stderr
    assert 'does-not-exist-wilsof-argv-probe' in r.stderr
