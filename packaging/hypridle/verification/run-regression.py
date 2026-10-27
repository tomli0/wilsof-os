#!/usr/bin/env python3
"""Extract actual v0.1.8 event loop/header/main tail; compile/run via read-only Docker.
Only seams: external Wayland/DBus/commands/time/log calls, poll fault injection,
and a nonfunctional worker-lifetime probe inserted at lambda entry.
No production control-flow or synchronization replacements.
"""
import argparse, pathlib, re, subprocess, sys, json, time, os, sqlite3
HERE = pathlib.Path(__file__).resolve().parent
IMAGE = 'nousresearch/hermes-sandbox:desktop'
CASES = ['hard-error','hup','hup-dbus','hup-dbus2','eintr','exception','exception-poll','events','two-fds','wayland-dispatch','retry','retry-false','pollerr','pollnval']
p = argparse.ArgumentParser()
p.add_argument('label')
p.add_argument('--source', type=pathlib.Path, required=True)
p.add_argument('--output', type=pathlib.Path, required=True)
p.add_argument('--image', default=IMAGE)
p.add_argument('--sanitize', default='')
p.add_argument('--no-pie', action='store_true')
a = p.parse_args()
if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', a.label):
    p.error('label must be a simple filename component')
ROOT = a.output.resolve()
ROOT.mkdir(parents=True, exist_ok=True)
if any((ROOT / (a.label + suffix)).exists() for suffix in ('.cpp', '.log')):
    p.error('refusing to overwrite existing evidence for this label')
IMAGE = a.image
source = a.source.resolve()
cpp = (source/'src/core/Hypridle.cpp').read_text()
hpp = (source/'src/core/Hypridle.hpp').read_text()
main = (source/'src/main.cpp').read_text()
body = cpp[cpp.index('void CHypridle::enterEventLoop() {'):cpp.index('\nstatic void spawn(const std::string& args) {')]
body, inserted = re.subn(r'(std::(?:jthread|thread) pollThr\([^\n]*\{)', r'\1\n        WorkerLifetime workerLifetime;', body)
assert inserted == 1
termination = re.search(r'[^\n;]*\bm_bTerminate\s*=\s*false;', hpp).group(0).strip()
internal = re.search(r'    struct \{\n        std::condition_variable(?:_any)? loopSignal;.*?\} m_sEventLoopInternals;', hpp, re.S).group(0)
prefix = (HERE/'harness-prefix.cpp').read_text().replace('TERMINATION_DECLARATION', termination).replace('INTERNALS_DECLARATION', internal)
# Include the actual main run/catch/return tail, not an independently invented exit policy.
start = main.index('    g_pHypridle = std::make_unique<CHypridle>();')
if '    try {\n        g_pHypridle' in main:
    start = main.index('    try {\n        g_pHypridle')
main_tail = main[start:]
generated = prefix + '\n' + body + '\n#undef poll\nint main(int argc, char** argv) {\n    if (argc != 2) return 90;\n    scenario = argv[1];\n    mainThread = std::this_thread::get_id();\n' + main_tail
(ROOT/f'{a.label}.cpp').write_text(generated)
flags = ['-std=c++23','-O1','-g','-pthread','-Wall','-Wextra','-Werror','-Wno-missing-field-initializers']
if a.sanitize: flags += ['-fsanitize='+a.sanitize,'-fno-omit-frame-pointer','-fno-sanitize-recover=all']
if a.no_pie: flags += ['-no-pie']
# Build only in container tmpfs; source mount is read-only. No homes, keys,
# devices, Docker socket, network, guest or parent build root are mounted.
import shlex
script = 'ulimit -c 0\n' + shlex.join(['g++',*flags,'/work/'+a.label+'.cpp','-o','/tmp/regression']) + '\nrc=$?; printf "COMPILE rc=%s\\n" "$rc"; [ "$rc" = 0 ] || exit 2\n'
for case in CASES:
    script += f'printf "CASE_BEGIN {case}\\n"; timeout 12 /tmp/regression {case}; rc=$?; printf "CASE_END {case} rc=%s\\n" "$rc"\n'
cmd = ['docker','run','--pull','never','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','512m','--tmpfs','/tmp:rw,exec,nosuid,nodev', '-v',str(ROOT)+':/work:ro','--entrypoint','/bin/sh',IMAGE,'-c',script]
print('COMMAND '+json.dumps(cmd),flush=True)
r = subprocess.run(cmd, capture_output=True,text=True)
out = r.stdout+r.stderr
passed=0
report=[]
for case in CASES:
    match=re.search(r'CASE_BEGIN '+case+r'\n(.*?)CASE_END '+case+r' rc=(\d+)',r.stdout,re.S)
    text=match.group(1) if match else ''
    rc=int(match.group(2)) if match else None
    ok=(rc==1 and 'CLEANUP main=1 worker_alive=0' in text and 'WORKER_EXIT' in text and text.index('WORKER_EXIT') < text.index('CLEANUP'))
    if case=='eintr': ok=ok and 'calls=3' in text and 'dbus1=1 dbus2=1' in text
    if case=='events': ok=ok and 'dbus1=1 dbus2=1 reads=1' in text
    if case=='two-fds': ok=ok and 'dbus1=1 dbus2=0 reads=1' in text
    if case=='wayland-dispatch': ok=ok and 'reads=0 dispatches=2' in text
    if case=='retry': ok=ok and 'conditions=1 spawns=1 pending=0' in text
    if case=='retry-false': ok=ok and 'conditions=1 spawns=0 pending=1 retry_at=107' in text
    report.append(f'{"PASS" if ok else "FAIL"} {case} rc={rc}')
    passed+=bool(ok)
report.append(f'RESULT {passed}/{len(CASES)} passed')
log='COMMAND '+json.dumps(cmd)+'\n'+out+'\n'+'\n'.join(report)+'\n'
(ROOT/f'{a.label}.log').write_text(log)
print(out+'\n'+'\n'.join(report))
sys.exit(0 if passed==len(CASES) else 1)
