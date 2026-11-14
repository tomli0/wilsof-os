"""Failed outcome stays failed; only independently duplicated payload can retire."""
import copy
import hashlib
import json
from pathlib import Path

import pytest
from test_artifact_maintenance import lab  # Real-file maintenance fixture.


def failed_policy(lab):
    m, policy, target, kept = lab
    failure = target.parent.parent / 'failed-build.json'
    failure.write_text(json.dumps({'schema': 1, 'workflow': 'fixture-failed',
                                   'result': 'FAIL', 'exit_code': 7}))
    evidence = {}
    for name in ('inputs', 'log', 'reproduction'):
        path = target.parent.parent / (name + '.txt')
        path.write_text('retained ' + name)
        evidence[name] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    evidence['failure'] = {'path': str(failure), 'sha256': hashlib.sha256(failure.read_bytes()).hexdigest()}
    policy['pins'] += list(evidence.values())
    policy['protected'] += [r['path'] for r in evidence.values()]
    policy['artifacts'][0]['workflow'] = {
        'id': 'fixture-failed', 'state': 'completed', 'result': 'failure',
        'pending_acceptance': False,
        'retirement': {'scope': 'duplicate-intermediates-only', 'evidence': evidence}}
    return m, policy, target, kept, failure


def test_failed_build_payload_can_be_planned_without_fabricated_success(lab):
    m, policy, target, kept, failure = failed_policy(lab)
    original = copy.deepcopy(policy)
    receipt = failure.read_bytes()
    result = m.plan(policy)
    assert result['targets'][0]['path'] == str(target)
    assert policy == original
    assert failure.read_bytes() == receipt
    assert json.loads(receipt)['exit_code'] == 7
    assert target.exists() and kept.exists()


@pytest.mark.parametrize('change', ['no-retirement', 'no-log', 'unpinned', 'changed-evidence',
                                   'success-receipt', 'wrong-workflow', 'zero-exit',
                                   'pending', 'active', 'wrong-scope'])
def test_failed_build_retirement_keeps_fail_closed_guards(lab, change):
    m, policy, target, kept, failure = failed_policy(lab)
    workflow = policy['artifacts'][0]['workflow']
    if change == 'no-retirement': workflow.pop('retirement')
    if change == 'no-log': workflow['retirement']['evidence'].pop('log')
    if change == 'unpinned': policy['pins'] = policy['pins'][:-1]
    if change == 'changed-evidence': failure.write_text('modified')
    if change in ('success-receipt', 'wrong-workflow', 'zero-exit'):
        data = json.loads(failure.read_text())
        if change == 'success-receipt': data['result'] = 'PASS'
        if change == 'wrong-workflow': data['workflow'] = 'another'
        if change == 'zero-exit': data['exit_code'] = 0
        failure.write_text(json.dumps(data))
        digest = hashlib.sha256(failure.read_bytes()).hexdigest()
        workflow['retirement']['evidence']['failure']['sha256'] = digest
        policy['pins'][-1]['sha256'] = digest
    if change == 'pending': workflow['pending_acceptance'] = True
    if change == 'active': workflow['state'] = 'active'
    if change == 'wrong-scope': workflow['retirement']['scope'] = 'all-data'
    with pytest.raises((m.Refusal, ValueError)):
        m.plan(policy)
    assert target.exists() and kept.exists()


def test_repeated_failures_retire_only_payload_and_preserve_each_fail(lab, monkeypatch, tmp_path):
    m, policy, target, kept, failure = failed_policy(lab)
    # Only privileged visibility is substituted; hashing, plans, locks, unlink,
    # preservation and durable audit are the production implementations.
    original_guard = m.process_guard
    monkeypatch.setattr(m, 'process_guard', lambda p, t, strict=False: original_guard(p, t, False))
    original_failure = failure.read_bytes()
    payload_blocks = []
    for attempt in range(3):
        if attempt:
            target.write_bytes(kept.read_bytes())
        workflow = policy['artifacts'][0]['workflow']
        workflow['id'] = 'fixture-failed-' + str(attempt)
        data = dict(schema=1, workflow=workflow['id'], result='FAIL', exit_code=7)
        attempt_failure = tmp_path / ('failure-' + str(attempt) + '.json')
        attempt_failure.write_text(json.dumps(data))
        pin = dict(path=str(attempt_failure), sha256=hashlib.sha256(attempt_failure.read_bytes()).hexdigest())
        policy['pins'].append(pin)
        policy['protected'].append(pin['path'])
        workflow['retirement']['evidence']['failure'] = pin
        plan = m.plan(policy)
        result = m.apply_plan(policy, plan['plan_sha256'], ['one'], str(tmp_path / ('audit-' + str(attempt))))
        assert result['removed_count'] == 1 and not target.exists()
        assert json.loads(attempt_failure.read_text()) == data
        payload_blocks.append(sum(p.stat().st_blocks * 512 for p in target.parent.iterdir() if p.is_file()))
    assert payload_blocks == [0, 0, 0]
    assert failure.read_bytes() == original_failure
    assert len(list(tmp_path.glob('failure-*.json'))) == 3
    assert kept.exists()
