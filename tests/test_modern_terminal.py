import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def runtime():
    spec = importlib.util.spec_from_file_location('modern_desktop', ROOT / 'runtime/desktop.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_modern_terminal_palette_and_native_ghostty_keys():
    config = ROOT / 'config/ghostty/config'
    assert config.exists(), 'Modern Terminal Ghostty configuration missing'
    text = config.read_text()
    for value in ['background = #121820', 'foreground = #E7EEF2', 'cursor-color = #86B9CE', 'window-padding-x = 12', 'window-padding-y = 10', 'new_split:right', 'new_split:down', 'copy_to_clipboard', 'paste_from_clipboard', 'increase_font_size', 'decrease_font_size', 'reset_font_size', 'clipboard-paste-protection = true']:
        assert value in text
    assert sum(line.startswith('palette = ') for line in text.splitlines()) == 16
    theme = json.loads((ROOT / 'config/dms/wilsof-theme.json').read_text())['dark']
    assert theme['surface'] == theme['background'] == '#121820'
    assert theme['primary'] == '#86B9CE'
    assert 'config/ghostty/config' in (ROOT / 'runtime/image-files.txt').read_text().splitlines()


def test_seed_ghostty_once_without_overwriting_manual_user_config(tmp_path):
    entry = tmp_path / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True)
    entry.write_text('-- base\n')
    runtime().install_user(ROOT, tmp_path)
    dest = tmp_path / '.config/ghostty/config'
    assert dest.exists(), 'Ghostty configuration not deployed'
    assert dest.read_bytes() == (ROOT / 'config/ghostty/config').read_bytes()
    personal = b'font-size = 18\n# personal preference\n'
    dest.write_bytes(personal)
    runtime().install_user(ROOT, tmp_path)
    assert dest.read_bytes() == personal
