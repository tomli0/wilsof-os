"""Small real-file controls for storage admission; never allocate an image."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def api():
    script = ROOT / 'scripts/artifact-lifecycle.py'
    assert script.is_file(), 'Missing bounded storage admission before allocation'
    spec = importlib.util.spec_from_file_location('lifecycle', script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def request(tmp_path, workflow='fixture'):
    return {'schema': 1, 'owner': 'wilsof-test', 'workflow': workflow,
            'purpose': 'Small isolated lifecycle fixture, not image acceptance',
            'budget_bytes': 1024 * 1024,
            'artifacts': [{'path': str(tmp_path / (workflow + '-work')), 'kind': 'build-workspace',
                           'classification': 'DISPOSABLE', 'dependencies': [],
                           'cleanup_condition': 'After verified workflow exit and retained evidence'}]}


def test_registration_precedes_allocation_and_records_custody(tmp_path):
    m = api()
    catalog = tmp_path / 'catalog.json'
    spec = request(tmp_path)
    result = m.register(str(catalog), spec)
    assert result['workflow'] == 'fixture'
    assert result['created_ns'] > 0
    assert result['state'] == 'ACTIVE'
    assert not Path(spec['artifacts'][0]['path']).exists()
    saved = json.loads(catalog.read_text())['workflows'][0]
    assert saved['owner'] == spec['owner'] and saved['purpose'] == spec['purpose']
    assert saved['artifacts'][0]['dependencies'] == []
    assert saved['artifacts'][0]['cleanup_condition']


def test_low_capacity_is_refused_before_catalog_or_outputs(tmp_path, monkeypatch):
    import pytest
    m = api()
    monkeypatch.setattr(m.os, 'statvfs', lambda p: type('Space', (), {'f_bavail': 1, 'f_frsize': 1})())
    catalog = tmp_path / 'catalog.json'
    spec = request(tmp_path)
    with pytest.raises(ValueError, match='capacity'):
        m.register(str(catalog), spec)
    assert not catalog.exists() and not Path(spec['artifacts'][0]['path']).exists()


def test_second_workspace_is_refused_and_original_manifest_unchanged(tmp_path):
    import pytest
    m = api()
    catalog = tmp_path / 'catalog.json'
    m.register(str(catalog), request(tmp_path))
    before = catalog.read_bytes()
    with pytest.raises(ValueError, match='limit'):
        m.register(str(catalog), request(tmp_path, 'second'))
    assert catalog.read_bytes() == before


def test_third_iso_or_qa_disk_cannot_be_registered(tmp_path):
    import pytest
    for kind in ('iso', 'qa-disk'):
        m = api()
        catalog = tmp_path / (kind + '.json')
        for i in range(2):
            spec = request(tmp_path, kind + str(i))
            spec['artifacts'][0]['kind'] = kind
            m.register(str(catalog), spec)
        before = catalog.read_bytes()
        third = request(tmp_path, kind + 'third')
        third['artifacts'][0]['kind'] = kind
        with pytest.raises(ValueError, match='limit'):
            m.register(str(catalog), third)
        assert catalog.read_bytes() == before


def test_success_cannot_claim_clean_while_disposable_output_remains(tmp_path):
    m = api()
    assert hasattr(m, 'complete'), 'Missing mandatory post-workflow cleanup reconciliation'
    catalog = tmp_path / 'catalog.json'
    spec = request(tmp_path)
    m.register(str(catalog), spec)
    artifact = Path(spec['artifacts'][0]['path'])
    artifact.mkdir()
    assert m.complete(str(catalog), 'fixture', 0)['state'] == 'CLEANUP_PENDING'
    assert artifact.is_dir(), 'Finalization must not blindly delete a workspace'
    artifact.rmdir()  # Empty isolated fixture, not a product workspace.
    assert m.complete(str(catalog), 'fixture', 0)['state'] == 'COMPLETE'


def test_failure_retains_outputs_and_is_not_acceptance(tmp_path):
    m = api()
    assert hasattr(m, 'complete'), 'Missing post-workflow failure retention'
    catalog = tmp_path / 'catalog.json'
    spec = request(tmp_path)
    m.register(str(catalog), spec)
    artifact = Path(spec['artifacts'][0]['path'])
    artifact.write_bytes(b'failure diagnostic')
    assert m.complete(str(catalog), 'fixture', 7)['state'] == 'RETAIN'
    assert artifact.read_bytes() == b'failure diagnostic'


def test_lock_symlink_and_duplicate_paths_are_refused(tmp_path):
    import pytest
    m = api()
    victim = tmp_path / 'unrelated'
    victim.write_bytes(b'preserve')
    catalog = tmp_path / 'catalog.json'
    lock = Path(str(catalog) + '.lock')
    lock.symlink_to(victim)
    with pytest.raises((ValueError, OSError)):
        m.register(str(catalog), request(tmp_path))
    assert victim.read_bytes() == b'preserve' and not catalog.exists()
    lock.unlink()
    spec = request(tmp_path)
    spec['artifacts'].append(dict(spec['artifacts'][0], kind='evidence'))
    with pytest.raises(ValueError, match='duplicate'):
        m.register(str(catalog), spec)
    assert not catalog.exists()


def test_audit_bounds_cache_and_expired_logs_without_deleting(tmp_path, monkeypatch):
    import os
    import time
    m = api()
    assert hasattr(m, 'audit'), 'Missing bounded cache/log retention enforcement'
    catalog = tmp_path / 'catalog.json'
    spec = request(tmp_path)
    spec['artifacts'] = [dict(spec['artifacts'][0], kind='cache')]
    m.register(str(catalog), spec)
    cache = Path(spec['artifacts'][0]['path'])
    cache.write_bytes(b'cache-fixture')
    monkeypatch.setattr(m, 'CACHE_LIMIT', 1)
    assert any('cache' in x for x in m.audit(str(catalog))['violations'])
    state = json.loads(catalog.read_text())
    state['workflows'][0]['artifacts'][0]['kind'] = 'log'
    catalog.write_text(json.dumps(state))
    old = time.time() - 8 * 86400
    os.utime(cache, (old, old))
    assert any('7 days' in x for x in m.audit(str(catalog))['violations'])
    assert cache.read_bytes() == b'cache-fixture'


def test_build_missing_catalog_refuses_before_materialization(tmp_path):
    import subprocess
    from build_fixture import layout
    source, _, _, env = layout(tmp_path)
    env.pop('WILSOF_ARTIFACT_CATALOG', None)
    env.pop('WILSOF_WORKFLOW_ID', None)
    result = subprocess.run(['sh', str(source / 'scripts/build-iso.sh'), '--build'],
                            env=env, capture_output=True, text=True)
    assert result.returncode != 0, 'Build allocated outputs without storage admission'
    assert not Path(env['CAPTURE']).exists()
    assert not Path(env['WILSOF_ISO_OUTDIR']).exists()


def test_qa_cli_requires_host_catalog_before_run_creation(tmp_path):
    import hashlib
    import subprocess
    import sys
    seed = tmp_path / 'seed'
    seed.write_bytes(b'known tiny input')
    run = tmp_path / 'qa-run'
    spec = {'schema': 1, 'run_id': 'new-qa', 'source_commit': 'a' * 40,
            'inputs': [{'path': str(seed), 'sha256': hashlib.sha256(seed.read_bytes()).hexdigest()}],
            'outputs': [{'path': 'artifacts/tiny.raw', 'classification': 'DISPOSABLE'}]}
    source = tmp_path / 'qa-spec.json'
    source.write_text(json.dumps(spec))
    cp = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/qa-retention.py'),
                         'begin', '--run-root', str(run), '--spec', str(source)],
                        capture_output=True, text=True)
    assert cp.returncode != 0, 'QA started without bounded host-wide admission'
    assert not run.exists()


def test_qa_cli_accepts_only_registered_exact_outputs(tmp_path):
    import hashlib
    import subprocess
    import sys
    seed = tmp_path / 'seed'
    seed.write_bytes(b'tiny')
    run = tmp_path / 'qa-run'
    catalog = tmp_path / 'catalog.json'
    catalog.write_text(json.dumps({'schema': 1, 'inventory_complete': True, 'workflows': []}))
    spec = request(tmp_path, 'new-qa')
    spec['artifacts'][0].update(path=str(run / 'artifacts/tiny.raw'), kind='qa-disk')
    api().register(str(catalog), spec)
    qa = {'schema': 1, 'run_id': 'new-qa', 'source_commit': 'a' * 40,
          'inputs': [{'path': str(seed), 'sha256': hashlib.sha256(seed.read_bytes()).hexdigest()}],
          'outputs': [{'path': 'artifacts/tiny.raw', 'classification': 'DISPOSABLE'}]}
    source = tmp_path / 'qa-spec.json'
    source.write_text(json.dumps(qa))
    cp = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/qa-retention.py'),
                         'begin', '--run-root', str(run), '--spec', str(source),
                         '--catalog', str(catalog)], capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    receipt = json.loads((run / 'retention-start.json').read_text())
    assert receipt['storage_catalog'] == str(catalog)
    assert receipt['owner'] == 'wilsof-test'
    assert not (run / 'artifacts/tiny.raw').exists()
    result = run / 'result.json'
    result.write_text(json.dumps({'schema': 1, 'run_id': 'new-qa', 'exit_code': 7,
                                 'timed_out': False, 'pending_acceptance': False, 'checks': []}))
    finished = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/qa-retention.py'),
                               'finish', '--run-root', str(run), '--result', str(result)],
                              capture_output=True, text=True)
    assert finished.returncode == 0, finished.stderr
    assert json.loads(catalog.read_text())['workflows'][0]['state'] == 'RETAIN'


def test_catalog_audit_never_follows_internal_symlinks(tmp_path):
    m = api()
    directory = tmp_path / 'cache'
    directory.mkdir()
    outside = tmp_path / 'outside'
    outside.write_bytes(b'not cache content')
    (directory / 'alias').symlink_to(outside)
    allocated, files = m.usage(directory)
    assert allocated == directory.stat().st_blocks * 512
    assert not files
    assert outside.read_bytes() == b'not cache content'


def test_capacity_is_refreshed_under_admission_lock(tmp_path, monkeypatch):
    import pytest
    m = api()
    readings = iter([100 * m.GIB, 1])
    monkeypatch.setattr(m.os, 'statvfs', lambda p: type('Space', (), {'f_bavail': next(readings), 'f_frsize': 1})())
    with pytest.raises(ValueError, match='capacity'):
        m.register(str(tmp_path / 'catalog.json'), request(tmp_path))
    assert not (tmp_path / 'catalog.json').exists()


def test_iso_directory_cannot_hide_multiple_images_in_one_slot(tmp_path):
    m = api()
    catalog = tmp_path / 'catalog.json'
    spec = request(tmp_path)
    spec['artifacts'][0]['kind'] = 'iso'
    m.register(str(catalog), spec)
    directory = Path(spec['artifacts'][0]['path'])
    directory.mkdir()
    for name in ('one.iso', 'two.iso', 'three.iso'):
        (directory / name).write_bytes(b'tiny nonbootable fixture')
    assert any('iso' in v for v in m.audit(str(catalog))['violations'])


def test_build_refuses_missing_or_uninventoried_catalog_before_outputs(tmp_path):
    import subprocess
    from build_fixture import layout
    for missing in (True, False):
        location = tmp_path / ('missing' if missing else 'uninventoried')
        location.mkdir()
        source, _, _, env = layout(location)
        catalog = Path(env['WILSOF_ARTIFACT_CATALOG'])
        catalog.unlink(missing_ok=True)
        if not missing:
            catalog.write_text(json.dumps({'schema': 1, 'workflows': []}))
        cp = subprocess.run(['sh', str(source / 'scripts/build-iso.sh'), '--build'],
                            env=env, capture_output=True, text=True)
        assert cp.returncode != 0, 'Build synthesized or trusted an unreviewed empty catalog'
        assert not Path(env['CAPTURE']).exists()
        assert not Path(env['WILSOF_ISO_OUTDIR']).exists()
        assert not Path(env['WILSOF_ISO_WORKDIR'] + '-profile').exists()
        if missing:
            assert not catalog.exists()


def test_closeout_reports_actual_over_budget_without_deleting(tmp_path):
    m = api()
    catalog = tmp_path / 'catalog.json'
    spec = request(tmp_path)
    spec['budget_bytes'] = 4096
    m.register(str(catalog), spec)
    artifact = Path(spec['artifacts'][0]['path'])
    artifact.write_bytes(b'x' * 8192)
    assert any('workflow budget' in v for v in m.audit(str(catalog))['violations'])
    result = m.complete(str(catalog), 'fixture', 0)
    assert result['state'] == 'RETAIN'
    assert any('workflow budget' in v for v in result['violations'])
    assert artifact.read_bytes() == b'x' * 8192


def test_closeout_reports_exhausted_emergency_reserve(tmp_path, monkeypatch):
    m = api()
    catalog = tmp_path / 'catalog.json'
    spec = request(tmp_path)
    m.register(str(catalog), spec)
    artifact = Path(spec['artifacts'][0]['path'])
    artifact.write_bytes(b'preserved result')
    monkeypatch.setattr(m.os, 'statvfs', lambda p: type('Space', (), {'f_bavail': 1, 'f_frsize': 1})())
    result = m.complete(str(catalog), 'fixture', 0)
    assert result['state'] == 'RETAIN'
    assert any('reserve' in v for v in result['violations'])
    assert artifact.read_bytes() == b'preserved result'


def test_qa_rechecks_stale_reservations_and_reports_final_retention_violation(tmp_path):
    import hashlib
    import os
    import subprocess
    import sys
    import time
    for phase in ('begin', 'finish'):
        location = tmp_path / phase
        location.mkdir()
        seed = location / 'seed'
        seed.write_bytes(b'tiny input')
        run = location / 'qa-run'
        log = location / 'ordinary.log'
        catalog = location / 'catalog.json'
        catalog.write_text(json.dumps({'schema': 1, 'inventory_complete': True, 'workflows': []}))
        spec = request(location, 'stale-qa')
        spec['artifacts'][0].update(path=str(run / 'artifacts/tiny.raw'), kind='qa-disk')
        spec['artifacts'].append(dict(spec['artifacts'][0], path=str(log), kind='log'))
        api().register(str(catalog), spec)
        qa = {'schema': 1, 'run_id': 'stale-qa', 'source_commit': 'a' * 40,
              'inputs': [{'path': str(seed), 'sha256': hashlib.sha256(seed.read_bytes()).hexdigest()}],
              'outputs': [{'path': 'artifacts/tiny.raw', 'classification': 'DISPOSABLE'}]}
        source = location / 'spec.json'
        source.write_text(json.dumps(qa))
        def expire_log():
            log.write_bytes(b'preserve stale log')
            old = time.time() - 8 * 86400
            os.utime(log, (old, old))
        if phase == 'begin':
            expire_log()
        start = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/qa-retention.py'),
                                'begin', '--run-root', str(run), '--spec', str(source),
                                '--catalog', str(catalog)], capture_output=True, text=True)
        if phase == 'begin':
            assert start.returncode != 0, 'QA reused a now-noncompliant reservation'
            assert not run.exists()
            assert '7 days' in start.stderr
        else:
            assert start.returncode == 0, start.stderr
            expire_log()
            result = run / 'result.json'
            result.write_text(json.dumps({'schema': 1, 'run_id': 'stale-qa', 'exit_code': 7,
                                         'timed_out': False, 'pending_acceptance': False, 'checks': []}))
            finished = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/qa-retention.py'),
                                       'finish', '--run-root', str(run), '--result', str(result)],
                                      capture_output=True, text=True)
            assert finished.returncode != 0
            assert '7 days' in finished.stderr
            assert (run / 'retention-finish.json').is_file()
            assert json.loads(catalog.read_text())['workflows'][0]['state'] == 'RETAIN'
        assert log.read_bytes() == b'preserve stale log'
