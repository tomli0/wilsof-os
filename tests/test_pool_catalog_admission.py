"""One32GiB backing object is distinct from the unchanged25GiB build budget."""
import copy
import json
from pathlib import Path

import pytest
from test_artifact_lifecycle import api, request


def pool_request(tmp_path, name='pool'):
    spec = request(tmp_path, name)
    spec['budget_bytes'] = 32 * 1024**3
    spec['artifacts'][0].update(kind='build-pool', classification='PROTECTED')
    return spec


def ample_space(m, monkeypatch):
    monkeypatch.setattr(m.os, 'statvfs', lambda p: type('Space', (), {'f_bavail': 100 * 1024**3, 'f_frsize': 1})())


def test_dedicated_pool_can_reserve_32gib_without_raising_build_budget(tmp_path, monkeypatch):
    m = api()
    ample_space(m, monkeypatch)
    catalog = tmp_path / 'catalog.json'
    result = m.register(str(catalog), pool_request(tmp_path))
    assert result['state'] == 'ACTIVE' and result['budget_bytes'] == 32 * 1024**3
    assert m.MAX_BUDGET == 25 * 1024**3
    assert m.audit(str(catalog))['active_counts']['build-pool'] == 1
    assert not Path(result['artifacts'][0]['path']).exists()
    with pytest.raises(ValueError, match='limit'):
        m.register(str(catalog), pool_request(tmp_path, 'second'))


@pytest.mark.parametrize('change', ['ordinary', 'mixed', 'too-large', 'small', 'disposable', 'exception'])
def test_pool_budget_is_not_a_general_allocation_bypass(tmp_path, monkeypatch, change):
    m = api()
    ample_space(m, monkeypatch)
    spec = pool_request(tmp_path)
    if change == 'ordinary': spec['artifacts'][0]['kind'] = 'build-workspace'
    if change == 'mixed': spec['artifacts'].append(dict(spec['artifacts'][0], path=str(tmp_path / 'another'), kind='cache'))
    if change == 'too-large': spec['budget_bytes'] += 1
    if change == 'small': spec['budget_bytes'] -= 1
    if change == 'disposable': spec['artifacts'][0]['classification'] = 'DISPOSABLE'
    if change == 'exception': spec['artifacts'][0]['exception_reason'] = 'bypass'
    with pytest.raises(ValueError):
        m.register(str(tmp_path / 'catalog.json'), spec)
    assert not (tmp_path / 'catalog.json').exists()


def test_outer_reservation_does_not_double_charge_inner_filesystem(tmp_path, monkeypatch):
    m = api()
    ample_space(m, monkeypatch)
    catalog = tmp_path / 'catalog.json'
    other = request(tmp_path, 'outer')
    other['budget_bytes'] = 16 * 1024**3
    other['artifacts'][0]['kind'] = 'evidence'
    m.register(str(catalog), other)
    original_audit = m.audit
    def measured(catalog, state=None):
        result = original_audit(catalog, state)
        # Only the filesystem-identity measurement is substituted; no allocation.
        for row in result['workflow_usage']:
            row['filesystem_device'] = tmp_path.stat().st_dev + 1
        return result
    monkeypatch.setattr(m, 'audit', measured)
    monkeypatch.setattr(m.os, 'statvfs', lambda p: type('Space', (), {'f_bavail': 31 * 1024**3, 'f_frsize': 1})())
    inner = request(tmp_path, 'inner')
    inner['budget_bytes'] = 25 * 1024**3
    assert m.register(str(catalog), inner)['state'] == 'ACTIVE'


def test_pool_shape_drift_is_audit_failure_not_zero_usage(tmp_path, monkeypatch):
    m = api()
    ample_space(m, monkeypatch)
    catalog = tmp_path / 'catalog.json'
    spec = pool_request(tmp_path)
    m.register(str(catalog), spec)
    Path(spec['artifacts'][0]['path']).write_bytes(b'not-a32GiB-backing')
    assert any('pool' in v for v in m.audit(str(catalog))['violations'])
