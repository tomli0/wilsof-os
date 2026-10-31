from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_application_shortcuts_are_explicit_and_personally_overridable():
    path = ROOT / 'config/hypr/wilsof-app-shortcuts.lua'
    assert path.exists(), 'Browser/Files shortcuts missing'
    text = path.read_text()
    assert 'hl.unbind("SUPER + B")' in text
    assert 'hl.unbind("SUPER + E")' in text
    assert 'hl.bind("SUPER + B", hl.dsp.exec_cmd("firefox"))' in text
    assert 'hl.bind("SUPER + E", hl.dsp.exec_cmd("nautilus"))' in text
    assert 'Return' not in text  # DMS already owns Super+Enter -> Ghostty.
    assert 'require("wilsof-app-shortcuts")' in (ROOT / 'config/hypr/wilsof.lua').read_text()
    assert "confined('.config/hypr/wilsof-app-shortcuts.lua')" in (ROOT / 'runtime/desktop.py').read_text()
