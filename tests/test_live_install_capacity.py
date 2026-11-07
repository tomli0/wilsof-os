"""Regression for the real live-overlay ENOSPC, not a package-policy bypass."""
from pathlib import Path
import runpy
import shutil
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('major', [91, 92])
def test_every_linux_boot_entry_sizes_overlay_without_preallocating_ram(tmp_path, major):
    profile = tmp_path / 'profile'
    shutil.copytree(ROOT / 'tests/fixtures' / f'archiso{major}', profile)
    entries = profile / 'efiboot/loader/entries'
    # An inherited small limit must not survive, nor create duplicate arguments.
    for name in ('01-archiso-linux.conf', '02-archiso-speech-linux.conf'):
        path = entries / name
        path.write_text(path.read_text().replace('%KERNEL_PARAMS%', 'cow_spacesize=256M %KERNEL_PARAMS%'))
    configure = runpy.run_path(str(ROOT / 'scripts/boot-profile.py'))['configure_boot']
    configure(profile, ROOT)
    linux = [p for p in entries.glob('*.conf') if any(line.startswith('linux ') for line in p.read_text().splitlines())]
    assert len(linux) == 4
    for entry in linux:
        args = next(line.split()[1:] for line in entry.read_text().splitlines() if line.startswith('options '))
        assert [arg for arg in args if arg.startswith('cow_spacesize=')] == ['cow_spacesize=75%']
        assert {'archisobasedir=%INSTALL_DIR%', 'archisosearchuuid=%ARCHISO_UUID%', '%KERNEL_PARAMS%'} <= set(args)
    assert 'cow_spacesize' not in (entries / '05-wilsof-memtest.conf').read_text()
    before = {str(p.relative_to(profile)): p.read_bytes() for p in profile.rglob('*') if p.is_file()}
    configure(profile, ROOT)
    assert before == {str(p.relative_to(profile)): p.read_bytes() for p in profile.rglob('*') if p.is_file()}


@pytest.mark.parametrize('free_mib,total_mib,available_mib,accepted', [
    (2048, 3900, 2800, True),
    (1792, 3584, 2304, True),
    (256, 3900, 2800, False),
    (1791, 3900, 2800, False),
    (2048, 3900, 2303, False),
    (2048, 3583, 2800, False),
])
def test_installation_capacity_gate_checks_real_free_space_and_available_ram(
    tmp_path, monkeypatch, free_mib, total_mib, available_mib, accepted
):
    from installer import wilsof_installer as m
    from types import SimpleNamespace
    assert callable(getattr(m, 'check_live_capacity', None)), 'Missing pre-package capacity guard'
    memory = tmp_path / 'meminfo'
    memory.write_text(f'MemTotal: {total_mib * 1024} kB\nMemAvailable: {available_mib * 1024} kB\n')
    monkeypatch.setattr(m.os, 'statvfs', lambda p: SimpleNamespace(f_bavail=free_mib, f_frsize=1024**2))
    if accepted:
        m.check_live_capacity(directory=tmp_path, memory=memory)
    else:
        with pytest.raises(m.Refusal, match='RAM|writable'):
            m.check_live_capacity(directory=tmp_path, memory=memory)


def installer_main_fixture(monkeypatch):
    from installer import wilsof_installer as m
    from types import SimpleNamespace
    monkeypatch.setattr(m.sys, 'stdin', SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(m.sys, 'stdout', SimpleNamespace(isatty=lambda: True))
    monkeypatch.setattr(m.os, 'geteuid', lambda: 0)
    monkeypatch.setattr(m, 'check_platform', lambda *a: None)
    monkeypatch.setattr(m, 'check_firmware', lambda: None)
    monkeypatch.setattr(Path, 'is_mount', lambda p: str(p) == '/run/archiso/airootfs')
    monkeypatch.setattr(m, 'guest_policy', lambda: ([], False))
    return m


def test_capacity_refusal_happens_before_package_executor_or_disk_prompts(monkeypatch):
    m = installer_main_fixture(monkeypatch)
    def refuse():
        raise m.Refusal('Insufficient RAM')
    monkeypatch.setattr(m, 'check_live_capacity', refuse)
    reached = []
    monkeypatch.setattr(m, 'ArchinstallExecutor', lambda **kw: reached.append('package preflight'))
    monkeypatch.setattr(m, 'interactive', lambda *a: reached.append('disk prompt'))
    assert m.main([]) == 1
    assert reached == []


@pytest.mark.parametrize('inherited', [0o077, 0o000])
@pytest.mark.parametrize('failure', [None, 'refusal', 'backend', 'interrupt', 'eof'])
def test_normal_install_umask_is_scoped_and_restored(tmp_path, monkeypatch, inherited, failure):
    import os
    import stat
    m = installer_main_fixture(monkeypatch)
    monkeypatch.setattr(m, 'check_live_capacity', lambda: None)
    parent = tmp_path / 'target' / 'usr' / 'share'
    def executor(**kw):
        parent.mkdir(parents=True)
        (parent / 'private-keys').mkdir(mode=0o700)
        return object()
    def interactive(_):
        if failure == 'interrupt':
            raise KeyboardInterrupt
        if failure == 'eof':
            raise EOFError
        if failure == 'refusal':
            raise m.Refusal('fixture cancellation')
        if failure == 'backend':
            raise RuntimeError('fixture backend failure')
    monkeypatch.setattr(m, 'ArchinstallExecutor', executor)
    monkeypatch.setattr(m, 'interactive', interactive)
    saved = os.umask(inherited)
    try:
        expected = 0 if failure is None else 130 if failure in ('interrupt', 'eof') else 1
        assert m.main([]) == expected
        observed = os.umask(inherited)
        assert observed == inherited, 'Caller umask must be restored on every exit'
        assert stat.S_IMODE(parent.stat().st_mode) == 0o755
        assert stat.S_IMODE(parent.parent.stat().st_mode) == 0o755
        assert stat.S_IMODE((parent / 'private-keys').stat().st_mode) == 0o700
    finally:
        os.umask(saved)


@pytest.mark.parametrize('text', [
    'MemTotal: 4194304 kB\n',
    'MemTotal: 4194304 kB\nMemAvailable: -1 kB\n',
    'MemTotal: 4194304 kB\nMemAvailable: 9000000 kB\n',
    'MemTotal: 4194304 MB\nMemAvailable: 3000000 kB\n',
    'MemTotal: 4194304 kB\nMemTotal: 4194304 kB\nMemAvailable: 3000000 kB\n',
])
def test_unknown_or_malformed_memory_accounting_is_not_a_capacity_pass(tmp_path, text):
    from installer import wilsof_installer as m
    memory = tmp_path / 'meminfo'
    memory.write_text(text)
    with pytest.raises(m.Refusal, match='Cannot verify'):
        m.check_live_capacity(directory=tmp_path, memory=memory)


def test_unreadable_temporary_capacity_is_not_a_capacity_pass(tmp_path):
    from installer import wilsof_installer as m
    memory = tmp_path / 'meminfo'
    memory.write_text('MemTotal: 4194304 kB\nMemAvailable: 3000000 kB\n')
    with pytest.raises(m.Refusal, match='Cannot verify'):
        m.check_live_capacity(directory=tmp_path / 'missing', memory=memory)
