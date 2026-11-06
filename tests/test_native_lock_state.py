"""Real admission-state model, not a mock of SessionService's stale boolean."""
import json
from pathlib import Path
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / 'config/dms/plugins/wilsofCommandCenter/NativeLock.js'


@pytest.mark.parametrize('scenario', ['initial', 'cycle', 'wrong-password', 'relock-race', 'repeated', 'restart-locked', 'restart-pending', 'restart-pending-quiescent', 'disconnect', 'invalid', 'stale-epoch'])
def test_native_lock_admission(scenario):
    assert JS.is_file(), 'Missing compositor-authoritative admission model'
    script = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const m={};vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),m);
const epoch='a'.repeat(32), other='b'.repeat(32), A='c'.repeat(32),B='d'.repeat(32);
let s=m.fresh();
const event=(kind,seq,extra={})=>s=m.receive(s,Object.assign({kind,seq,epoch},extra),epoch);
const initial=(locked=false,busy=false)=>event('snapshot',0,{locked,guardBusy:busy,key:'e'.repeat(64)});
const begin=(token,seq)=>{s=m.prepare(s,token);event('barrier',seq,{token,locked:s.locked});};
assert(!m.allowed(s));
switch(process.argv[2]) {
case 'initial': initial();assert(m.allowed(s));break;
case 'cycle': initial();begin(A,0);assert(!m.allowed(s)&&s.ready);event('locked',1);assert(!m.allowed(s));event('unlocked',2);assert(m.allowed(s));break;
case 'wrong-password': initial();begin(A,0);event('locked',1);for(let i=0;i<8;i++){event('pulse',1);assert(!m.allowed(s));}break;
case 'relock-race': initial();begin(A,0);event('locked',1);s=m.prepare(s,B);event('unlocked',2);assert(!m.allowed(s),'queued A unlock must not release B');event('barrier',2,{token:B,locked:false});assert(s.ready&&!m.allowed(s));event('locked',3);event('unlocked',4);assert(m.allowed(s));break;
case 'repeated': initial();for(let i=0;i<20;i++){begin(i%2?A:B,2*i);event('locked',2*i+1);assert(!m.allowed(s));event('unlocked',2*i+2);assert(m.allowed(s));}break;
case 'restart-locked': initial(true,true);assert(!m.allowed(s));event('unlocked',1);assert(m.allowed(s));break;
case 'restart-pending': initial(false,true);assert(!m.allowed(s));event('pulse',0);assert(!m.allowed(s));event('locked',1);event('unlocked',2);assert(m.allowed(s));break;
case 'restart-pending-quiescent': initial(false,true);assert(!m.allowed(s));event('quiescent',0);assert(m.allowed(s));begin(A,0);event('quiescent',0);assert(!m.allowed(s),'a quiescent receipt cannot clear a newer token');break;
case 'disconnect': initial();s=m.fresh();assert(!m.allowed(s));break;
case 'invalid': initial();event('unlocked',1);assert(!m.allowed(s),'unpaired unlock rejected');initial();assert(!m.allowed(s),'duplicate bootstrap is not recovery');break;
case 'stale-epoch': initial();begin(A,0);event('locked',1);s=m.receive(s,{kind:'unlocked',seq:2,epoch:other},epoch);assert(!m.allowed(s));event('unlocked',2);assert(m.allowed(s));break;
}
'''
    result = subprocess.run(['node', '-e', script, str(JS), scenario],capture_output=True,text=True,timeout=10)
    assert result.returncode == 0, result.stderr
