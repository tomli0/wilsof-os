"""M5: explicit restore of the approved Wilsof appearance defaults."""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin" / "wilsof-appearance"
DESKTOP = ROOT / "runtime" / "desktop.py"
INSTALLER = ROOT / "scripts" / "install-user-config.sh"


def run_cli(home, *args):
    env = os.environ | {"HOME": str(home), "XDG_STATE_HOME": str(home / ".local/state")}
    return subprocess.run([str(CLI), *args], text=True, capture_output=True, env=env, check=False)


def seed_home(tmp_path, personal_changes=True):
    settings = tmp_path / ".config" / "DankMaterialShell" / "settings.json"
    settings.parent.mkdir(parents=True)
    template = json.loads((ROOT / "config" / "dms" / "settings-template.json").read_text(encoding="utf-8"))
    if personal_changes:
        template["wallpaperFillMode"] = "Zoom"
        template["currentThemeName"] = "personal"
    settings.write_text(json.dumps(template), encoding="utf-8")
    return settings


def test_show_reports_current_and_default_appearance(tmp_path):
    seed_home(tmp_path)
    result = run_cli(tmp_path, "show", "--json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["current"]["wallpaperFillMode"] == "Zoom"
    assert data["current"]["currentThemeName"] == "personal"
    assert data["defaults"]["wallpaperFillMode"] == "Fit"
    assert data["defaults"]["currentThemeName"] == "custom"


def test_show_fails_safely_when_settings_are_missing_or_invalid(tmp_path):
    result = run_cli(tmp_path, "show")
    assert result.returncode == 69
    broken = tmp_path / ".config" / "DankMaterialShell" / "settings.json"
    broken.parent.mkdir(parents=True)
    broken.write_text("{not json", encoding="utf-8")
    assert run_cli(tmp_path, "show").returncode == 69


def test_reset_backs_up_personal_settings_and_restores_wilsof_defaults(tmp_path):
    settings = seed_home(tmp_path)
    result = run_cli(tmp_path, "reset")
    assert result.returncode == 0, result.stderr
    restored = json.loads(settings.read_text(encoding="utf-8"))
    assert restored["wallpaperFillMode"] == "Fit"
    assert restored["currentThemeName"] == "custom"
    assert restored["customThemeFile"] == str(
        tmp_path / ".local/share/wilsof-os/wilsof-theme.json"
    )
    backups = list((tmp_path / ".local/state/wilsof-os/backups").rglob("settings.json"))
    assert len(backups) == 1, "the personal settings file must be backed up before restore"
    assert json.loads(backups[0].read_text(encoding="utf-8"))["wallpaperFillMode"] == "Zoom"


def test_reset_never_touches_other_user_files_and_refuses_invalid_settings(tmp_path):
    seed_home(tmp_path)
    personal = tmp_path / ".config" / "hypr" / "personal-notes.txt"
    personal.parent.mkdir(parents=True, exist_ok=True)
    personal.write_text("keep me", encoding="utf-8")
    assert run_cli(tmp_path, "reset").returncode == 0
    assert personal.read_text(encoding="utf-8") == "keep me"
    broken = tmp_path / ".config" / "DankMaterialShell" / "settings.json"
    broken.write_text("{not json", encoding="utf-8")
    before = broken.read_text(encoding="utf-8")
    assert run_cli(tmp_path, "reset").returncode == 69
    assert broken.read_text(encoding="utf-8") == before


def test_installer_deploys_the_appearance_tool(tmp_path):
    desktop = DESKTOP.read_text(encoding="utf-8")
    assert "wilsof-appearance" in desktop
    installer = INSTALLER.read_text(encoding="utf-8")
    assert "wilsof-appearance" in installer
