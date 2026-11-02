"""Execute actual QML callback bodies. Not a compositor-security test."""
import json
from pathlib import Path
import subprocess
from test_auth_session import lock_env, events

ROOT = Path(__file__).resolve().parents[1]
QML = ROOT / 'config/dms/plugins/wilsofCommandCenter/CommandCenter.qml'


def test_direct_locker_does_not_roundtrip_synthetic_logind_lock(lock_env):
    env, _, log = lock_env
    p = subprocess.run([str(ROOT / 'bin/wilsof-lock')], env=env, capture_output=True, timeout=8)
    assert p.returncode == 0
    assert any(c[0] == 'hyprlock' for c in events(log))
    assert not any('lock-session' in c or 'unlock-session' in c for c in events(log))


def test_actual_callbacks_cleanup_without_boolean_authorization():
    script = r'''
const fs=require('fs'),vm=require('vm'); const src=fs.readFileSync(process.argv[1],'utf8');
function body(name){const m=new RegExp('function '+name+'\\([^)]*\\)(?:\\s*:\\s*string)?\\s*\\{').exec(src); if(!m)throw Error(name);let i=m.index+m[0].length,n=1,start=i;for(;n;i++){if(src[i]==='{')n++;else if(src[i]==='}')n--;}return src.slice(start,i-1);}
const state={SessionService:{locked:true},wantedOpen:false,query:'',category:'',fileGeneration:0,activeFileProcess:{running:true},rows:[],localRows:[],fileRows:[],pendingModal:'about',aboutLoader:{item:{close(){state.aboutClosed=true}}},shortcutsLoader:{item:{close(){state.shortcutsClosed=true}}},fileTimer:{stop(){state.timerStopped=true}},CompositorService:{getFocusedScreen(){return 1}},center:{open(){state.opened=true},close(){state.closed=true}},refresh(){state.refreshed=true}};
state.root=state; vm.createContext(state);
for(const name of ['lockdown','open']) vm.runInContext('function '+name+'(){'+body(name)+'}',state);
state.lockdown();
if(state.wantedOpen||!state.closed||!state.aboutClosed||!state.shortcutsClosed||state.pendingModal!==''||state.query!==''||state.activeFileProcess.running)throw Error('incomplete cosmetic cleanup');
state.open(); // cached true must not permanently deny legitimate native-release input
if(!state.opened||!state.wantedOpen)throw Error('cached boolean remains authority');
for(const name of ['toggle','search']){if(body(name).includes('SessionService.locked'))throw Error('IPC authorization');}
if(src.includes('onSessionUnlocked')||src.includes('forceunlock')||src.includes('above_lock'))throw Error('unlock/privileged path');
for(const name of ['about','shortcuts']){if(!src.includes('onLoaded: root.finishModal("'+name+'")'))throw Error('unguarded deferred modal');}
console.log(JSON.stringify({cleanup:true,staleTrueLiveness:true,ipcNoAuthority:true}));
'''
    p = subprocess.run(['node', '-e', script, str(QML)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert all(json.loads(p.stdout).values())
