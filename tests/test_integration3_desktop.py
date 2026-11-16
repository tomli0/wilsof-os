"""Upgrade/preservation regressions in dedicated disposable homes."""
import json
from pathlib import Path
import pytest
from test_desktop_runtime import load_runtime, ROOT


@pytest.mark.parametrize('original', [
    {'wilsofProfiles': {'enabled': True}},
    {'personal': {'enabled': False, 'sentinel': 'keep'}},
    {'wilsofProfiles': {'enabled': False}, 'wilsofCommandCenter': {'enabled': False}},
])
def test_upgrade_seeds_missing_plugins_preserving_explicit_states(tmp_path, original):
    entry = tmp_path / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True)
    entry.write_text('-- personal base\n')
    plugins = tmp_path / '.config/dms/plugin_settings.json'
    plugins.parent.mkdir(parents=True)
    plugins.write_text(json.dumps(original))
    load_runtime().install_user(ROOT, tmp_path)
    actual = json.loads(plugins.read_text())
    expected = {'wilsofCommandCenter': {'enabled': True}} | original
    if 'wilsofProfiles' in expected:
        expected['wilsofProfiles'] = dict(expected['wilsofProfiles'], enabled=False)
    assert actual == expected


def test_reset_refuses_collision_without_writing_either_file(tmp_path):
    from test_user_shortcuts import run_cli
    assert run_cli(tmp_path, 'set', 'command-center', 'ALT+F12').returncode == 0
    assert run_cli(tmp_path, 'set', 'lock', 'SUPER+space').returncode == 0
    files = [tmp_path / '.local/state/wilsof-os/user-shortcuts.json',
             tmp_path / '.config/hypr/wilsof-user-shortcuts.lua']
    before = [p.read_bytes() for p in files]
    result = run_cli(tmp_path, 'reset', 'command-center')
    assert result.returncode == 65, result.stderr
    assert [p.read_bytes() for p in files] == before
    assert run_cli(tmp_path, 'reset').returncode == 0


def test_appearance_reset_preserves_all_nonappearance_preferences(tmp_path):
    from test_appearance import seed_home, run_cli
    settings = seed_home(tmp_path)
    original = json.loads(settings.read_text()) | {
        'personalSentinel': {'keep': [1, 2]}, 'loginctlLockIntegration': False,
        'customPowerActionLock': '/personal/locker', 'powerMenuActions': ['logout'],
        'sortAppsAlphabetically': False, 'spotlightBarShowModeChips': False,
    }
    settings.write_text(json.dumps(original))
    assert run_cli(tmp_path, 'reset').returncode == 0
    actual = json.loads(settings.read_text())
    owned = {'currentThemeName', 'customThemeFile', 'wallpaperFillMode', 'barConfigs'}
    assert {k: v for k, v in actual.items() if k not in owned} == {k: v for k, v in original.items() if k not in owned}
    assert actual['currentThemeName'] == 'custom'


def test_reapply_repairs_only_owned_regular_helper_mode(tmp_path):
    import os
    entry = tmp_path / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True)
    entry.write_text('-- generated base\n')
    runtime = load_runtime()
    runtime.install_user(ROOT, tmp_path)
    helper = tmp_path / '.local/bin/wilsof-search'
    helper.chmod(0o644)
    personal = tmp_path / '.config/ghostty/config'
    personal.write_text('# personal\n')
    personal.chmod(0o600)
    runtime.install_user(ROOT, tmp_path)
    assert os.stat(helper).st_mode & 0o777 == 0o755
    assert os.stat(personal).st_mode & 0o777 == 0o600
    assert personal.read_text() == '# personal\n'
