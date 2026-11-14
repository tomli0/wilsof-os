"""Source preparation regression, not native/ISO acceptance."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'packaging/xdg-desktop-portal-hyprland'


def test_portal_backport_inputs_are_pinned_and_license_is_packaged():
    metadata = json.loads((PACKAGE / 'provenance.json').read_text())
    assert metadata['upstream_commit'] == 'cc8e5ef8fb2acef3db488b9a33b0c48c2a4ee204'
    assert metadata['fix_commit'] == '0121b2e3f85c7ebf6280173f1054f7e5606262d1'
    recipe = (PACKAGE / 'PKGBUILD').read_text()
    for name in ['wayland-teardown.patch', 'teardown.cpp', 'run.py']:
        assert hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() == metadata['sha256'][name]
        assert metadata['sha256'][name] in recipe
    assert "pkgver=1.4.1" in recipe
    assert "pkgrel=2.1" in recipe
    assert 'SKIP' not in recipe
    assert 'usr/share/licenses/$pkgname/LICENSE' in recipe
    assert 'run.py' in recipe
    assert 'WILSOF_BASELINE_REPRODUCTION' not in (PACKAGE / 'teardown.cpp').read_text()


def test_proxy_ownership_regression_exercises_actual_manager():
    source = (PACKAGE / 'teardown.cpp').read_text()
    assert 'portal->releaseWayland();' in source
    assert 'g_pPortalManager.reset();' in source
    assert 'wl_display_connect_to_fd' in source
    assert 'getAllOutputs()[0]->xdgOutput' in source
    assert source.count('portal->releaseWayland();') == 2
