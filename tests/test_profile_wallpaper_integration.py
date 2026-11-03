"""Combined M1/M2/wallpaper deployment contract; no host desktop or disks."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def install(home, *, live=False):
    entry = home / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True, exist_ok=True)
    if not entry.exists():
        entry.write_text('-- disposable generated base\n')
    spec = importlib.util.spec_from_file_location('combined_desktop', ROOT / 'runtime/desktop.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.install_user(ROOT, home, live=live)


@pytest.mark.parametrize('live', [False, True])
@pytest.mark.parametrize('mask', [0o022, 0o002])
def test_combined_clean_default_and_wallpaper_recovery_are_deployed(tmp_path, live, mask):
    previous = os.umask(mask)
    try:
        install(tmp_path, live=live)
    finally:
        os.umask(previous)
    profile = tmp_path / '.local/state/wilsof-os/profile.json'
    assert not profile.exists(), 'deployment must not create or reset profile intent'
    cli = tmp_path / '.local/bin/wilsof-profile'
    result = subprocess.run([str(cli), 'get'], env=os.environ | {'HOME': str(tmp_path)},
                            capture_output=True, text=True, timeout=5)
    assert result.returncode == 0 and result.stdout == 'clean\n'
    choices = subprocess.run([str(cli), 'list'], capture_output=True, text=True, timeout=5)
    assert choices.returncode == 0
    assert choices.stdout.splitlines() == ['clean', 'study', 'development', 'everyday']
    dropin = tmp_path / '.config/systemd/user/dms.service.d/wilsof.conf'
    assert dropin.read_bytes() == (ROOT / 'config/systemd/dms-wilsof.conf').read_bytes()
    assert dropin.read_text().count('ExecStartPost=') == 1
    assert '--no-block start wilsof-wallpaper.service' in dropin.read_text()
    assert (tmp_path / '.config/dms/plugins/wilsofProfiles/ProfileState.qml').is_file()
    settings = json.loads((tmp_path / '.config/DankMaterialShell/settings.json').read_text())
    assert settings['barConfigs'][0]['leftWidgets'][0] == 'wilsofProfiles'
    assert (tmp_path / '.config/systemd/user/wilsof-session.target.wants/wilsof-wallpaper.service').is_symlink()


@pytest.mark.parametrize('raw', [b'{"schema_version":1,"profile":"study"}\n', b'{corrupt'])
def test_combined_config_update_preserves_profile_and_unmanaged_user_data(tmp_path, raw):
    install(tmp_path)
    profile = tmp_path / '.local/state/wilsof-os/profile.json'
    profile.write_bytes(raw)
    profile.chmod(0o600)
    user_data = tmp_path / 'Documents/unsaved-work-fixture.txt'
    user_data.parent.mkdir()
    user_data.write_bytes(b'user-owned contents\n')
    before = (profile.read_bytes(), profile.stat().st_mode, user_data.read_bytes())
    for _ in range(2):
        install(tmp_path)
        assert (profile.read_bytes(), profile.stat().st_mode, user_data.read_bytes()) == before
    assert (tmp_path / '.config/systemd/user/dms.service.d/wilsof.conf').read_bytes() == (
        ROOT / 'config/systemd/dms-wilsof.conf').read_bytes()
