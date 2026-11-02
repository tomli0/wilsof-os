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
    assert actual == {'wilsofProfiles': {'enabled': True}, 'wilsofCommandCenter': {'enabled': True}} | original
