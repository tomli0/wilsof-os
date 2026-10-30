import json
from pathlib import Path
import runpy
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def seed(home):
    entry = home / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True)
    entry.write_text('-- existing generated base\n')
    runpy.run_path(str(ROOT / 'runtime/desktop.py'))['install_user'](ROOT, home)
    return json.loads((home / '.config/DankMaterialShell/settings.json').read_text())


def test_fresh_desktop_uses_supported_fit_and_curated_power_defaults(tmp_path):
    settings = seed(tmp_path)
    assert settings.get('wallpaperFillMode') == 'Fit'
    assert settings.get('powerMenuActions') == ['lock', 'suspend', 'logout', 'reboot', 'poweroff']
    assert settings.get('spotlightBarShowModeChips') is True
    assert settings.get('sortAppsAlphabetically') is True


def test_new_desktop_marks_only_current_dms_release_line_seen(tmp_path):
    seed(tmp_path)
    assert (tmp_path / '.config/dms/.changelog-2.0').read_text() == '2.0\n'
    assert not (tmp_path / '.config/dms/.changelog-2.1').exists()


def test_existing_personal_desktop_does_not_gain_changelog_marker(tmp_path):
    entry = tmp_path / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True)
    entry.write_text('-- base\n')
    settings = tmp_path / '.config/DankMaterialShell/settings.json'
    settings.parent.mkdir()
    settings.write_text('{"wallpaperFillMode":"Fill","personal":true}\n')
    runpy.run_path(str(ROOT / 'runtime/desktop.py'))['install_user'](ROOT, tmp_path)
    assert settings.read_text() == '{"wallpaperFillMode":"Fill","personal":true}\n'
    assert not (tmp_path / '.config/dms/.changelog-2.0').exists()


def test_only_identified_video_test_utilities_hidden_not_removed(tmp_path):
    seed(tmp_path)
    apps = tmp_path / '.local/share/applications'
    assert sorted(p.name for p in apps.glob('*.desktop')) == ['qv4l2.desktop', 'qvidcap.desktop']
    for name in ('qv4l2', 'qvidcap'):
        text = (apps / (name + '.desktop')).read_text()
        assert 'NoDisplay=true\n' in text
        assert f'Exec={name}\n' in text
    assert (tmp_path / '.local/bin/wilsof-hardware-report').read_bytes() == (ROOT / 'bin/wilsof-hardware-report').read_bytes()
    assert 'bin/wilsof-hardware-report' in (ROOT / 'runtime/image-files.txt').read_text().splitlines()


def test_profile_items_do_not_compete_with_empty_or_general_app_search():
    js = ROOT / 'config/dms/plugins/wilsofProfiles/Profiles.js'
    script = r'''
const vm=require('vm'),fs=require('fs'),assert=require('assert');const c={};vm.createContext(c);
vm.runInContext(fs.readFileSync(process.argv[1],'utf8').replace(/^\.pragma library\s*/,''),c);
for (const q of ['', 'p', 'file', 'firefox']) assert.equal(c.items(q,{}).length,0,q);
assert.equal(c.items('profil',{}).length,4);
assert.equal(c.items('profil study',{})[0].action,'study');
assert.equal(c.items('dev',{})[0].action,'development');
'''
    r = subprocess.run(['node', '-e', script, str(js)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_fit_projection_keeps_original_assets_centered_without_crop():
    # Geometry contract, not a substitute for rendered/physical acceptance.
    for name in ('Wilsof OS-logo med geometrisk WS-monogram.png',
                 'Mørk geometrisk bakgrunn med isblått WS-monogram.png'):
        data = (ROOT / 'assets' / name).read_bytes()
        w, h = struct.unpack('>II', data[16:24])
        for sw, sh in ((1920, 1080), (1920, 1200), (1500, 1000)):
            scale = min(sw / w, sh / h)
            x, y = (sw - w * scale) / 2, (sh - h * scale) / 2
            assert x >= -1e-9 and y >= -1e-9
            assert w * scale <= sw + 1e-9 and h * scale <= sh + 1e-9
