#!/usr/bin/env python3
"""Read-only source contracts + actual upstream JS callback, NOT native acceptance.
Usage: python probe.py --sources-root /directory/containing/as02-upstream-*
No compositor, locker, D-Bus, DMS service or production entrypoint is executed.
"""
import argparse, hashlib, json, re, shutil, subprocess, unittest
from pathlib import Path

P=argparse.ArgumentParser(); P.add_argument('--sources-root', required=True)
ARGS=P.parse_args(); ROOT=Path(ARGS.sources_root)

def read(repo,path): return (ROOT/('as02-upstream-'+repo)/path).read_text()
def function(text, signature):
    start=text.index(signature); brace=text.index('{',start); depth=1; end=brace+1
    while depth:
        depth += (text[end]=='{') - (text[end]=='}'); end+=1
    return text[start:end]

QML=read('dms','quickshell/Services/SessionService.qml')
CALLBACK=function(QML,'function updateLoginctlState(state)')
FOCUS=read('hyprland','src/desktop/state/FocusState.cpp')
MANAGER=read('hyprland','src/managers/SessionLockManager.cpp')
PROTO=read('hyprland','src/protocols/SessionLock.cpp')
INPUT=read('hyprland','src/managers/input/InputManager.cpp')
SEAT=read('hyprland','src/managers/SeatManager.cpp')
XML=read('protocols','staging/ext-session-lock/ext-session-lock-v1.xml')
TRACES={}

def callback_trace(name,states):
    node=shutil.which('node')
    if not node: raise unittest.SkipTest('existing Node required; do not install for this fixture')
    js="const vm=require('node:vm'); const c={locked:false, preparingForSleep:false, counts:{locked:0,unlocked:0,resumed:0,changed:0}}; c.sessionLocked=()=>c.counts.locked++; c.sessionUnlocked=()=>c.counts.unlocked++; c.emitSessionResumedOnce=()=>c.counts.resumed++; c.loginctlStateChanged=()=>c.counts.changed++; vm.createContext(c); vm.runInContext("+json.dumps(CALLBACK)+",c); const trace=[]; for(const s of "+json.dumps(states)+"){c.updateLoginctlState(s); trace.push({locked:c.locked, sessionId:c.sessionId});} console.log(JSON.stringify({trace, counts:c.counts}));"
    p=subprocess.run([node,'-e',js],capture_output=True,text=True,check=True,timeout=8)
    result=json.loads(p.stdout); TRACES[name]=result; return result

class BoundaryContracts(unittest.TestCase):
    def test_01_old_unlock_during_new_lock(self):
        r=callback_trace('old_unlock_after_new_lock',[{'locked':True},{'locked':False},{'locked':True},{'locked':False}])
        self.assertFalse(r['trace'][-1]['locked'])
        self.assertIn('isSessionLocked() && pSurface && !g_pSessionLockManager->isSurfaceSessionLock(pSurface)',FOCUS)
        # Callback deliberately demonstrates UI false; no native compositor state is simulated.
    def test_02_dms_restart_defaults(self):
        self.assertIn('property bool locked: false',QML)
        self.assertFalse(callback_trace('fresh_ui',[{}])['trace'][0]['locked'])
        self.assertIn('PROTO::sessionLock->isLocked()',MANAGER)
    def test_03_existing_modal_at_lock(self):
        self.assertIn('rawSurfaceFocus(nullptr)',MANAGER)
        self.assertIn('g_pSeatManager->setGrab(nullptr)',MANAGER)
    def test_04_grab_during_transition_is_unresolved(self):
        focus_grab=read('hyprland','src/protocols/FocusGrab.cpp')
        self.assertIn('g_pSeatManager->setGrab(m_grab)',focus_grab)
        self.assertIn('rawSurfaceFocus(surface)',focus_grab)
        self.assertIn('if (g_pInputManager->isLocked() && grab)',SEAT)
        self.assertIn('return m_pointerConstraints.locked();',INPUT)
        # Passing detects the counterexample premise, NOT a corrected grab gate.
    def test_05_locker_crash_not_release(self):
        body=function(PROTO,'void CSessionLockProtocol::destroyResource(CSessionLock* lock)')
        self.assertNotIn('m_locked = false',body)
        self.assertIn('the compositor must not\n      unlock the session in response',XML)
    def test_06_ipc_disconnect_boolean_is_not_authority(self):
        r=callback_trace('missing_state',[{'locked':True},{}])
        self.assertFalse(r['trace'][-1]['locked'])
        self.assertNotIn('SessionService',FOCUS)
        self.assertNotIn('DMS',function(PROTO,'bool CSessionLockProtocol::isLocked()'))
    def test_07_repeated_lock_callbacks(self):
        r=callback_trace('duplicates',[{'locked':True},{'locked':True},{'locked':False},{'locked':False}])
        self.assertEqual(r['counts']['locked'],1); self.assertEqual(r['counts']['unlocked'],1)
    def test_08_external_native_lock_path(self):
        body=function(PROTO,'void CSessionLockProtocol::onLock(')
        self.assertIn('m_events.newLock.emit(RESOURCE)',body); self.assertIn('m_locked = true',body)
        self.assertNotIn('wilsof',body.lower())
        self.assertIn('The client is responsible for performing authentication',XML)
    def test_09_real_release_source_only(self):
        unlock=PROTO[PROTO.index('m_resource->setUnlockAndDestroy'):PROTO.index('CSessionLock::~CSessionLock')]
        self.assertIn('m_locked = false',unlock); self.assertIn('if (m_inert)',unlock)
        self.assertIn('sendUnlockAndDestroy()',read('hyprlock','src/core/hyprlock.cpp'))
        self.assertFalse(callback_trace('release_ui',[{'locked':True},{'locked':False}])['trace'][-1]['locked'])
    def test_10_new_session_callback_rebind(self):
        r=callback_trace('new_session',[{'sessionId':'old','locked':True},{'sessionId':'new','locked':False}])
        self.assertEqual(r['trace'][-1],{'sessionId':'new','locked':False})
        self.assertNotIn('generation',CALLBACK)
        # Does not prove compositor/session service rebinding or auto-lock policy.

suite=unittest.defaultTestLoader.loadTestsFromTestCase(BoundaryContracts)
result=unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({'kind':'SOURCE_CONTRACT_AND_REAL_JS_CALLBACK_ONLY','native_acceptance':False,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skips':len(result.skipped),'callback_sha256':hashlib.sha256(CALLBACK.encode()).hexdigest(),'callback_traces':TRACES},sort_keys=True))
raise SystemExit(not result.wasSuccessful())
