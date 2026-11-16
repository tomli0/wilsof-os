"""Focused action boundary: no shell interpolation or fabricated availability."""
import importlib.machinery
import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]


def module():
    path=ROOT/'bin/wilsof-action'
    assert path.exists(), 'Focused action implementation missing'
    loader=importlib.machinery.SourceFileLoader('p3action',str(path))
    spec=importlib.util.spec_from_loader(loader.name,loader)
    assert spec and spec.loader
    m=importlib.util.module_from_spec(spec);loader.exec_module(m)
    return m


def test_capabilities_require_actual_dependencies():
    m=module()
    caps=m.capabilities(which=lambda name: None if name in ('grim','wf-recorder','pacman') else '/usr/bin/'+name)
    assert caps['screenshot'] is False and caps['recording'] is False
    assert caps['install'] is False and caps['remove'] is False and caps['update'] is False
    assert caps['emoji'] is True
    assert caps['window-visuals'] is False


def test_update_capability_uses_the_actual_sibling_without_local_bin_in_path(monkeypatch):
    m = module()
    calls = []
    def system_path_only(name):
        calls.append(name)
        return None if name == 'wilsof' else '/usr/bin/' + name
    assert m.capabilities(which=system_path_only)['update'] is True
    assert 'wilsof' not in calls
    sibling = Path(m.software_command('update')[0])
    assert sibling == ROOT / 'bin/wilsof'
    monkeypatch.setattr(m.os, 'access', lambda path, mode: False if Path(path) == sibling else True)
    assert m.capabilities(which=system_path_only)['update'] is False


@pytest.mark.parametrize('name',['--overwrite','firefox;reboot','../../etc/passwd','a b','$(id)',''])
def test_package_names_cannot_be_options_or_shell_payloads(name):
    with pytest.raises(ValueError): module().software_command('install',name)


def test_software_transactions_keep_signature_policy_and_user_confirmation():
    m=module()
    assert m.software_command('install','firefox')==['sudo','pacman','-Syu','--','firefox']
    assert m.software_command('remove','vlc')==['sudo','pacman','-Rns','--','vlc']
    assert m.software_command('update')==[str(ROOT/'bin/wilsof'),'update']
    with pytest.raises(ValueError):m.software_command('remove','hyprland')
    with pytest.raises(ValueError):m.software_command('not-an-action','firefox')


def test_recording_stop_refuses_an_unrelated_transient_unit():
    m=module()
    assert m.owned_recorder({'Description':'Wilsof Screen Recording','ExecStart':'{ path=/usr/bin/wf-recorder ; argv[]=/usr/bin/wf-recorder -g 0,0 100x100 -f /home/test/new.mp4 ; }'})
    assert not m.owned_recorder({'Description':'Unrelated','ExecStart':'/usr/bin/wf-recorder'})
    assert not m.owned_recorder({'Description':'Wilsof Screen Recording','ExecStart':'{ path=/usr/bin/other ; }'})


def test_emoji_picker_filters_shared_menu_rows():
    import subprocess,json
    model=ROOT/'config/dms/plugins/wilsofCommandCenter/Model.js'
    script="const fs=require('fs'),vm=require('vm'),m={};vm.createContext(m);vm.runInContext(fs.readFileSync(process.argv[1],'utf8').replace('.pragma library',''),m);console.log(JSON.stringify(m.emojis('heart')));"
    r=subprocess.run(['node','-e',script,str(model)],text=True,capture_output=True,check=True)
    rows=json.loads(r.stdout)
    assert rows and all(row['kind']=='copy' and 'heart' in row['name'].lower() for row in rows)
