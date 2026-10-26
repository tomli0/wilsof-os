"""Live guards must survive Archiso's documented copy-to-RAM media unmount."""
from pathlib import Path
import runpy
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_live_provisioning_accepts_ram_root_after_boot_media_unmount(monkeypatch):
    validate = runpy.run_path(str(ROOT / 'runtime/provision-target'))['validate_target']
    reads = {
        '/usr/lib/os-release': 'ID=arch\n',
        '/etc/passwd': 'live:x:1000:1000::/home/live:/bin/bash\n',
    }
    original_read = Path.read_text
    monkeypatch.setattr(Path, 'read_text', lambda p, *a, **k: reads[str(p)] if str(p) in reads else original_read(p, *a, **k))
    monkeypatch.setattr(Path, 'exists', lambda p: str(p) in reads)
    monkeypatch.setattr(Path, 'is_symlink', lambda p: False)
    monkeypatch.setattr(Path, 'is_mount', lambda p: str(p) == '/run/archiso/airootfs')
    assert validate(Path('/'), 'live', True) == Path('/')


@pytest.mark.parametrize('live_root', [True, False])
def test_installer_ram_boot_guard_preserves_live_only_boundary(monkeypatch, live_root):
    import importlib
    from types import SimpleNamespace
    m = importlib.import_module('installer.wilsof_installer')
    monkeypatch.setattr(m.sys, 'stdin', SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(m.sys, 'stdout', SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(m.os, 'geteuid', lambda: 0)
    monkeypatch.setattr(m, 'check_platform', lambda *a: None)
    monkeypatch.setattr(m, 'check_firmware', lambda: None)
    monkeypatch.setattr(Path, 'is_mount', lambda p: live_root and str(p) == '/run/archiso/airootfs')
    monkeypatch.setattr(m, 'guest_policy', lambda: ([], False))
    monkeypatch.setattr(m, 'ArchinstallExecutor', lambda **kw: object())
    reached = []
    monkeypatch.setattr(m, 'interactive', lambda executor: reached.append(True))
    assert m.main([]) == (0 if live_root else 1)
    assert bool(reached) == live_root


def test_live_provisioning_rejects_an_installed_root(monkeypatch):
    validate = runpy.run_path(str(ROOT / 'runtime/provision-target'))['validate_target']
    monkeypatch.setattr(Path, 'is_mount', lambda p: False)
    with pytest.raises(ValueError, match='booted Archiso'):
        validate(Path('/'), 'live', True)
