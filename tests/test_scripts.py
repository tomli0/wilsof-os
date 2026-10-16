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


def test_arch_preflight_checks_the_apps_required_by_wilsof_flows():
    content = ARCH_PREFLIGHT.read_text(encoding="utf-8")
    for package in ("ghostty", "firefox", "nautilus", "gnome-text-editor", "papers", "loupe", "vlc"):
        assert package in content


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


def test_vm_test_binding_wrapper_is_opt_in_and_reversible(tmp_path):
    wrapper = ROOT / "bin" / "wilsof-vm-test-binds"
    source = tmp_path / ".local" / "share" / "wilsof-os" / "vm-test"
    source.mkdir(parents=True)
    (source / "wilsof-vm-test.lua").write_text("-- test\n", encoding="utf-8")
    env = {"HOME": str(tmp_path), "PATH": os.environ["PATH"]}
    assert run(wrapper, "status", env=env).stdout.strip() == "disabled"
    assert run(wrapper, "enable", env=env).returncode == 0
    assert run(wrapper, "status", env=env).stdout.strip() == "enabled"
    assert run(wrapper, "disable", env=env).returncode == 0
    assert run(wrapper, "status", env=env).stdout.strip() == "disabled"


def test_vm_test_lua_has_only_the_four_requested_ctrl_alt_bindings():
    config = (ROOT / "config" / "hypr" / "wilsof-vm-test.lua").read_text(encoding="utf-8")
    for key in ("space", "L", "I", "F1"):
        assert f'"CTRL + ALT + {key}"' in config
    assert config.count("hl.bind(") == 4


def test_help_opens_a_keyboard_closable_local_view_from_the_shared_manifest(tmp_path):
    helper = ROOT / "bin" / "wilsof-help"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "args"
    ghostty = fake_bin / "ghostty"
    ghostty.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" > {log}\n", encoding="utf-8")
    ghostty.chmod(0o755)
    manifest = tmp_path / "shortcuts.json"
    manifest.write_text('{"schema": 1, "standard": [], "vm_test": []}\n', encoding="utf-8")
    renderer = tmp_path / "wilsof-help-view"
    renderer.write_text("#!/bin/sh\n", encoding="utf-8")
    renderer.chmod(0o755)
    result = run(
        helper,
        env={
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "WILSOF_SHORTCUTS_FILE": str(manifest),
            "WILSOF_HELP_VIEWER": str(renderer),
        },
    )
    assert result.returncode == 0, result.stderr
    assert log.read_text(encoding="utf-8").strip() == f"--title=Wilsof snarveier --command {renderer} {manifest}"


def test_help_viewer_renders_standard_and_enabled_vm_test_bindings(tmp_path):
    viewer = ROOT / "bin" / "wilsof-help-view"
    manifest = tmp_path / "shortcuts.json"
    manifest.write_text(
        """{
  "schema": 1,
  "standard": [{"keys": "Super+Space", "action": "Launcher"}],
  "vm_test": [{"keys": "Ctrl+Alt+Space", "action": "Launcher"}]
}
""",
        encoding="utf-8",
    )
    disabled = run(viewer, str(manifest), env={"WILSOF_VM_TEST_BINDS": "disabled"})
    assert disabled.returncode == 0, disabled.stderr
    assert "Super (Command/Windows)" in disabled.stdout
    assert "Super+Space" in disabled.stdout
    assert "VM-testbindinger er ikke aktivert" in disabled.stdout
    enabled = run(viewer, str(manifest), env={"WILSOF_VM_TEST_BINDS": "enabled"})
    assert enabled.returncode == 0, enabled.stderr
    assert "Valgfrie VM-testbindinger (aktive)" in enabled.stdout
    assert "Ctrl+Alt+Space" in enabled.stdout


def test_help_viewer_rejects_malformed_manifest(tmp_path):
    viewer = ROOT / "bin" / "wilsof-help-view"
    manifest = tmp_path / "broken.json"
    manifest.write_text("not-json\n", encoding="utf-8")
    result = run(viewer, str(manifest))
    assert result.returncode == 65
    assert "invalid shortcut manifest" in result.stderr


def test_lock_is_idempotent_only_for_the_current_user(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    hyprlock = fake_bin / "hyprlock"
    hyprlock.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hyprlock.chmod(0o755)
    pgrep = fake_bin / "pgrep"
    pgrep.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\"\nexit 0\n", encoding="utf-8")
    pgrep.chmod(0o755)
    result = run(LOCK, env={"PATH": f"{fake_bin}:{os.environ['PATH']}"})
    assert result.returncode == 0
    assert "already active" in result.stderr


def test_installer_deploys_the_help_viewer_and_shared_shortcut_manifest():
    content = INSTALL.read_text(encoding="utf-8")
    assert 'bin/wilsof-help-view' in content
    assert 'config/wilsof-shortcuts.json' in content


def test_installer_backs_up_replaced_wilsof_managed_files_before_installing():
    content = INSTALL.read_text(encoding="utf-8")
    assert 'backup_managed()' in content
    assert '"$HOME/.config/hypr/wilsof.lua"' in content
    assert '"$HOME/.local/bin/wilsof-help"' in content
    assert '"$HOME/.local/state/wilsof-os/backups"' in content


def test_shared_shortcut_manifest_covers_all_wilsof_action_bindings():
    import json

    manifest = json.loads((ROOT / "config" / "wilsof-shortcuts.json").read_text(encoding="utf-8"))
    standard = {row["keys"] for row in manifest["standard"]}
    vm_test = {row["keys"] for row in manifest["vm_test"]}
    for keys in (
        "Super+Space", "Super+L", "Super+I", "Super+F1", "Super+Q", "Super+F", "Super+Shift+Space",
    ):
        assert keys in standard
    for keys in ("Ctrl+Alt+Space", "Ctrl+Alt+L", "Ctrl+Alt+I", "Ctrl+Alt+F1"):
        assert keys in vm_test
