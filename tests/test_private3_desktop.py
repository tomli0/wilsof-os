"""Private3 installed desktop contracts, exercised through the real provisioner."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pty
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def provision(home):
    entry=home/'.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True,exist_ok=True)
    entry.write_text('-- base\n')
    spec=importlib.util.spec_from_file_location('p3desktop',ROOT/'runtime/desktop.py')
    assert spec and spec.loader
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m.install_user(ROOT,home)


def test_default_bar_is_authentic_logo_and_numbered_workspaces_without_profiles(tmp_path):
    provision(tmp_path)
    data=json.loads((tmp_path/'.config/DankMaterialShell/settings.json').read_text())
    left=data['barConfigs'][0]['leftWidgets']
    assert left[0]=='wilsofCommandCenter'
    ws=left[1]
    assert ws['id']=='workspaceSwitcher' and ws['showWorkspaceIndex'] is True
    assert ws['showWorkspaceName'] is False and ws['showWorkspacePadding'] is True
    assert ws['showOccupiedWorkspacesOnly'] is False
    plugins=json.loads((tmp_path/'.config/dms/plugin_settings.json').read_text())
    assert plugins.get('wilsofProfiles',{}).get('enabled',False) is False
    assert not (tmp_path/'.config/dms/plugins/wilsofProfiles').exists()
    assert not (tmp_path/'.local/bin/wilsof-profile-ui').exists()
    assert (tmp_path/'.local/share/wilsof-os/assets/ws-monogram.png').is_file()


def test_existing_profile_bar_migrates_only_owned_entry_and_preserves_accounts_and_data(tmp_path):
    settings=tmp_path/'.config/DankMaterialShell/settings.json';settings.parent.mkdir(parents=True)
    settings.write_text(json.dumps({'barConfigs':[{'leftWidgets':['wilsofProfiles','clock'],'rightWidgets':['systemTray']}],'fontSize':19}))
    state=tmp_path/'.local/state/wilsof-os/profile.json';state.parent.mkdir(parents=True)
    state.write_bytes(b'personal historical profile state\n')
    provision(tmp_path)
    data=json.loads(settings.read_text())
    assert data['barConfigs'][0]['leftWidgets']==['wilsofCommandCenter','clock']
    assert data['fontSize']==19
    assert state.read_bytes()==b'personal historical profile state\n'


def test_owned_bar_migrates_implicit_workspace_defaults_but_keeps_explicit_preferences(tmp_path):
    settings=tmp_path/'.config/DankMaterialShell/settings.json';settings.parent.mkdir(parents=True)
    settings.write_text(json.dumps({'barConfigs':[{'leftWidgets':['wilsofProfiles','workspaceSwitcher']},{'leftWidgets':['wilsofCommandCenter',{'id':'workspaceSwitcher','showWorkspaceName':True}]}]}))
    provision(tmp_path)
    bars=json.loads(settings.read_text())['barConfigs']
    assert bars[0]['leftWidgets'][1]['showWorkspaceIndex'] is True
    assert bars[1]['leftWidgets'][1] == {'id':'workspaceSwitcher','showWorkspaceName':True}


def test_fastfetch_seed_preserves_personal_shell_configuration_and_noninteractive_silence(tmp_path):
    bashrc=tmp_path/'.bashrc';bashrc.write_text('# personal\nexport MY_PREF=kept\n')
    provision(tmp_path)
    first=bashrc.read_bytes();provision(tmp_path)
    assert bashrc.read_bytes()==first
    assert b'export MY_PREF=kept' in first
    assert first.count(b'WILSOF_MANAGED_TERMINAL_START')==1
    assert (tmp_path/'.local/share/applications/com.mitchellh.ghostty.desktop').read_text().splitlines().count('Name=Terminal')==1
    tools=tmp_path/'tools';tools.mkdir()
    fast=tools/'fastfetch';fast.write_text('#!/bin/sh\nprintf "REAL_FASTFETCH_EXECUTED\\n"\n');fast.chmod(0o755)
    env=os.environ|{'HOME':str(tmp_path),'PATH':str(tools)+':'+os.environ['PATH'],'TERM':'xterm-256color'}
    r=subprocess.run(['bash','--noprofile','--norc','-c','source "$HOME/.config/wilsof/terminal-start.sh"; printf automation-ok'],env=env,capture_output=True,text=True)
    assert r.returncode==0 and r.stdout=='automation-ok' and not r.stderr
    master,slave=pty.openpty()
    p=subprocess.Popen(['bash','--noprofile','--rcfile',str(bashrc),'-ic','exit'],env=env,stdin=slave,stdout=slave,stderr=slave,start_new_session=True)
    os.close(slave);output=b''
    while True:
        try: output+=os.read(master,4096)
        except OSError: break
    os.close(master);assert p.wait()==0
    assert output.count(b'REAL_FASTFETCH_EXECUTED')==1
    config=json.loads((tmp_path/'.local/share/wilsof-os/fastfetch.json').read_text())
    assert config['modules']==['title','separator','os','kernel','cpu','gpu','memory','disk','shell','uptime']


def test_locked_about_wording_and_original_logo_are_not_rewritten():
    qml=(ROOT/'config/dms/plugins/wilsofCommandCenter/About.qml').read_text()
    for text in ['Wilsof OS','Made with purpose. Built with curiosity.',
        'Wilsof OS was created from a simple idea: Linux should be powerful without being complicated. A clean, modern desktop that puts usability, freedom and simplicity first.',
        'Built on Arch Linux, Hyprland and Dux, combining established open-source technology with custom Wilsof design, configuration and development.',
        'Dedicated to William & Sofie',
        'The name Wilsof comes from my two children, William and Sofie. What began as a personal project carries their names as a reminder of curiosity, creativity and the joy of building something of your own.']:
        assert text in qml,text
    assert '[ W S ]' not in qml
    assert 'ws-monogram.png' in qml
    assert '/usr/share/licenses' in qml
    for name in ['About.qml','Shortcuts.qml']:
        text=(ROOT/'config/dms/plugins/wilsofCommandCenter'/name).read_text()
        assert 'Material.accent: "#86B9CE"' in text
        assert 'ScrollBar.AlwaysOn' in text


def test_required_lightweight_packages_are_in_target_closure_and_brand_tokens_match():
    packages={l.strip() for l in (ROOT/'runtime/desktop-packages.txt').read_text().splitlines() if l.strip() and not l.startswith('#')}
    assert {'firefox','nautilus','ghostty','gnome-text-editor','vlc','papers','loupe','file-roller','gnome-calculator','gnome-system-monitor','fastfetch','wpa_supplicant','iw','wireless-regdb','linux-firmware','wf-recorder','grim','slurp','wl-clipboard'}<=packages
    theme=json.loads((ROOT/'config/dms/wilsof-theme.json').read_text())
    assert theme['dark']['surface']==theme['dark']['background']=='#14181E'
    assert 'background = #14181E' in (ROOT/'config/ghostty/config').read_text()
    record=json.loads((ROOT/'assets/ws-monogram.provenance.json').read_text())
    for path,key in [(record['source'],'source_sha256'),(record['output'],'output_sha256')]:
        assert hashlib.sha256((ROOT/'assets'/path).read_bytes()).hexdigest()==record[key]
