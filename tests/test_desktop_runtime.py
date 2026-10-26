import importlib.util
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def load_runtime():
    path = ROOT / "runtime/desktop.py"
    assert path.is_file(), "The offline desktop provisioning runtime is missing"
    spec = importlib.util.spec_from_file_location("wilsof_desktop", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_provision_target_rejects_root_and_symlink_writes_before_mutation(tmp_path):
    import runpy
    import pytest
    validate = runpy.run_path(str(ROOT / 'runtime/provision-target'))['validate_target']
    with pytest.raises(ValueError, match='running system'):
        validate(Path('/'), 'demo', False)
    target = tmp_path / 'target'
    (target / 'etc').mkdir(parents=True)
    (target / 'etc/os-release').write_text('ID=arch\n')
    (target / 'etc/passwd').write_text('demo:x:1000:1000::/home/demo:/bin/bash\n')
    (target / 'home/demo').mkdir(parents=True)
    external = tmp_path / 'outside'
    external.mkdir()
    (target / 'usr').symlink_to(external, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        validate(target, 'demo', False)
    (target / 'usr').unlink()
    (target / 'usr/local/bin').mkdir(parents=True)
    victim = external / 'victim'
    victim.write_text('must remain unchanged')
    (target / 'usr/local/bin/wilsof-config-update').symlink_to(victim)
    with pytest.raises(ValueError, match='symlink'):
        validate(target, 'demo', False)
    assert victim.read_text() == 'must remain unchanged'


def test_live_configuration_updates_keep_all_lock_paths_harmless(tmp_path):
    desktop = load_runtime()
    home = tmp_path / 'home'
    entry = home / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True)
    entry.write_text('-- generated base\n')
    desktop.install_user(ROOT, home, live=True)
    desktop.install_user(ROOT, home)
    settings = json.loads((home / '.config/DankMaterialShell/settings.json').read_text())
    assert settings['customPowerActionLock'] == str(home / '.local/bin/wilsof-lock')
    assert settings['loginctlLockIntegration'] is False
    assert settings['lockBeforeSuspend'] is False
    assert 'hyprlock' not in (home / '.local/bin/wilsof-lock').read_text()
    assert not (home / '.config/systemd/user/graphical-session.target.wants/hypridle.service').is_symlink()


def test_new_desktop_resolves_theme_placeholder(tmp_path):
    desktop = load_runtime()
    entry = tmp_path / '.config/hypr/hyprland.lua'
    entry.parent.mkdir(parents=True)
    entry.write_text('-- base\n')
    desktop.install_user(ROOT, tmp_path)
    settings = json.loads((tmp_path / '.config/DankMaterialShell/settings.json').read_text())
    assert settings['customThemeFile'] == str(tmp_path / '.local/share/wilsof-os/wilsof-theme.json')


def test_desktop_startup_has_bounded_slow_vm_allowance():
    assert 'TimeoutStartSec=300' in (ROOT / 'config/systemd/dms-wilsof.conf').read_text()


def test_desktop_provisioning_preserves_personal_settings_and_backs_up_managed_files(tmp_path):
    desktop = load_runtime()
    home = tmp_path / "home"
    entry = home / ".config/hypr/hyprland.lua"
    entry.parent.mkdir(parents=True)
    entry.write_text('-- personal base\n')
    settings = home / ".config/DankMaterialShell/settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text('{"personal":true}\n')
    desktop.install_user(ROOT, home)
    assert settings.read_text() == '{"personal":true}\n'
    assert entry.read_text().count('require("wilsof")') == 1
    managed = home / ".config/hypr/wilsof.lua"
    managed.write_text('-- old managed file\n')
    desktop.install_user(ROOT, home)
    assert entry.read_text().count('require("wilsof")') == 1
    assert any(p.read_text() == '-- old managed file\n' for p in (home / '.local/state/wilsof-os/backups').rglob('wilsof.lua'))
    assert managed.read_bytes() == (ROOT / 'config/hypr/wilsof.lua').read_bytes()
