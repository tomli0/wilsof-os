"""M2 boundary: saved intent is not a GUI acknowledgement."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / 'bin/wilsof-profile-ui'


@pytest.fixture
def desktop(tmp_path):
    home = tmp_path / 'home'
    home.mkdir()
    tools = tmp_path / 'tools'
    tools.mkdir()
    control = tmp_path / 'control.json'
    control.write_text(json.dumps({'clients': [{'class': 'editor', 'address': '0xabc',
                                               'workspace': {'id': 1}, 'pid': 900}],
                                   'layers': {'screen1': {'levels': {'0': []}}}}))
    fake = tools / 'hyprctl'
    fake.write_text('#!' + sys.executable + '\n' + '''import json, os, sys, time
from pathlib import Path
control = Path(os.environ['CONTROL'])
data = json.loads(control.read_text())
with Path(os.environ['CALLS']).open('a') as f: f.write(json.dumps(sys.argv[1:]) + '\\n')
if data.get('sleep'): time.sleep(data['sleep'])
if data.get('fail'): sys.exit(1)
if data.get('raw') is not None: print(data['raw']); sys.exit(0)
print(json.dumps(data[sys.argv[-1]]))
''')
    fake.chmod(0o755)
    env = os.environ | {'HOME': str(home), 'PATH': str(tools) + os.pathsep + os.environ['PATH'],
                        'WAYLAND_DISPLAY': 'wayland-test', 'HYPRLAND_INSTANCE_SIGNATURE': 'fixture',
                        'CONTROL': str(control), 'CALLS': str(tmp_path / 'calls'),
                        'PYTHONDONTWRITEBYTECODE': '1'}
    return home, env, control


def invoke(desktop, *args, env=None):
    assert UI.is_file(), 'M2 GUI boundary helper is missing'
    done = subprocess.run([sys.executable, '-B', str(UI), *args], env=env or desktop[1],
                          text=True, capture_output=True, timeout=9)
    return done, json.loads(done.stdout) if done.stdout else None


def test_missing_state_reports_clean_only_after_gui_verification_without_writes(desktop):
    done, state = invoke(desktop, 'status')
    assert done.returncode == 0, done.stderr
    assert state == {'schema_version': 1, 'saved': 'clean', 'applied': 'clean', 'error': None}
    assert not (desktop[0] / '.local').exists()
    calls = [json.loads(x) for x in Path(desktop[1]['CALLS']).read_text().splitlines()]
    assert calls == [['-j', 'clients'], ['-j', 'layers']]


@pytest.mark.parametrize('profile', ('clean', 'study', 'development', 'everyday'))
def test_apply_only_saves_profile_and_queries_never_dispatches(desktop, profile):
    before = desktop[2].read_bytes()
    done, result = invoke(desktop, 'apply', profile)
    assert done.returncode == 0, done.stderr
    assert result['saved'] == result['applied'] == profile
    assert result['error'] is None
    path = desktop[0] / '.local/state/wilsof-os/profile.json'
    assert json.loads(path.read_text()) == {'schema_version': 1, 'profile': profile}
    assert path.stat().st_mode & 0o777 == 0o600
    assert before == desktop[2].read_bytes()
    calls = [json.loads(x) for x in Path(desktop[1]['CALLS']).read_text().splitlines()]
    assert calls == [['-j', q] for q in ('clients', 'layers', 'clients', 'layers')]


def test_saved_profile_without_graphical_session_is_not_applied(desktop):
    subprocess.run([sys.executable, str(ROOT / 'bin/wilsof-profile'), 'set', 'study'],
                   env=desktop[1], check=True, capture_output=True)
    env = desktop[1].copy()
    env.pop('HYPRLAND_INSTANCE_SIGNATURE')
    done, result = invoke(desktop, 'status', env=env)
    assert done.returncode == 1
    assert result['saved'] == 'study' and result['applied'] is None
    assert 'not GUI-confirmed' in result['error']


@pytest.mark.parametrize('surface', ('client', 'initialClass', 'layer-second-monitor'))
def test_dashboard_surfaces_refused_without_modification(desktop, surface):
    data = json.loads(desktop[2].read_text())
    if surface == 'client':
        data['clients'].append({'class': 'org.wilsof.Tasks'})
    elif surface == 'initialClass':
        data['clients'].append({'class': 'custom', 'initialClass': 'org.wilsof.Tasks'})
    else:
        data['layers']['screen2'] = {'levels': {'2': [{'namespace': 'org.wilsof.Tasks'}]}}
    desktop[2].write_text(json.dumps(data))
    for action in (('status',), ('apply', 'clean')):
        done, result = invoke(desktop, *action)
        assert done.returncode == 1
        assert result['applied'] is None
        assert 'Dashboard surface detected' in result['error']
    assert not (desktop[0] / '.local/state/wilsof-os/profile.json').exists()


@pytest.mark.parametrize('override', ({'fail': True}, {'raw': 'Target not found.'},
                                     {'sleep': 5}, {'clients': {}}, {'layers': []},
                                     {'clients': [{}]}, {'layers': {'s': {'levels': {'0': [{}]}}}}))
def test_ipc_errors_never_acknowledged(desktop, override):
    data = json.loads(desktop[2].read_text())
    data.update(override)
    desktop[2].write_text(json.dumps(data))
    done, result = invoke(desktop, 'apply', 'study')
    assert done.returncode == 1 and result['error']
    assert result['applied'] is None
    assert not (desktop[0] / '.local/state/wilsof-os/profile.json').exists()


def test_corruption_is_clean_fallback_with_visible_error_not_silent_repair(desktop):
    subprocess.run([sys.executable, str(ROOT / 'bin/wilsof-profile'), 'set', 'study'],
                   env=desktop[1], check=True, capture_output=True)
    path = desktop[0] / '.local/state/wilsof-os/profile.json'
    path.write_text('{broken')
    for args in (('status',), ('apply', 'everyday')):
        done, result = invoke(desktop, *args)
        assert done.returncode == 1
        assert result['saved'] == 'clean' and result['applied'] is None
        assert 'CLEAN fallback' in result['error']
        assert path.read_text() == '{broken'


@pytest.mark.parametrize('args', ((), ('other',), ('apply',), ('apply', 'STUDY'),
                                  ('apply', 'study;touch nope'), ('status', 'study')))
def test_invalid_actions_cannot_execute(desktop, args):
    done, result = invoke(desktop, *args)
    assert done.returncode == 2 and result is None
    assert not (desktop[0] / '.local/state/wilsof-os/profile.json').exists()


def test_post_rename_failure_reports_actual_saved_profile_without_success(desktop, monkeypatch, capsys):
    import runpy
    module = runpy.run_path(str(UI))
    monkeypatch.setenv('HOME', str(desktop[0]))
    monkeypatch.setattr(sys, 'argv', [str(UI), 'apply', 'study'])
    monkeypatch.setitem(module['main'].__globals__, 'verify_gui', lambda: None)
    original = module['state']['write_profile']

    def sync_failure(directory, profile):
        original(directory, profile)
        raise OSError('profile replaced, directory sync failed; durability unknown')

    monkeypatch.setitem(module['state'], 'write_profile', sync_failure)
    assert module['main']() == 1
    result = json.loads(capsys.readouterr().out)
    assert result['saved'] == 'study' and result['applied'] is None
    assert 'durability unknown' in result['error']
