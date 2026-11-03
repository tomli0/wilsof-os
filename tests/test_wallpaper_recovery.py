import os
from pathlib import Path
import runpy
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_post_ready_hook_is_nonblocking_failure_isolated_and_has_no_restart_loop():
    dropin = (ROOT / 'config/systemd/dms-wilsof.conf').read_text()
    assert dropin.count('ExecStartPost=') == 1
    assert 'ExecStartPost=-/usr/bin/systemctl --user --no-block start wilsof-wallpaper.service' in dropin
    assert 'Restart=' not in dropin
    unit = (ROOT / 'config/systemd/wilsof-wallpaper.service').read_text()
    assert 'After=dms.service' in unit and 'Requires=dms.service' in unit
    assert 'Restart=' not in unit


@pytest.mark.parametrize('fault', ('target-missing', 'set-failed', 'get-mismatch', 'timeout'))
def test_ipc_failure_is_bounded_and_never_falsely_confirmed(tmp_path, monkeypatch, fault):
    apply = runpy.run_path(str(ROOT / 'bin/wilsof-apply-wallpaper'))['apply_wallpaper']
    image = tmp_path / 'approved.png'
    image.write_bytes(b'fixture')
    clock = [0]
    calls = []
    monkeypatch.setitem(apply.__globals__, 'time', SimpleNamespace(monotonic=lambda: clock[0]))

    def wait(seconds):
        clock[0] += seconds

    def ipc(argv, **kwargs):
        calls.append(argv)
        assert kwargs['timeout'] == 5
        if fault == 'timeout':
            raise subprocess.TimeoutExpired(argv, 5)
        if fault == 'target-missing':
            return SimpleNamespace(returncode=0, stdout='Target not found.\n')
        if fault == 'set-failed':
            return SimpleNamespace(returncode=1, stdout='failed')
        return SimpleNamespace(returncode=0, stdout=(f'SUCCESS: Wallpaper set to {image}\n'
                                                     if argv[4] == 'set' else '/different/image.png\n'))

    with pytest.raises(RuntimeError, match='did not confirm'):
        apply(image, run=ipc, wait=wait, timeout=2)
    assert clock[0] == 2
    assert len(calls) == (4 if fault == 'get-mismatch' else 2)


def test_missing_asset_and_binary_propagate_without_retry(tmp_path):
    apply = runpy.run_path(str(ROOT / 'bin/wilsof-apply-wallpaper'))['apply_wallpaper']
    def unavailable(*args, **kwargs):
        raise FileNotFoundError('dms not installed')
    with pytest.raises(RuntimeError, match='wallpaper is missing'):
        apply(tmp_path / 'absent', run=unavailable)
    image = tmp_path / 'image'
    image.write_bytes(b'fixture')
    with pytest.raises(FileNotFoundError, match='dms not installed'):
        apply(image, run=unavailable)


@pytest.mark.skipif(os.environ.get('WILSOF_SYSTEMD_LIFECYCLE_TEST') != '1',
                    reason='opt-in disposable QEMU user-manager lifecycle; not a CI mock')
def test_native_systemd_lifecycle():
    result = subprocess.run([sys.executable, str(ROOT / 'tests/integration/wallpaper_lifecycle.py'),
                             '--source', str(ROOT), '--evidence',
                             str(Path.home() / '.local/state/wilsof-wallpaper-lifecycle')],
                            capture_output=True, text=True, timeout=240)
    assert result.returncode == 0, result.stdout + result.stderr
