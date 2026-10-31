"""The native lifecycle observer must never see a truncated counter file."""
from pathlib import Path
import runpy
import subprocess
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('script,counter', [('daemon.py', 'dms.count'), ('wallpaper.py', 'wallpaper.count')])
def test_native_fixture_publishes_counter_atomically(tmp_path, monkeypatch, script, counter):
    api = runpy.run_path(str(ROOT / 'tests/integration/wallpaper_lifecycle.py'))
    lifecycle = api['Lifecycle']()
    namespace = lifecycle.prepare.__globals__
    monkeypatch.setitem(namespace, 'SOURCE', ROOT)
    monkeypatch.setitem(namespace, 'EVIDENCE', tmp_path / 'evidence')
    monkeypatch.setitem(namespace, 'run', lambda *a, **k: subprocess.CompletedProcess(a, 0, '', ''))
    home = tmp_path / 'home'
    home.mkdir()
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: home))
    lifecycle.setUp()
    lifecycle.prepare(fail_first=False)
    target = lifecycle.case / counter
    target.write_text('1')
    original_write = Path.write_text

    def checked_write(path, data, *args, **kwargs):
        assert path != target, 'in-place counter write exposes an empty file to count()'
        return original_write(path, data, *args, **kwargs)

    monkeypatch.setattr(Path, 'write_text', checked_write)
    # Stop the daemon at its first sleep after publication; no real unit/notify.
    def stop(_):
        raise StopIteration('counter published')
    monkeypatch.setattr(time, 'sleep', stop)
    if script == 'daemon.py':
        with pytest.raises(StopIteration, match='counter published'):
            runpy.run_path(str(lifecycle.case / script))
    else:
        with pytest.raises(SystemExit) as result:
            runpy.run_path(str(lifecycle.case / script))
        assert result.value.code == 0
    assert target.read_text() == '2'
