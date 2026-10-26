import runpy
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def test_wallpaper_waits_for_ipc_target_and_verifies_applied_path(tmp_path):
    script = ROOT / 'bin/wilsof-apply-wallpaper'
    assert script.is_file(), 'Wallpaper readiness handler is missing'
    apply = runpy.run_path(str(script))['apply_wallpaper']
    image = tmp_path / 'wallpaper.png'
    image.write_bytes(b'fixture')
    replies = iter(['Target not found.\n', f'SUCCESS: Wallpaper set to {image}\n', str(image) + '\n'])
    calls = []
    def run(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stdout=next(replies))
    apply(image, run=run, wait=lambda _: None)
    assert [call[4] for call in calls] == ['set', 'set', 'get']
