"""Guard the 0.57 Lua-config boundary; live behavior is checked separately in QEMU."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_lua_window_shortcuts_do_not_execute_removed_legacy_dispatch_syntax():
    config = (ROOT / 'config/hypr/wilsof.lua').read_text()
    assert 'hl.dsp.exec_cmd("hyprctl dispatch ' not in config
    assert 'hl.dsp.window.fullscreen()' in config
    for direction in ('left', 'right', 'up', 'down'):
        assert f'hl.dsp.window.move({{ direction = "{direction}" }})' in config
    for x, y in ((-40, 0), (40, 0), (0, -40), (0, 40)):
        assert f'hl.dsp.window.resize({{ x = {x}, y = {y}, relative = true }})' in config
