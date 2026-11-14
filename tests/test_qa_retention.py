"""Producer lifecycle and bounded post-test maintenance integration."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import pytest
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def api():
    path = ROOT / 'scripts/qa-retention.py'
    assert path.is_file(), 'QA producers have no creation/finalization retention helper'
    spec = importlib.util.spec_from_file_location('retention', path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepared_run(tmp_path):
    m = api()
    kept = tmp_path / 'retained-raw-seed'
    kept.write_bytes(b'known disposable raw disk fixture')
    run = tmp_path / 'new-run'
    spec = {'schema': 1, 'run_id': 'passed-fixture', 'source_commit': 'a' * 40,
            'inputs': [{'path': str(kept), 'sha256': sha(kept)}],
            'outputs': [{'path': 'artifacts/test.raw', 'classification': 'DISPOSABLE'},
                        {'path': 'evidence/result.json', 'classification': 'PROTECTED'}]}
    m.begin(str(run), spec)
    assert json.loads((run / 'retention-start.json').read_text())['state'] == 'ACTIVE'
    (run / 'artifacts').mkdir()
    disk = run / 'artifacts/test.raw'
    disk.write_bytes(kept.read_bytes())
    (run / 'evidence').mkdir()
    evidence = run / 'evidence/result.json'
    evidence.write_text('{"observed": "PASS"}')
    result = {'schema': 1, 'run_id': 'passed-fixture', 'exit_code': 0,
              'pending_acceptance': False, 'timed_out': False,
              'checks': [{'name': 'fixture', 'status': 'PASS',
                          'evidence': [{'path': str(evidence), 'sha256': sha(evidence)}]}]}
    result_path = run / 'test-result.json'
    result_path.write_text(json.dumps(result))
    policy = {'version': 1, 'roots': [str(disk.parent)], 'protected': [str(kept), str(evidence)],
              'pins': spec['inputs'], 'locks': [str(tmp_path / 'existing-workflow.lock')],
              'image_roots': [str(disk.parent)],
              'artifacts': [{'id': 'fixture-raw', 'path': str(disk), 'classification': 'DISPOSABLE',
                             'sha256': sha(disk), 'proof': {'path': str(kept), 'sha256': sha(kept)},
                             'workflow': {'id': 'passed-fixture', 'state': 'completed',
                                          'result': 'success', 'pending_acceptance': False}}]}
    policy_path = run / 'cleanup-policy.json'
    policy_path.write_text(json.dumps(policy))
    return m, run, disk, evidence, kept, result_path, policy_path


def test_successful_run_produces_verified_bounded_cleanup_plan(tmp_path):
    m, run, disk, evidence, kept, result_path, policy_path = prepared_run(tmp_path)
    finished = m.finish(str(run), str(result_path), str(policy_path), seconds=30)
    assert finished['state'] == 'CLEANUP_REVIEW_REQUIRED'
    plan = json.loads((run / 'cleanup-plan.json').read_text())
    assert plan['targets'][0]['path'] == str(disk)
    assert finished['plan_sha256'] == plan['plan_sha256']
    assert disk.exists() and evidence.exists() and kept.exists()
    assert finished['applied'] is False


@pytest.mark.parametrize('where', ['begin', 'finish'])
def test_boolean_schema_is_not_integer_schema(tmp_path, where):
    m, run, disk, _, kept, result_path, policy_path = prepared_run(tmp_path)
    if where == 'begin':
        spec = json.loads((run / 'retention-start.json').read_text())
        spec['schema'] = True
        new = tmp_path / 'boolean-schema-run'
        with pytest.raises(ValueError):
            m.begin(str(new), spec)
        assert not new.exists()
    else:
        result = json.loads(result_path.read_text())
        result['schema'] = True
        result_path.write_text(json.dumps(result))
        finished = m.finish(str(run), str(result_path), str(policy_path), seconds=30)
        assert finished['state'] == 'RETAIN'
        assert not (run / 'cleanup-plan.json').exists()
    assert disk.exists() and kept.exists()


@pytest.mark.parametrize('change', ['failed', 'timeout', 'pending', 'no-checks', 'failed-check', 'wrong-run'])
def test_incomplete_runs_retain_every_output_without_planning(tmp_path, monkeypatch, change):
    m, run, disk, evidence, kept, result_path, policy_path = prepared_run(tmp_path)
    result = json.loads(result_path.read_text())
    if change == 'failed': result['exit_code'] = 7
    if change == 'timeout': result['timed_out'] = True
    if change == 'pending': result['pending_acceptance'] = True
    if change == 'no-checks': result['checks'] = []
    if change == 'failed-check': result['checks'][0]['status'] = 'FAIL'
    if change == 'wrong-run': result['run_id'] = 'another-run'
    result_path.write_text(json.dumps(result))
    def forbidden(*args, **kwargs):
        raise AssertionError('failed workflow must not invoke a cleanup planner')
    monkeypatch.setattr(m, 'bounded_plan', forbidden)
    completed = m.finish(str(run), str(result_path), str(policy_path))
    assert completed['state'] == 'RETAIN' and completed['applied'] is False
    assert not (run / 'cleanup-plan.json').exists()
    assert disk.exists() and evidence.exists() and kept.exists()


@pytest.mark.parametrize('change', ['evidence', 'input', 'foreign-target', 'protected', 'workflow', 'root'])
def test_unsafe_retention_contract_cannot_produce_cleanup_plan(tmp_path, change):
    m, run, disk, evidence, kept, result_path, policy_path = prepared_run(tmp_path)
    policy = json.loads(policy_path.read_text())
    if change == 'evidence': evidence.write_text('changed evidence')
    if change == 'input': kept.write_bytes(b'changed input')
    if change == 'foreign-target': policy['artifacts'][0]['path'] = str(kept)
    if change == 'protected': policy['artifacts'][0]['path'] = str(evidence)
    if change == 'workflow': policy['artifacts'][0]['workflow']['id'] = 'other-run'
    if change == 'root': policy['roots'] = [str(tmp_path)]
    policy_path.write_text(json.dumps(policy))
    with pytest.raises(ValueError):
        m.finish(str(run), str(result_path), str(policy_path), seconds=30)
    assert not (run / 'cleanup-plan.json').exists()
    assert disk.exists() and evidence.exists() and kept.exists()


def test_real_cli_preserves_receipts_and_refuses_refinalization(tmp_path):
    m, run, disk, evidence, kept, result_path, policy_path = prepared_run(tmp_path)
    command = [sys.executable, '-I', str(ROOT / 'scripts/qa-retention.py'), 'finish',
               '--run-root', str(run), '--result', str(result_path),
               '--policy', str(policy_path), '--seconds', '30']
    done = subprocess.run(command, capture_output=True, text=True, timeout=40)
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout)['state'] == 'CLEANUP_REVIEW_REQUIRED'
    before = (run / 'retention-finish.json').read_bytes()
    again = subprocess.run(command, capture_output=True, text=True, timeout=10)
    assert again.returncode == 1 and 'already finalized' in again.stderr
    assert (run / 'retention-finish.json').read_bytes() == before
    assert disk.exists() and evidence.exists() and kept.exists()


def test_plan_timeout_stops_owned_descendants(tmp_path, monkeypatch):
    import os
    import time
    m = api()
    helper = tmp_path / 'finite-plan-fixture.py'
    pid_path = tmp_path / 'child.pid'
    helper.write_text('import subprocess,sys,time,pathlib\n'
                      'p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(8)"])\n'
                      f'pathlib.Path({str(pid_path)!r}).write_text(str(p.pid))\n'
                      'p.wait(timeout=10)\n')
    guards = m.maintenance()
    monkeypatch.setattr(m, 'MAINTENANCE', helper)
    start = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        m.bounded_plan(tmp_path / 'unused-policy.json', 1, guards)
    assert time.monotonic() - start < 7
    pid = int(pid_path.read_text())
    try:
        state = Path(f'/proc/{pid}/stat').read_text().split()[2]
    except (FileNotFoundError, ProcessLookupError):
        state = 'exited'
    assert state in ('Z', 'exited'), f'owned planner descendant remains live: {pid}'


@pytest.mark.parametrize('stop_signal', ['SIGTERM', 'SIGHUP', 'SIGINT', 'SIGTERM+SIGINT'])
def test_cli_signal_cancels_separate_planner_group(tmp_path, stop_signal):
    import os
    import shutil
    import signal
    import time
    _, run, disk, evidence, kept, result_path, policy_path = prepared_run(tmp_path)
    copied = tmp_path / 'signal-fixture-tools'
    copied.mkdir()
    shutil.copy2(ROOT / 'scripts/qa-retention.py', copied / 'qa-retention.py')
    planner_state = tmp_path / 'planner-processes.json'
    tool = (ROOT / 'scripts/artifact-maintenance.py').read_text()
    hook = ('if __name__ == "__main__" and "plan" in sys.argv:\n'
            + ('    signal.signal(signal.SIGTERM,signal.SIG_IGN)\n' if '+' in stop_signal else '') +
            '    owned = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10)"])\n'
            f'    Path({str(planner_state)!r}).write_text(json.dumps([os.getpid(), owned.pid]))\n'
            '    owned.wait(timeout=12)\n'
            '    sys.exit(1)\n\n')
    tool = tool.replace("if __name__ == '__main__':", hook + "if __name__ == '__main__':")
    (copied / 'artifact-maintenance.py').write_text(tool)
    command = [sys.executable, '-I', str(copied / 'qa-retention.py'), 'finish',
               '--run-root', str(run), '--result', str(result_path),
               '--policy', str(policy_path), '--seconds', '8']
    owned_ids = []
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          start_new_session=True) as cli:
        try:
            deadline = time.monotonic() + 4
            while not planner_state.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            assert planner_state.exists(), 'CLI never reached planner boundary'
            owned_ids = json.loads(planner_state.read_text())
            first = getattr(signal, stop_signal.split('+')[0])
            os.kill(cli.pid, first)
            if '+' in stop_signal:
                time.sleep(0.05)
                os.kill(cli.pid, signal.SIGINT)
            cli.communicate(timeout=8)
            assert cli.returncode == 128 + first
            states = []
            for pid in owned_ids:
                try: states.append(Path(f'/proc/{pid}/stat').read_text().split()[2])
                except (FileNotFoundError, ProcessLookupError): states.append('exited')
            assert all(state in ('Z', 'exited') for state in states), states
            assert not (run / 'cleanup-plan.json').exists()
            assert disk.exists() and evidence.exists() and kept.exists()
        finally:
            # The RED control must not leave its reproduced orphan behind.
            if owned_ids:
                try: os.killpg(owned_ids[0], signal.SIGTERM)
                except ProcessLookupError: pass
            if cli.poll() is None:
                cli.terminate()
                cli.communicate(timeout=4)


def test_receipt_creation_fsyncs_file_and_parent(tmp_path, monkeypatch):
    import os
    import stat
    m = api()
    kinds = []
    original = os.fsync
    def observed(fd):
        kinds.append('directory' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'file')
        return original(fd)
    monkeypatch.setattr(m.os, 'fsync', observed)
    m.save(tmp_path / 'receipt.json', {'schema': 1})
    assert kinds == ['file', 'directory']


def test_oversized_json_is_refused_before_hashing(tmp_path, monkeypatch):
    m = api()
    guards = m.maintenance()
    oversized = tmp_path / 'oversized.json'
    with oversized.open('wb') as stream:
        stream.truncate(4 * 1024 * 1024 + 1)
    def forbidden_hash(*args, **kwargs):
        raise AssertionError('oversized JSON must not be hashed before size refusal')
    monkeypatch.setattr(guards, 'file_record', forbidden_hash)
    with pytest.raises(ValueError, match='oversized'):
        m.read_json(oversized, guards)


def test_timeout_stops_term_resistant_reader_with_redirected_stdio(tmp_path, monkeypatch):
    import os
    import signal
    m = api()
    guards = m.maintenance()
    helper = tmp_path / 'redirected-reader-plan.py'
    ready = tmp_path / 'reader-ready.pid'
    reader = ('import os,pathlib,signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);'
              f'pathlib.Path({str(ready)!r}).write_text(str(os.getpid()));time.sleep(12)')
    helper.write_text('import pathlib,subprocess,sys,time\n'
                      f'p=subprocess.Popen([sys.executable,"-c",{reader!r}],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n'
                      'deadline=time.monotonic()+2\n'
                      f'while not pathlib.Path({str(ready)!r}).exists() and time.monotonic()<deadline:time.sleep(0.01)\n'
                      'p.wait(timeout=15)\n')
    monkeypatch.setattr(m, 'MAINTENANCE', helper)
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            m.bounded_plan(tmp_path / 'unused-policy.json', 1, guards)
        pid = int(ready.read_text())
        try: state = Path(f'/proc/{pid}/stat').read_text().split()[2]
        except (FileNotFoundError, ProcessLookupError): state = 'exited'
        assert state in ('Z', 'exited'), 'redirected proof-reader survived planner exit'
    finally:
        if ready.exists():
            try: os.kill(int(ready.read_text()), signal.SIGKILL)
            except ProcessLookupError: pass
