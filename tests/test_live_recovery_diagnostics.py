"""Recovery must expose session/GPU failures, not only successful boot units."""
from pathlib import Path
import runpy
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


def recovery(monkeypatch):
    module = runpy.run_path(str(ROOT / 'runtime/live-recover'))
    monkeypatch.setattr(module['os'], 'geteuid', lambda: 0)
    monkeypatch.setattr(Path, 'is_mount', lambda self: str(self) == '/run/archiso/airootfs')
    return module


def test_recovery_reports_compositor_and_kernel_separately_from_boot_units(monkeypatch, capsys):
    module = recovery(monkeypatch)
    calls = []

    def run(argv, **kwargs):
        assert 0 < kwargs.get('timeout', 0) <= 20
        calls.append(argv)
        if '-t' in argv and argv[argv.index('-t') + 1] == 'wilsof-session':
            # Real journal fields from a greetd-owned user session must not be
            # intersected with the system unit filter, which hides the failure.
            assert '-u' not in argv
            print('fixture compositor EGL initialization failed')
        elif '-k' in argv:
            assert '-u' not in argv and '-t' not in argv
            print('fixture i915 DRM connector failure')
        elif '_SYSTEMD_USER_UNIT=dms.service' in argv:
            assert '-u' not in argv and '-t' not in argv
            print('fixture Dux startup failure')
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(module['subprocess'], 'run', run)
    assert module['main']([]) == 0
    output = capsys.readouterr().out
    assert 'fixture compositor EGL initialization failed' in output
    assert 'fixture i915 DRM connector failure' in output
    assert 'fixture Dux startup failure' in output
    assert any('-u' in argv and 'wilsof-live-setup' in argv and 'greetd' in argv for argv in calls)
    assert all('-b' in argv and '--no-pager' in argv and '-n' in argv for argv in calls)


@pytest.mark.parametrize('failed_query', [0, 1, 2, 3])
def test_recovery_keeps_other_diagnostics_and_preserves_query_failure(monkeypatch, failed_query):
    module = recovery(monkeypatch)
    calls = []

    def run(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=42 if len(calls) - 1 == failed_query else 0)

    monkeypatch.setattr(module['subprocess'], 'run', run)
    assert module['main']([]) == 42
    assert len(calls) == 4


@pytest.mark.parametrize('failed_query', [0, 1, 2, 3])
def test_recovery_continues_after_a_bounded_query_timeout(monkeypatch, capsys, failed_query):
    module = recovery(monkeypatch)
    calls = []

    def run(argv, **kwargs):
        calls.append(argv)
        if len(calls) - 1 == failed_query:
            raise module['subprocess'].TimeoutExpired(argv, kwargs['timeout'])
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(module['subprocess'], 'run', run)
    assert module['main']([]) == 124
    assert len(calls) == 4
    assert 'timed out' in capsys.readouterr().err


def test_recovery_rejects_arbitrary_commands(monkeypatch):
    module = recovery(monkeypatch)
    calls = []
    monkeypatch.setattr(module['subprocess'], 'run', lambda *a, **k: calls.append(a))
    with pytest.raises(SystemExit, match='Usage:'):
        module['main'](['--command', '/bin/sh'])
    assert calls == []


def test_materialized_live_diagnostics_match_reviewed_helper(tmp_path):
    prepare = runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare']
    upstream = tmp_path / 'upstream'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    prepare(upstream, output, ROOT, 'a' * 40)
    helper = output / 'airootfs/usr/local/bin/wilsof-live-recover'
    assert helper.read_bytes() == (ROOT / 'runtime/live-recover').read_bytes()
    assert helper.stat().st_mode & 0o777 == 0o755
    sudo = (output / 'airootfs/etc/sudoers.d/wilsof-live-installer').read_text()
    assert '/usr/local/bin/wilsof-live-recover ""' in sudo
    assert 'NOPASSWD: ALL' not in sudo


@pytest.mark.parametrize('args', [[], ['--restart'], ['--show-failure']])
def test_recovery_refuses_installed_system_before_any_command(monkeypatch, args):
    module = recovery(monkeypatch)
    monkeypatch.setattr(Path, 'is_mount', lambda self: False)
    calls = []
    monkeypatch.setattr(module['subprocess'], 'run', lambda *a, **k: calls.append(a))
    with pytest.raises(SystemExit, match='only in the running live environment'):
        module['main'](args)
    assert calls == []
