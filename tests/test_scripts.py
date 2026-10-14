import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEARCH = ROOT / "bin" / "wilsof-search"
PREFLIGHT = ROOT / "scripts" / "preflight-fedora.sh"
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


def test_preflight_is_read_only_and_reports_missing_fedora_tools():
    result = run(PREFLIGHT)
    assert result.returncode != 0
    assert "Fedora" in result.stderr


def test_installer_requires_explicit_target_vm_guard():
    result = run(INSTALL)
    assert result.returncode == 64
    assert "WILSOF_TARGET_VM=1" in result.stderr


def test_wallpaper_unit_quotes_asset_path_with_spaces():
    content = WALLPAPER_UNIT.read_text(encoding="utf-8")
    assert '"%h/.local/share/wilsof-os/assets/Mørk geometrisk bakgrunn med isblått WS-monogram.png"' in content
