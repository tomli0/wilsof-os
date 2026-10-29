"""Distribution goes through the existing explicit image manifest."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def runtime():
    spec = importlib.util.spec_from_file_location('desktop_m2', ROOT / 'runtime/desktop.py')
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_new_home_installs_all_plugin_inputs_and_enables_default_bar(tmp_path):
    entry = tmp_path / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True)
    entry.write_text('-- base\n')
    runtime().install_user(ROOT, tmp_path)
    for name in ('wilsof-profile', 'wilsof-profile-ui'):
        installed = tmp_path / '.local/bin' / name
        assert installed.is_file(), 'M2 helper not distributed'
        assert installed.read_bytes() == (ROOT / 'bin' / name).read_bytes()
        assert installed.stat().st_mode & 0o777 == 0o755
    source = ROOT / 'config/dms/plugins/wilsofProfiles'
    for file in source.iterdir():
        installed = tmp_path / '.config/dms/plugins/wilsofProfiles' / file.name
        assert installed.read_bytes() == file.read_bytes()
    settings = json.loads((tmp_path / '.config/DankMaterialShell/settings.json').read_text())
    assert settings['barConfigs'][0]['leftWidgets'][0] == 'wilsofProfiles'
    assert json.loads((tmp_path / '.config/dms/plugin_settings.json').read_text())['wilsofProfiles']['enabled'] is True
    manifest = (ROOT / 'runtime/image-files.txt').read_text().splitlines()
    assert len(manifest) == len(set(manifest))
    assert 'bin/wilsof-profile' in manifest and 'bin/wilsof-profile-ui' in manifest
    assert all(str(f.relative_to(ROOT)) in manifest for f in source.iterdir())


def test_personal_settings_and_explicit_plugin_disable_survive(tmp_path):
    entry = tmp_path / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True)
    entry.write_text('-- base\n')
    settings = tmp_path / '.config/dms/settings.json'
    settings.parent.mkdir()
    original = b'{"barConfigs":[],"personal":"kept"}\n'
    settings.write_bytes(original)
    (tmp_path / '.config/DankMaterialShell').symlink_to('dms')
    plugins = tmp_path / '.config/dms/plugin_settings.json'
    plugins.write_text('{"other":{"enabled":true},"wilsofProfiles":{"enabled":false}}\n')
    plugin_bytes = plugins.read_bytes()
    for _ in range(2):
        runtime().install_user(ROOT, tmp_path)
        assert settings.read_bytes() == original
        assert plugins.read_bytes() == plugin_bytes


def test_plugin_settings_corruption_and_symlinks_are_not_repaired(tmp_path):
    import pytest
    for kind in ('corrupt', 'non-object', 'linked-file', 'linked-directory'):
        home = tmp_path / kind
        entry = home / '.config/hypr/hyprland.lua'
        entry.parent.mkdir(parents=True)
        entry.write_text('-- base\n')
        outside = tmp_path / (kind + '-outside')
        outside.mkdir()
        victim = outside / 'plugin_settings.json'
        victim.write_text('{"unchanged":true}\n')
        p = home / '.config/dms/plugin_settings.json'
        if kind == 'linked-directory':
            p.parent.symlink_to(outside)
        else:
            p.parent.mkdir()
            if kind == 'linked-file':
                p.symlink_to(victim)
            else:
                p.write_text('{broken' if kind == 'corrupt' else '[]')
        before = p.read_bytes()
        with pytest.raises((ValueError, RuntimeError)):
            runtime().install_user(ROOT, home)
        assert p.read_bytes() == before
        assert victim.read_text() == '{"unchanged":true}\n'
