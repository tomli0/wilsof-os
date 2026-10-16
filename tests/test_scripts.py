import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEARCH = ROOT / "bin" / "wilsof-search"
LOCK = ROOT / "bin" / "wilsof-lock"
PREFLIGHT = ROOT / "scripts" / "preflight-fedora.sh"
ARCH_PREFLIGHT = ROOT / "scripts" / "preflight-arch.sh"
INSTALL = ROOT / "scripts" / "install-user-config.sh"
WALLPAPER_UNIT = ROOT / "config" / "systemd" / "wilsof-wallpaper.service"


def run(script, *args, env=None):
    variables = os.environ | (env or {})
    return subprocess.run(
        [str(script), *args], text=True, capture_output=True, env=variables, check=False
    )


def test_search_delegates_to_documented_dms_spotlight_api(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "args"
    dms = fake_bin / "dms"
    dms.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" > {log}\n", encoding="utf-8")
    dms.chmod(0o755)
    result = run(SEARCH, "toggle", env={"PATH": f"{fake_bin}:{os.environ['PATH']}"})
    assert result.returncode == 0, result.stderr
    assert log.read_text(encoding="utf-8").strip() == "ipc call spotlight toggle"


def test_search_rejects_unsupported_actions():
    result = run(SEARCH, "anything-else")
    assert result.returncode == 64
    assert "Usage" in result.stderr


def test_lock_delegates_to_hyprlock_and_rejects_arguments(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "args"
    hyprlock = fake_bin / "hyprlock"
    hyprlock.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" > {log}\n", encoding="utf-8")
    hyprlock.chmod(0o755)
    pgrep = fake_bin / "pgrep"
    pgrep.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    pgrep.chmod(0o755)
    result = run(LOCK, env={"PATH": f"{fake_bin}:{os.environ['PATH']}"})
    assert result.returncode == 0, result.stderr
    assert log.read_text(encoding="utf-8").strip() == ""
    rejected = run(LOCK, "unexpected")
    assert rejected.returncode == 64


def test_preflight_is_read_only_and_reports_missing_fedora_tools():
    result = run(PREFLIGHT)
    assert result.returncode != 0
    assert "Fedora" in result.stderr


def test_arch_preflight_is_read_only_and_rejects_non_arch_hosts():
    result = run(ARCH_PREFLIGHT)
    assert result.returncode != 0
    assert "Arch" in result.stderr


def test_installer_requires_explicit_target_vm_guard():
    result = run(INSTALL)
    assert result.returncode == 64
    assert "WILSOF_TARGET_VM=1" in result.stderr


def test_installer_selects_arch_or_fedora_preflight_explicitly():
    content = INSTALL.read_text(encoding="utf-8")
    assert 'fedora) "$root/scripts/preflight-fedora.sh"' in content
    assert 'arch) "$root/scripts/preflight-arch.sh"' in content


def test_wallpaper_unit_quotes_asset_path_with_spaces():
    content = WALLPAPER_UNIT.read_text(encoding="utf-8")
    assert '"%h/.local/share/wilsof-os/assets/Mørk geometrisk bakgrunn med isblått WS-monogram.png"' in content


def test_installer_integrates_with_the_dms_lua_entrypoint_and_locking():
    content = INSTALL.read_text(encoding="utf-8")
    assert 'config/hypr/wilsof.lua' in content
    assert 'config/hypr/hypridle.conf' in content
    assert 'bin/wilsof-lock' in content
    assert 'bin/wilsof-help' in content
    assert 'require("wilsof")' in content
    assert 'systemctl --user enable dms.service hypridle.service' in content


def test_installer_seeds_static_dms_theme_only_once():
    content = INSTALL.read_text(encoding="utf-8")
    assert 'config/dms/wilsof-theme.json' in content
    assert 'config/dms/settings-template.json' in content
    assert 'dms.service.d/wilsof.conf' in content
    assert 'dms-defaults-v1' in content
    assert 'if [ ! -e "$settings" ]' in content


def test_static_theme_defines_the_approved_base_and_accent():
    theme = (ROOT / "config" / "dms" / "wilsof-theme.json").read_text(encoding="utf-8")
    assert '"primary": "#86B9CE"' in theme
    assert '"surface": "#14181E"' in theme
    assert '"background": "#14181E"' in theme


def test_help_wrapper_delegates_to_the_supported_dms_keybind_view(tmp_path):
    helper = ROOT / "bin" / "wilsof-help"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "args"
    dms = fake_bin / "dms"
    dms.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" > {log}\n", encoding="utf-8")
    dms.chmod(0o755)
    result = run(helper, env={"PATH": f"{fake_bin}:{os.environ['PATH']}"})
    assert result.returncode == 0, result.stderr
    assert log.read_text(encoding="utf-8").strip() == "ipc call keybinds open"
