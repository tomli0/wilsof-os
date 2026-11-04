import os
import shlex
import subprocess
from pathlib import Path

import pytest


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


def test_search_delegates_to_the_single_dms_launcher_api(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "args"
    dms = fake_bin / "dms"
    dms.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" > {log}\n", encoding="utf-8")
    dms.chmod(0o755)
    result = run(SEARCH, "toggle", env={"PATH": f"{fake_bin}:{os.environ['PATH']}"})
    assert result.returncode == 0, result.stderr
    assert log.read_text(encoding="utf-8").strip() == "ipc call spotlight toggle"


def test_search_uses_command_center_marker_without_double_toggling(tmp_path):
    fake_bin = tmp_path / 'bin'
    fake_bin.mkdir()
    log = tmp_path / 'calls'
    dms = fake_bin / 'dms'
    dms.write_text(f'#!/bin/sh\nprintf "%s\\n" "$*" >> "{log}"\nprintf "%s\\n" WILSOF_COMMAND_CENTER_OK\n')
    dms.chmod(0o755)
    result = run(SEARCH, 'toggle', env={'PATH': f"{fake_bin}:{os.environ['PATH']}"})
    assert result.returncode == 0
    assert log.read_text().splitlines() == ['ipc call commandCenter toggle']


def test_search_treats_locked_session_marker_as_handled(tmp_path):
    # While the session is locked the Command Center answers with a distinct
    # marker; the wrapper must treat it as handled and never fall back to the
    # upstream launcher, which would reopen a keyboard-grabbing modal.
    fake_bin = tmp_path / 'bin'
    fake_bin.mkdir()
    log = tmp_path / 'calls'
    dms = fake_bin / 'dms'
    dms.write_text(f'#!/bin/sh\nprintf "%s\\n" "$*" >> "{log}"\nprintf "%s\\n" WILSOF_COMMAND_CENTER_LOCKED\n')
    dms.chmod(0o755)
    result = run(SEARCH, 'toggle', env={'PATH': f"{fake_bin}:{os.environ['PATH']}"})
    assert result.returncode == 0
    assert log.read_text().splitlines() == ['ipc call commandCenter toggle']


def test_search_rejects_unsupported_actions():
    result = run(SEARCH, "anything-else")
    assert result.returncode == 64
    assert "Usage" in result.stderr


def test_lock_wrappers_delegate_to_one_lifecycle_and_reject_arguments():
    for name, action in [('wilsof-lock', 'lock'), ('wilsof-idle', 'idle')]:
        script = ROOT / 'bin' / name
        source = script.read_text()
        assert '/wilsof-lock-session" ' + action in source
        assert 'unlock-session' not in source
        assert run(script, 'unexpected').returncode == 64


def test_unverified_unlock_bridge_is_withheld_fail_closed():
    source = (ROOT / 'bin/wilsof-lock-session').read_text()
    assert 'unlock-session' not in source
    assert 'SetLockedHint' not in source
    assert 'pgrep' not in source
    assert 'pass_fds=(fd,)' in source


def test_idle_policy_defines_three_tiers_with_dpms_and_secure_relock():
    hypridle = (ROOT / "config" / "hypr" / "hypridle.conf").read_text(encoding="utf-8")
    assert "timeout = 180" in hypridle
    assert "wilsof-idle" in hypridle
    assert "timeout = 300" in hypridle
    assert "wilsof-lock" in hypridle
    assert "timeout = 600" in hypridle
    assert "dpms off" in hypridle
    assert "dpms on" in hypridle
    assert "before_sleep_cmd" in hypridle


def test_idle_presentation_matches_the_approved_terminal_idle_design():
    conf = (ROOT / "config" / "hypr" / "hyprlock-idle.conf").read_text(encoding="utf-8")
    assert "rgb(9, 15, 20)" in conf
    assert "[ W S ]" in conf
    assert "SYSTEM IDLE_" in conf
    assert "enabled = false" in conf
    # It must remain a real Hyprlock PAM surface with an input field.
    assert "input-field" in conf


def test_installer_deploys_the_idle_tier_files():
    content = INSTALL.read_text(encoding="utf-8")
    assert 'bin/wilsof-idle' in content
    assert 'config/hypr/hyprlock-idle.conf' in content
    assert '"$HOME/.config/hypr/hyprlock-idle.conf"' in content


def test_preflight_is_read_only_and_reports_missing_fedora_tools():
    result = run(PREFLIGHT)
    assert result.returncode != 0
    assert "Fedora" in result.stderr


@pytest.fixture
def arch_preflight_host(tmp_path):
    # Redirect only the OS-file boundary in a disposable copy. Production keeps
    # its fixed /etc/os-release path: no runtime override or weakened OS guard.
    release = tmp_path / 'os release'
    script = tmp_path / 'preflight-arch.sh'
    source = ARCH_PREFLIGHT.read_text(encoding='utf-8')
    check = '[ ! -r /etc/os-release ]'
    load = '. /etc/os-release\n'
    assert source.count(check) == source.count(load) == 1
    source = source.replace(check, f'[ ! -r {shlex.quote(str(release))} ]')
    script.write_text(source.replace(load, f'. {shlex.quote(str(release))}\n'))
    script.chmod(0o755)
    fake_bin = tmp_path / 'bin'
    fake_bin.mkdir()
    log = tmp_path / 'commands'
    for command in ('systemctl', 'pacman', 'hyprctl', 'dms', 'loginctl'):
        stub = fake_bin / command
        stub.write_text(
            f'#!/bin/sh\nprintf "%s\\n" "{command} $*" >> {shlex.quote(str(log))}\n'
        )
        stub.chmod(0o755)
    return script, release, log, {'PATH': str(fake_bin)}


@pytest.mark.parametrize('release_text,found', [
    ('ID=fedora\n', 'fedora'),
    ('ID=ubuntu\nID_LIKE=arch\n', 'ubuntu'),
    ('ID=archlinux\n', 'archlinux'),
    ('NAME=Unknown\n', 'unknown'),
])
def test_arch_preflight_is_read_only_and_rejects_non_arch_hosts(
    arch_preflight_host, release_text, found
):
    script, release, log, env = arch_preflight_host
    release.write_text(release_text)
    result = run(script, env=env)
    assert result.returncode == 1
    assert result.stderr == f'Arch preflight: target must be Arch Linux; found {found}.\n'
    assert result.stdout == ''
    assert not log.exists(), 'Non-Arch hosts must be rejected before tool/package probes'
    assert release.read_text() == release_text


def test_arch_preflight_accepts_arch_fixture_without_writing_host_state(arch_preflight_host):
    script, release, log, env = arch_preflight_host
    release.write_text('ID=arch\n')
    result = run(script, env=env)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ''
    assert 'PASS package: hyprland\n' in result.stdout
    assert 'PASS user systemd session\n' in result.stdout
    calls = log.read_text().splitlines()
    assert calls[-1] == 'systemctl --user show-environment'
    assert all(call.startswith('pacman -Q ') for call in calls[:-1])
    assert release.read_text() == 'ID=arch\n'


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


def test_wallpaper_unit_requires_dms_and_uses_argument_safe_readiness_helper():
    content = WALLPAPER_UNIT.read_text(encoding="utf-8")
    assert "Requires=dms.service" in content
    assert "After=dms.service" in content
    assert 'ExecStart=%h/.local/bin/wilsof-apply-wallpaper' in content
    helper = (ROOT / 'bin/wilsof-apply-wallpaper').read_text()
    assert "['dms', 'ipc', 'call', 'wallpaper', 'set', str(image)]" in helper
    assert 'Mørk geometrisk bakgrunn med isblått WS-monogram.png' in helper


def test_installer_integrates_with_the_dms_lua_entrypoint_and_locking():
    content = INSTALL.read_text(encoding="utf-8")
    assert 'config/hypr/wilsof.lua' in content
    assert 'config/hypr/hypridle.conf' in content
    assert 'config/hypr/hyprlock.conf' in content
    assert 'bin/wilsof-lock' in content
    assert 'bin/wilsof-help' in content
    assert 'require("wilsof")' in content
    assert 'systemctl --user enable dms.service hypridle.service' in content
    assert 'assets/Wilsof OS-logo med geometrisk WS-monogram.png' in content


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
    assert '"surface": "#121820"' in theme
    assert '"background": "#121820"' in theme


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


def test_help_renders_the_shared_manifest_in_dms_notepad(tmp_path):
    helper = ROOT / "bin" / "wilsof-help"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "args"
    dms = fake_bin / "dms"
    dms.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" > {log}\n", encoding="utf-8")
    dms.chmod(0o755)
    manifest = tmp_path / "shortcuts.json"
    manifest.write_text('{"schema": 1, "standard": [], "vm_test": []}\n', encoding="utf-8")
    renderer = tmp_path / "wilsof-help-view"
    renderer.write_text("#!/bin/sh\nprintf '%s\\n' 'Wilsof snarveier'\n", encoding="utf-8")
    renderer.chmod(0o755)
    document = tmp_path / "state" / "Wilsof snarveier.txt"
    result = run(
        helper,
        env={
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "WILSOF_SHORTCUTS_FILE": str(manifest),
            "WILSOF_HELP_VIEWER": str(renderer),
            "WILSOF_HELP_DOCUMENT": str(document),
        },
    )
    assert result.returncode == 0, result.stderr
    assert log.read_text(encoding="utf-8").strip() == f"ipc call notepad openFile {document}"
    assert document.read_text(encoding="utf-8").strip() == "Wilsof snarveier"


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
    assert "Super er Command-tasten" in disabled.stdout
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


def test_lock_guard_is_session_scoped_not_uid_wide():
    source = (ROOT / 'bin/wilsof-lock-session').read_text()
    assert 'GetSessionByPID' in source
    assert 'LOCK_EX | fcntl.LOCK_NB' in source
    assert 'O_NOFOLLOW' in source


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


def test_doctor_reports_missing_dependencies_with_a_nonzero_exit(tmp_path):
    doctor = ROOT / "bin" / "wilsof-doctor"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    result = run(
        doctor,
        env={
            "HOME": str(tmp_path),
            "PATH": str(fake_bin),
            "WILSOF_DOCTOR_SKIP_SESSION": "1",
        },
    )
    assert result.returncode == 1
    assert "MISSING dms" in result.stdout
    assert "MISSING ghostty" in result.stdout
    assert "MISSING busctl (cannot inspect the power-profile D-Bus backend)" in result.stdout


def test_doctor_is_read_only_and_reports_a_present_empty_ghostty_config(tmp_path):
    doctor = ROOT / "bin" / "wilsof-doctor"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    for command in ("dms", "ghostty", "hyprland", "hypridle", "hyprlock", "systemctl"):
        executable = fake_bin / command
        executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        executable.chmod(0o755)
    config = tmp_path / ".config" / "ghostty"
    config.mkdir(parents=True)
    (config / "config.ghostty").touch()
    result = run(
        doctor,
        env={
            "HOME": str(tmp_path),
            "PATH": str(fake_bin),
            "WILSOF_DOCTOR_SKIP_SESSION": "1",
        },
    )
    assert result.returncode == 1
    assert "WARN Ghostty configuration is empty" in result.stdout
    assert (config / "config.ghostty").exists()


def test_doctor_checks_the_power_profile_package_and_dbus_backend():
    doctor = (ROOT / "bin" / "wilsof-doctor").read_text(encoding="utf-8")
    assert 'pacman -Q power-profiles-daemon' in doctor
    assert 'busctl --system status net.hadess.PowerProfiles' in doctor


def test_search_uses_dms_spotlight_all_mode_and_rejects_other_actions(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "args"
    dms = fake_bin / "dms"
    dms.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" > {log}\n", encoding="utf-8")
    dms.chmod(0o755)
    result = run(SEARCH, "toggle", env={"PATH": f"{fake_bin}:{os.environ['PATH']}"})
    assert result.returncode == 0, result.stderr
    assert log.read_text(encoding="utf-8").strip() == "ipc call spotlight toggle"
    assert run(SEARCH, "files", env={"PATH": f"{fake_bin}:{os.environ['PATH']}"}).returncode == 64


def test_vm_installer_provisions_regreet_with_tuigreet_fallback():
    content = (ROOT / "scripts" / "install-arch-test-vm.sh").read_text(encoding="utf-8")
    # Established distro packages; no custom greeter or auth stack.
    assert "greetd-regreet" in content
    assert "cage" in content
    assert "greetd-tuigreet" in content
    # The verified tuigreet greeter stays the default; ReGreet is provisioned
    # and documented as a one-line opt-in because QEMU/TCG evaluation could
    # not safely verify input delivery to the GTK entry.
    assert 'command = "tuigreet --time --cmd Hyprland"' in content
    assert '"wilsof-regreet"' in content
    assert "wilsof-greeter-bg.png" in content


def test_regreet_uses_the_approved_branding_and_dark_theme():
    regreet = (ROOT / "config" / "greetd" / "regreet.toml").read_text(encoding="utf-8")
    assert "wilsof-greeter-bg.png" in regreet
    assert "application_prefer_dark_theme = true" in regreet
    # No autologin: regreet always asks for credentials through greetd PAM.
    assert "autologin" not in regreet


def test_regreet_wrapper_forces_cairo_gtk_rendering_without_custom_auth():
    wrapper = ROOT / "config" / "greetd" / "wilsof-regreet"
    assert wrapper.is_file(), "the greeter wrapper must be tracked in the repository"
    text = wrapper.read_text(encoding="utf-8")
    # GTK4 default GL renderer painted blank text (and crashed once) on the
    # TCG software-rendering path; Cairo is the documented diagnostic that
    # rendered text. Keep the fix per-process inside the greeter wrapper.
    assert "GSK_RENDERER=cairo" in text
    assert "cage -s -- regreet" in text
    # The wrapper launches the stock greeter only; no auth logic of its own.
    assert "exec " in text
    assert text.count("\n") >= 5


def test_regreet_wrapper_exports_environment_and_execs_cage(tmp_path):
    wrapper = ROOT / "config" / "greetd" / "wilsof-regreet"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    cage = fake_bin / "cage"
    cage.write_text("#!/usr/bin/env bash\nprintf '%s\\n' \"$GSK_RENDERER\" \"$@\"\n", encoding="utf-8")
    cage.chmod(0o755)
    result = run(wrapper, env={"PATH": f"{fake_bin}:{os.environ['PATH']}"})
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == "cairo"
    assert lines[1:] == ["-s", "--", "regreet"]


def test_vm_installer_installs_the_regreet_wrapper():
    content = (ROOT / "scripts" / "install-arch-test-vm.sh").read_text(encoding="utf-8")
    assert "config/greetd/wilsof-regreet /usr/local/bin/wilsof-regreet" in content


def test_iso_profile_and_builder_are_present_and_keep_secrets_out_of_the_profile():
    profile = ROOT / "iso" / "profiledef.sh"
    packages = ROOT / "iso" / "packages.x86_64"
    builder = ROOT / "scripts" / "build-iso.sh"
    assert profile.is_file()
    assert packages.is_file()
    assert builder.is_file()
    package_text = packages.read_text(encoding="utf-8")
    assert "archiso" not in package_text
    assert "openssh" not in package_text
    assert "ghostty" in package_text
    assert "dux-shell" in package_text
    assert "power-profiles-daemon" in package_text
    assert "mkarchiso" in builder.read_text(encoding="utf-8")


def test_engineering_guide_and_audit_are_linked_from_the_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    guide = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    audit = (ROOT / "docs" / "quality-audit.md").read_text(encoding="utf-8")
    assert "[engineering guide](CONTRIBUTING.md)" in readme
    assert "[quality audit](docs/quality-audit.md)" in readme
    assert "physical client" in guide
    assert "High: validation did not cover every executable shell path" in audit


def test_validation_workflow_uses_shellcheck_for_each_shell_dialect():
    workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
    assert "apt-get install --yes shellcheck" in workflow
    assert "bin/wilsof-doctor" in workflow
    assert "--shell=sh" in workflow
    assert "--shell=bash automation/wilsof-github-worker.sh scripts/install-arch-test-vm.sh" in workflow
