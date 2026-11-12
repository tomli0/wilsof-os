"""Pool arithmetic: internal reserve is included, physical outer growth is not."""
import pytest
from test_artifact_lifecycle import api

G = 1024 ** 3


def test_empty_pool_can_admit_25_plus_5_without_double_counting():
    m = api()
    assert hasattr(m, 'pool_capacity'), 'Missing bounded-pool admission reconciliation'
    r = m.pool_capacity(31 * G, 40 * G, 0)
    assert r['violations'] == []
    assert r['inner_required_bytes'] == 30 * G
    assert r['outer_required_bytes'] == 40 * G
    assert r['additional_staging_headroom_bytes'] == G


def test_preallocated_pool_bytes_are_not_charged_to_host_twice():
    m = api()
    assert hasattr(m, 'pool_capacity'), 'Missing bounded-pool admission reconciliation'
    r = m.pool_capacity(31 * G, 8 * G, 32 * G)
    assert r['violations'] == []
    assert r['outer_required_bytes'] == 8 * G


@pytest.mark.parametrize('inner,outer,allocated,outstanding,gate', [
    (29 * G, 40 * G, 0, 0, 'inner'),
    (31 * G, 39 * G, 0, 0, 'outer'),
    (31 * G, 8 * G, 0, 0, 'outer'),  # sparse length is not backing allocation
    (31 * G, 40 * G, 0, G, 'outer'),
    (25 * G, 40 * G, 0, 0, 'inner'),  # persistent 6GiB cache prevents next admission
])
def test_pool_refuses_impossible_admission(inner, outer, allocated, outstanding, gate):
    m = api()
    assert hasattr(m, 'pool_capacity'), 'Missing bounded-pool admission reconciliation'
    r = m.pool_capacity(inner, outer, allocated, outstanding)
    assert any(gate in x for x in r['violations'])


@pytest.mark.parametrize('values', [(-1, 40 * G, 0), (33 * G, 40 * G, 0),
                                  (31 * G, -1, 0), (31 * G, 40 * G, -1),
                                  (31 * G, 40 * G, 33 * G), (True, 40 * G, 0)])
def test_invalid_pool_measurements_fail_closed(values):
    m = api()
    assert hasattr(m, 'pool_capacity'), 'Missing bounded-pool admission reconciliation'
    with pytest.raises(ValueError):
        m.pool_capacity(*values)
