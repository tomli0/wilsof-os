from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "hypr" / "wilsof.conf"


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
        "bind = SUPER, 1, workspace, 1",
        "bind = SUPER SHIFT, 1, movetoworkspace, 1",
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
