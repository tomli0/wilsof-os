from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "hypr" / "wilsof.conf"
LUA_CONFIG = ROOT / "config" / "hypr" / "wilsof.lua"
IDLE_CONFIG = ROOT / "config" / "hypr" / "hypridle.conf"
LOCK_CONFIG = ROOT / "config" / "hypr" / "hyprlock.conf"


def read_lua_config():
    return LUA_CONFIG.read_text(encoding="utf-8")


def read_idle_config():
    return IDLE_CONFIG.read_text(encoding="utf-8")


def read_config():
    return CONFIG.read_text(encoding="utf-8")


def test_super_space_uses_the_single_wilsof_search_entrypoint():
    config = read_config()
    assert "bind = SUPER, SPACE, exec, wilsof-search toggle" in config
    assert "dms ipc call spotlight toggle" not in config


def test_required_window_and_workspace_bindings_exist():
    config = read_config()
    for binding in (
        "bind = SUPER, left, movefocus, l",
        "bind = SUPER SHIFT, left, movewindow, l",
        "bind = SUPER CTRL, left, resizeactive, -40 0",
        *[f"bind = SUPER, {number}, workspace, {number}" for number in range(1, 10)],
        *[f"bind = SUPER SHIFT, {number}, movetoworkspace, {number}" for number in range(1, 10)],
        "bind = SUPER, Q, killactive,",
        "bind = SUPER, F, fullscreen,",
        "bind = SUPER SHIFT, SPACE, togglefloating,",
        "bind = SUPER, L, exec, loginctl lock-session",
    ):
        assert binding in config


def test_visual_tokens_match_the_approved_direction():
    config = read_config()
    assert "col.active_border = rgb(86b9ce)" in config
    assert "col.inactive_border = rgb(3a424b)" in config
    assert "rounding = 6" in config
    assert "gaps_in = 8" in config
    assert "gaps_out = 10" in config


def test_config_starts_shell_via_user_systemd_target():
    config = read_config()
    assert "dbus-update-activation-environment --systemd --all" in config
    assert "systemctl --user start wilsof-session.target" in config


def test_assets_are_included_in_project():
    assets = ROOT / "assets"
    assert (assets / "Mørk geometrisk bakgrunn med isblått WS-monogram.png").is_file()
    assert (assets / "Wilsof OS-logo med geometrisk WS-monogram.png").is_file()
    assert (assets / "exec-92ed0dcf-0232-4ba6-a50e-52edcc98abbd.png").is_file()


def test_dms_lua_integration_overrides_the_generated_defaults():
    config = read_lua_config()
    assert 'hl.bind("SUPER + space", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-search toggle"))' in config
    assert 'hl.bind("SUPER + L", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-lock"))' in config
    assert 'active_border = "rgb(86b9ce)"' in config
    assert 'kb_layout = "no"' in config
    assert 'systemctl --user start wilsof-session.target' in config
    assert 'require("wilsof")' not in config


def test_lua_owns_the_agreed_live_keybindings_with_supported_dispatchers():
    config = read_lua_config()
    for binding in (
        '"SUPER + I", hl.dsp.exec_cmd("dms ipc call settings open")',
        '"SUPER + F1", hl.dsp.exec_cmd(wilsof_bin .. "wilsof-help")',
        '"SUPER + Q", hl.dsp.window.close()',
        '"SUPER + F", hl.dsp.exec_cmd("hyprctl dispatch fullscreen")',
        '"SUPER + SHIFT + space", hl.dsp.window.float({ action = "toggle" })',
        '"SUPER + CTRL + left", hl.dsp.exec_cmd("hyprctl dispatch resizeactive -40 0")',
        'hl.dsp.focus({ workspace = workspace })',
        'hl.dsp.window.move({ workspace = workspace })',
    ):
        assert binding in config
    assert "hl.dsp.dispatch" not in config
    assert 'hl.unbind(key)' in config
    key_table = config.split("for _, key", 1)[0]
    assert '"SUPER + F1"' in key_table
    assert 'require("wilsof-vm-test-enabled")' in config


def test_idle_config_locks_with_the_wilsof_wrapper_before_sleep():
    config = read_idle_config()
    assert "lock_cmd = $HOME/.local/bin/wilsof-lock" in config
    assert "before_sleep_cmd = $HOME/.local/bin/wilsof-lock" in config
    assert "on-timeout = $HOME/.local/bin/wilsof-lock" in config
    assert "dpms" not in config


def test_lock_surface_uses_approved_wilsof_tokens_and_password_feedback():
    config = LOCK_CONFIG.read_text(encoding="utf-8")
    assert "text = Wilsof OS" not in config
    assert "image {" in config
    assert "Wilsof OS-logo med geometrisk WS-monogram.png" in config
    assert "size = 93" in config
    assert "position = 0, 120" in config
    assert "rgb(20, 24, 30)" in config
    assert "rgb(134, 185, 206)" in config
    assert "rgb(230, 160, 160)" in config
    assert "Skriv passord for å låse opp" in config
    assert "Feil passord" in config
    assert "Mørk geometrisk bakgrunn med isblått WS-monogram.png" in config


def test_lock_logo_is_an_approved_transparent_asset():
    logo = ROOT / "assets" / "Wilsof OS-logo med geometrisk WS-monogram.png"
    data = logo.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    # PNG IHDR's ninth byte is the colour type; 6 is truecolour with alpha.
    assert data[25] == 6
