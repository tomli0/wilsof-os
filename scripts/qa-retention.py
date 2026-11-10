#!/usr/bin/env python3
"""Register QA retention before allocation; seal bounded post-test cleanup plans.

Never deletes or grants cleanup approval. Actual apply uses artifact-maintenance.py
with its independently reviewed policy/plan/target set and authenticated host guards.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time

MAINTENANCE = Path(__file__).with_name('artifact-maintenance.py')


def maintenance():
    spec = importlib.util.spec_from_file_location('maintenance', MAINTENANCE)
    if spec is None or spec.loader is None:
        raise ValueError('maintenance helper is unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path, m):
    path = m.canonical(str(path))
    parent = m.directory(path.parent)
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, 'rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise m.Refusal('retention input is not a regular file')
            limit = 4 * 1024 * 1024
            if before.st_size > limit:
                raise m.Refusal('oversized retention input')
            data = stream.read(limit + 1)
            if len(data) > limit or m.metadata(os.fstat(stream.fileno())) != m.metadata(before):
                raise m.Refusal('retention input changed while reading')
    finally:
        os.close(parent)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise m.Refusal('duplicate retention field')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)


def save(path, value):
    parent = maintenance().directory(path.parent)
    try:
        fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=parent)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(parent)
    finally:
        os.close(parent)


def outputs(spec, root, m):
    entries = spec['outputs']
    if not isinstance(entries, list) or not 0 < len(entries) <= 1024:
        raise m.Refusal('explicit bounded output list required')
    result = {}
    for entry in entries:
        value = entry['path']
        path = Path(value)
        if (path.is_absolute() or str(path) != value or not path.parts or
                any(part in ('.', '..') for part in path.parts) or
                any(ord(c) < 32 for c in value) or
                path.parts[0].startswith('retention-') or
                entry['classification'] not in ('PROTECTED', 'ARCHIVE', 'DISPOSABLE')):
            raise m.Refusal('invalid relative output or retention classification')
        full = str(root / path)
        if full in result:
            raise m.Refusal('duplicate output')
        result[full] = entry['classification']
    return result


def begin(run_root, spec):
    m = maintenance()
    root = m.canonical(run_root)
    if (type(spec.get('schema')) is not int or spec['schema'] != 1 or
            not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]{0,95}', spec['run_id']) or
            not re.fullmatch(r'[0-9a-f]{40}', spec['source_commit'])):
        raise m.Refusal('exact run/source identity required')
    outputs(spec, root, m)
    if not spec['inputs']:
        raise m.Refusal('independently pinned inputs required')
    inputs = []
    for pin in spec['inputs']:
        record = m.file_record(pin['path'])
        if record['sha256'] != pin['sha256']:
            raise m.Refusal('QA input pin mismatch')
        inputs.append(record)
    parent = m.directory(root.parent)
    try:
        os.mkdir(root.name, 0o700, dir_fd=parent)
        os.fsync(parent)
    finally:
        os.close(parent)
    record = dict(spec, state='ACTIVE', started_ns=time.time_ns(), input_records=inputs)
    save(root / 'retention-start.json', record)
    return record


def live_group(group):
    """Pipe EOF/leader reaping does not establish descendant termination."""
    for process in Path('/proc').iterdir():
        if not process.name.isdecimal():
            continue
        try:
            fields = (process / 'stat').read_text().rsplit(')', 1)[1].split()
        except (FileNotFoundError, ProcessLookupError):
            continue
        if int(fields[2]) == group and fields[0] not in ('Z', 'X'):
            return True
    return False


def bounded_plan(policy, seconds, m):
    if type(seconds) is not int or not 1 <= seconds <= 300:
        raise m.Refusal('post-test plan timeout must be 1..300 seconds')
    command = [sys.executable, '-I', str(MAINTENANCE), '--policy', str(policy), 'plan']
    signals = (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)
    previous = {value: signal.getsignal(value) for value in signals}
    def ignore_signals():
        for value in signals:
            signal.signal(value, signal.SIG_IGN)
    def interrupted(signum, frame):
        ignore_signals()
        raise SystemExit(128 + signum)
    try:
        for value in signals:
            signal.signal(value, interrupted)
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, start_new_session=True) as child:
            try:
                out, err = child.communicate(timeout=seconds)
                if live_group(child.pid):
                    raise m.Refusal('planner left live descendants after exit')
                if child.returncode:
                    raise m.Refusal('post-test maintenance plan refused: ' + err.strip())
            except BaseException:
                # Also protect timeout cleanup from a subsequent Ctrl-C/termination.
                ignore_signals()
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    child.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
                # Always escalate the owned group, even after leader exit/pipe EOF.
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                deadline = time.monotonic() + 2
                while live_group(child.pid) and time.monotonic() < deadline:
                    time.sleep(0.01)
                if live_group(child.pid):
                    raise m.Refusal('owned planner group did not stop')
                child.communicate(timeout=2)
                raise
        return json.loads(out)
    finally:
        for value, handler in previous.items():
            signal.signal(value, handler)


def finish(run_root, result_path, policy_path=None, seconds=120):
    m = maintenance()
    root = m.canonical(run_root)
    os.close(m.directory(root))
    if os.path.lexists(root / 'retention-finish.json'):
        raise m.Refusal('run already finalized; preserve its receipt')
    started = read_json(root / 'retention-start.json', m)
    declared = outputs(started, root, m)
    result = read_json(result_path, m)
    completed = {'schema': 1, 'run_id': started['run_id'], 'state': 'RETAIN',
                 'finished_ns': time.time_ns(), 'applied': False}
    checks = result.get('checks', [])
    passed = (type(result.get('schema')) is int and result['schema'] == 1 and
              result.get('run_id') == started['run_id'] and
              type(result.get('exit_code')) is int and result['exit_code'] == 0 and
              result.get('pending_acceptance') is False and result.get('timed_out') is False and
              isinstance(checks, list) and bool(checks) and
              all(c.get('status') == 'PASS' and c.get('name') and c.get('evidence') for c in checks))
    if not passed or policy_path is None:
        completed['reason'] = 'Failure, timeout, pending gates or no explicit cleanup policy; preserve outputs'
        save(root / 'retention-finish.json', completed)
        return completed
    for pin in started['input_records']:
        if m.file_record(pin['path']) != pin:
            raise m.Refusal('QA input changed during run')
    evidence = []
    for check in checks:
        for pin in check['evidence']:
            if declared.get(pin['path']) not in ('PROTECTED', 'ARCHIVE'):
                raise m.Refusal('gate evidence must be declared retained output')
            record = m.file_record(pin['path'])
            if record['sha256'] != pin['sha256']:
                raise m.Refusal('gate evidence hash mismatch')
            evidence.append(record)
    policy = read_json(policy_path, m)
    for value in policy['roots']:
        path = m.canonical(value)
        if not path.is_relative_to(root) or path == root:
            raise m.Refusal('cleanup roots must be strict run subdirectories')
    for artifact in policy['artifacts']:
        if (artifact['classification'] != 'DISPOSABLE' or
                declared.get(artifact['path']) != 'DISPOSABLE' or
                artifact['workflow'] != {'id': started['run_id'], 'state': 'completed',
                                         'result': 'success', 'pending_acceptance': False}):
            raise m.Refusal('cleanup target is not a completed disposable output of this run')
    policy['protected'] = sorted(set(policy['protected']) | {
        path for path, kind in declared.items() if kind != 'DISPOSABLE'})
    receipts = [m.file_record(str(root / 'retention-start.json')), m.file_record(result_path)]
    by_path = {pin['path']: pin['sha256'] for pin in policy['pins']}
    for pin in [*started['input_records'], *evidence, *receipts]:
        if by_path.get(pin['path'], pin['sha256']) != pin['sha256']:
            raise m.Refusal('conflicting protected pin')
        by_path[pin['path']] = pin['sha256']
    policy['pins'] = [{'path': path, 'sha256': digest} for path, digest in sorted(by_path.items())]
    frozen = root / 'cleanup-policy.frozen.json'
    save(frozen, policy)
    plan = bounded_plan(frozen, seconds, m)
    if not plan['targets']:
        raise m.Refusal('no disposable outputs selected')
    save(root / 'cleanup-plan.json', plan)
    save(root / 'cleanup-targets.json', [target['id'] for target in plan['targets']])
    completed.update(state='CLEANUP_REVIEW_REQUIRED', policy_sha256=plan['policy_sha256'],
                     plan_sha256=plan['plan_sha256'], targets=len(plan['targets']),
                     allocated_candidate_bytes=plan['estimated_recoverable_bytes'],
                     visibility='authenticated root apply recheck required')
    save(root / 'retention-finish.json', completed)
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('begin', 'finish'))
    parser.add_argument('--run-root', required=True)
    parser.add_argument('--spec')
    parser.add_argument('--result')
    parser.add_argument('--policy')
    parser.add_argument('--seconds', type=int, default=120)
    args = parser.parse_args()
    try:
        if args.mode == 'begin':
            if not args.spec:
                parser.error('begin requires --spec')
            result = begin(args.run_root, read_json(args.spec, maintenance()))
        else:
            if not args.result:
                parser.error('finish requires --result')
            result = finish(args.run_root, args.result, args.policy, args.seconds)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('REFUSED: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
