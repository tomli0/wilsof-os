"""Live shortcut authority and refusal-before-write contracts."""
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'bin/wilsof-shortcuts'


def module():
    loader = importlib.machinery.SourceFileLoader('private3_shortcuts', str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


@pytest.fixture
def live(tmp_path):
    tools = tmp_path / 'bin'
    tools.mkdir()
    active = tmp_path / 'active.json'
    active.write_text(json.dumps([
        {'modmask':64,'key':'L','description':'Wilsof:lock','dispatcher':'HL.Dispatcher(exec_cmd)','arg':'3','submap':''},
        {'modmask':12,'key':'K','description':'Personal unrelated action','dispatcher':'HL.Dispatcher(exec_cmd)','arg':'8','submap':''}
    ]))
    ctl = tools / 'hyprctl'
    ctl.write_text('''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
p=Path(os.environ['HOME'])
if sys.argv[1:] == ['-j','binds']:
 print((p/'active.json').read_text())
elif sys.argv[1:] == ['reload']:
 if os.environ.get('FAIL_RELOAD'):sys.exit(1)
 data=json.loads((p/'active.json').read_text())
 state=p/'.local/state/wilsof-os/user-shortcuts.json'
 keys=json.loads(state.read_text())['overrides'].get('lock',{}).get('keys','SUPER + L')
 mods={'SUPER':64,'SHIFT':1,'CTRL':4,'ALT':8};tokens=keys.split(' + ')
 data[0]['modmask']=sum(mods[t] for t in tokens[:-1]);data[0]['key']=tokens[-1]
 (p/'active.json').write_text(json.dumps(data));print('ok')
else:sys.exit(2)
''')
    ctl.chmod(0o755)
    env=os.environ | {'HOME':str(tmp_path),'XDG_STATE_HOME':str(tmp_path/'.local/state'), 'HYPRLAND_INSTANCE_SIGNATURE':'fixture', 'PATH':str(tools)+':'+os.environ['PATH']}
    return tmp_path,env


def run(live,*args,extra=None):
    home,env=live
    return subprocess.run([str(CLI),*args],capture_output=True,text=True,env=env | (extra or {}))


def test_live_unrelated_conflict_refuses_without_writing(live):
    result=run(live,'set','lock','CTRL + ALT + K','--apply')
    assert result.returncode == 65, result.stderr
    assert 'Personal unrelated action' in result.stderr
    assert not (live[0]/'.local/state/wilsof-os/user-shortcuts.json').exists()


def test_apply_never_unbinds_an_unrelated_user_on_the_old_default_key(live):
    home=live[0]
    path=home/'active.json'
    bindings=json.loads(path.read_text());bindings[0]['description']='Personal replacement of default'
    path.write_text(json.dumps(bindings))
    result=run(live,'set','lock','CTRL + ALT + J','--apply')
    assert result.returncode==65,result.stderr
    assert not (home/'.local/state/wilsof-os/user-shortcuts.json').exists()
    assert json.loads(path.read_text())==bindings


def test_restore_can_vacate_other_owned_bindings_but_never_unrelated_ones():
    m=module()
    binding={'keys':'SUPER + space','description':'Wilsof:lock'}
    assert m.live_conflict([binding],'command-center','SUPER + space',vacating={'lock'}) is None
    assert m.live_conflict([binding],'command-center','SUPER + space')
    binding['description']='Personal action'
    assert m.live_conflict([binding],'command-center','SUPER + space',vacating={'lock'})


def test_list_reports_actual_runtime_binding_not_just_saved_configuration(live):
    data=json.loads(run(live,'list','--json').stdout)
    assert data['runtimeAvailable'] is True
    lock=next(a for a in data['actions'] if a['id']=='lock')
    assert lock['activeKeys'] == ['SUPER + L']
    assert any(b['description']=='Personal unrelated action' for b in data['bindings'])


def test_apply_verifies_reload_and_reset_preserves_unrelated_bindings(live):
    unrelated=json.loads((live[0]/'active.json').read_text())[1]
    result=run(live,'set','lock','CTRL + ALT + J','--apply')
    assert result.returncode == 0,result.stderr
    data=json.loads(run(live,'list','--json').stdout)
    assert next(a for a in data['actions'] if a['id']=='lock')['activeKeys'] == ['CTRL + ALT + J']
    assert run(live,'reset','lock','--apply').returncode == 0
    assert json.loads((live[0]/'active.json').read_text())[1] == unrelated


def test_failed_reload_rolls_back_exact_configuration_bytes(live):
    assert run(live,'set','lock','CTRL + ALT + J','--apply').returncode == 0
    home=live[0]
    paths=[home/'.local/state/wilsof-os/user-shortcuts.json',home/'.config/hypr/wilsof-user-shortcuts.lua']
    before=[p.read_bytes() for p in paths]
    result=run(live,'set','lock','CTRL + ALT + H','--apply',extra={'FAIL_RELOAD':'1'})
    assert result.returncode == 69
    assert [p.read_bytes() for p in paths] == before


@pytest.mark.parametrize('keys',['SUPER++K','CTRL + ALT + F3','A','SUPER + SHIFT','SUPER + K + J'])
def test_unsafe_or_malformed_capture_is_rejected(keys):
    with pytest.raises(ValueError):module().normalize_keys(keys)


def test_interactive_capture_uses_supported_inhibitor_and_releases_on_close():
    qml = (ROOT/'config/dms/plugins/wilsofCommandCenter/Shortcuts.qml').read_text()
    assert 'text: editor.filter' in qml, 'The editor query must remain synchronized across dialog recreation'
    for token in ['ShortcutInhibitor {', 'window: editor.contentWindow', 'enabled: editor.capturing', 'onDialogClosed:', 'Capture.combination(', '"--apply"', 'Restore all defaults', 'Restore default', 'activeKeys', 'runtimeAvailable', 'editor.capturing = false']:
        assert token in qml, token


def test_capture_maps_qt_events_without_saving_modifier_only_or_escape():
    capture = ROOT/'config/dms/plugins/wilsofCommandCenter/Capture.js'
    assert capture.exists(), 'Interactive capture model missing'
    script = "const fs=require('fs'),vm=require('vm'),m={};vm.createContext(m);vm.runInContext(fs.readFileSync(process.argv[1],'utf8').replace('.pragma library',''),m);console.log(JSON.stringify([m.combination(32,0x10000000),m.combination(75,0x0c000000),m.combination(16777216,0),m.combination(16777251,0x08000000)]));"
    r=subprocess.run(['node','-e',script,str(capture)],capture_output=True,text=True,check=True)
    assert json.loads(r.stdout) == ['SUPER + space','CTRL + ALT + K','cancel',None]
