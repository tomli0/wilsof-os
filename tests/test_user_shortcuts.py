"""M5: limited, conflict-checked editing of common Wilsof shortcuts."""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYBINDS = ROOT / "config" / "wilsof-keybinds.json"
CLI = ROOT / "bin" / "wilsof-shortcuts"
LUA = ROOT / "config" / "hypr" / "wilsof.lua"
DESKTOP = ROOT / "runtime" / "desktop.py"
IMAGE_FILES = ROOT / "runtime" / "image-files.txt"
CENTER = ROOT / "config" / "dms" / "plugins" / "wilsofCommandCenter" / "CommandCenter.qml"
MODEL = ROOT / "config" / "dms" / "plugins" / "wilsofCommandCenter" / "Model.js"


def run_cli(home, *args):
    env = os.environ | {"HOME": str(home), "XDG_STATE_HOME": str(home / ".local/state")}
    return subprocess.run([str(CLI), *args], text=True, capture_output=True, env=env, check=False)


def read_state(home):
    return json.loads((home / ".local/state/wilsof-os/user-shortcuts.json").read_text(encoding="utf-8"))


def defaults_table():
    assert KEYBINDS.is_file(), "the machine-readable keybind table must be tracked"
    data = json.loads(KEYBINDS.read_text(encoding="utf-8"))
    assert data.get("schema") == 1
    return data


def test_keybind_table_covers_the_documented_wilsof_map_and_marks_editable_actions():
    data = defaults_table()
    actions = data["actions"]
    for action_id in ("command-center", "lock", "help", "settings", "firefox", "nautilus",
                      "fullscreen", "close-window"):
        assert action_id in actions, f"missing editable action {action_id}"
        assert actions[action_id]["keys"], f"{action_id} must declare its default keys"
    # Documented required mappings stay the Wilsof defaults.
    assert actions["command-center"]["keys"] == "SUPER + space"
    assert actions["lock"]["keys"] == "SUPER + L"
    assert actions["firefox"]["keys"] == "SUPER + B"
    assert actions["nautilus"]["keys"] == "SUPER + E"
    assert actions["fullscreen"]["keys"] == "SUPER + F"
    for action in actions.values():
        assert action["editable"] is True, "the table carries only editable actions"
    assert "SUPER + 1" in data["reserved"]
    assert "SUPER + SHIFT + 9" in data["reserved"]
    assert "SUPER + RETURN" in data["reserved"]


def test_list_shows_defaults_and_supports_filtering(tmp_path):
    result = run_cli(tmp_path, "list")
    assert result.returncode == 0, result.stderr
    assert "SUPER + L" in result.stdout
    result = run_cli(tmp_path, "list", "--filter", "lås")
    assert result.returncode == 0
    assert "lock" in result.stdout
    assert "SUPER + space" not in result.stdout


def test_set_rewrites_one_binding_and_generates_a_valid_override_file(tmp_path):
    result = run_cli(tmp_path, "set", "lock", "Ctrl+Alt+K")
    assert result.returncode == 0, result.stderr
    state = read_state(tmp_path)
    assert state["overrides"]["lock"]["keys"] == "CTRL + ALT + K"
    lua = (tmp_path / ".config/hypr/wilsof-user-shortcuts.lua").read_text(encoding="utf-8")
    assert 'hl.unbind("SUPER + L")' in lua
    assert 'hl.bind("CTRL + ALT + K"' in lua
    assert "wilsof-lock" in lua
    # The effective map now reports the new keys for the edited action only.
    result = run_cli(tmp_path, "list", "--json")
    effective = {row["id"]: row["keys"] for row in json.loads(result.stdout)["actions"]}
    assert effective["lock"] == "CTRL + ALT + K"
    assert effective["command-center"] == "SUPER + space"


def test_set_rejects_conflicting_keys_without_touching_existing_files(tmp_path):
    first = run_cli(tmp_path, "set", "lock", "Ctrl+Alt+K")
    assert first.returncode == 0, first.stderr
    before = (tmp_path / ".config/hypr/wilsof-user-shortcuts.lua").read_text(encoding="utf-8")
    clash = run_cli(tmp_path, "set", "help", "Ctrl+Alt+K")
    assert clash.returncode == 65, clash.stdout + clash.stderr
    assert "conflict" in (clash.stderr + clash.stdout).lower()
    # A default key of another action is also a conflict.
    reserved = run_cli(tmp_path, "set", "help", "Super+Q")
    assert reserved.returncode == 65
    assert (tmp_path / ".config/hypr/wilsof-user-shortcuts.lua").read_text(encoding="utf-8") == before


def test_set_rejects_reserved_workspace_and_navigation_keys(tmp_path):
    for keys in ("SUPER + 3", "Super+Shift+9", "SUPER + RETURN"):
        result = run_cli(tmp_path, "set", "lock", keys)
        assert result.returncode == 65, keys
        assert not (tmp_path / ".config/hypr/wilsof-user-shortcuts.lua").exists(), keys


def test_set_rejects_unknown_actions_and_invalid_keys(tmp_path):
    assert run_cli(tmp_path, "set", "workspace-9", "Super+K").returncode == 66
    assert run_cli(tmp_path, "set", "lock", "").returncode == 64
    assert run_cli(tmp_path, "set", "lock", "Not+A+Key!").returncode == 64
    assert not (tmp_path / ".local/state/wilsof-os/user-shortcuts.json").exists()


def test_reset_restores_defaults_and_preserves_other_overrides(tmp_path):
    assert run_cli(tmp_path, "set", "lock", "Ctrl+Alt+K").returncode == 0
    assert run_cli(tmp_path, "set", "help", "Ctrl+Alt+F2").returncode == 0
    result = run_cli(tmp_path, "reset", "lock")
    assert result.returncode == 0, result.stderr
    state = read_state(tmp_path)
    assert "lock" not in state["overrides"]
    assert state["overrides"]["help"]["keys"] == "CTRL + ALT + F2"
    lua = (tmp_path / ".config/hypr/wilsof-user-shortcuts.lua").read_text(encoding="utf-8")
    assert "SUPER + L" not in lua
    assert "CTRL + ALT + F2" in lua
    all_reset = run_cli(tmp_path, "reset")
    assert all_reset.returncode == 0, all_reset.stderr
    assert read_state(tmp_path)["overrides"] == {}
    assert not (tmp_path / ".config/hypr/wilsof-user-shortcuts.lua").exists()


def test_wilsof_lua_loads_user_overrides_after_the_app_shortcuts_seed():
    text = LUA.read_text(encoding="utf-8")
    assert 'require("wilsof-app-shortcuts")' in text
    assert "wilsof-user-shortcuts.lua" in text
    assert text.index("wilsof-app-shortcuts") < text.index("wilsof-user-shortcuts")


def test_installer_deploys_the_shortcuts_tools_without_touching_user_files():
    desktop = DESKTOP.read_text(encoding="utf-8")
    assert "wilsof-shortcuts" in desktop
    assert "wilsof-keybinds.json" in desktop
    user_config = (ROOT / "scripts" / "install-user-config.sh").read_text(encoding="utf-8")
    assert "wilsof-shortcuts" in user_config
    # The override file itself is never seeded: it only appears on first edit.
    assert "wilsof-user-shortcuts.lua" not in desktop
    image_files = IMAGE_FILES.read_text(encoding="utf-8")
    assert "config/dms/plugins/wilsofCommandCenter/Shortcuts.qml" in image_files


def test_command_center_exposes_the_shortcut_editor_and_locks_it_down_with_the_session():
    center = CENTER.read_text(encoding="utf-8")
    assert 'source: Qt.resolvedUrl("Shortcuts.qml")' in center
    # The editor modal has its own keyboard input; the same F1 discipline applies.
    lockdown = center.split("function lockdown()")[1].split("function open()")[0]
    assert "shortcutsLoader" in lockdown or "shortcuts" in lockdown
    model = MODEL.read_text(encoding="utf-8")
    assert "shortcuts" in model
    modal = ROOT / "config" / "dms" / "plugins" / "wilsofCommandCenter" / "Shortcuts.qml"
    assert modal.is_file()
