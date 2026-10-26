from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_iso_bash_profile_is_shellchecked():
    for filename in (".github/workflows/validate.yml", "CONTRIBUTING.md", "README.md"):
        lines = (ROOT / filename).read_text().splitlines()
        assert any("shellcheck --shell=bash" in line and "iso/profiledef.sh" in line for line in lines)


def test_lock_logo_has_scalar_size_and_no_frame():
    content = (ROOT / "config/hypr/hyprlock.conf").read_text()
    assert "size = 93" in content
    assert "rounding = 0" in content
    assert "border_size = 0" in content


def test_doctor_recognizes_activatable_backend(tmp_path):
    fake = tmp_path / "bin"
    fake.mkdir()
    bus = fake / "busctl"
    bus.write_text('#!/bin/sh\ncase "$*" in\n *status*) exit 1;;\n *--activatable*) printf "net.hadess.PowerProfiles\\n";;\n *) exit 2;;\nesac\n')
    bus.chmod(0o755)
    result = subprocess.run([str(ROOT / "bin/wilsof-doctor")], text=True, capture_output=True,
                            env=os.environ | {"HOME": str(tmp_path), "PATH": f"{fake}:/usr/bin:/bin", "WILSOF_DOCTOR_SKIP_SESSION": "1"})
    assert "OK D-Bus power-profile backend" in result.stdout
    assert "WARN D-Bus power-profile backend unavailable" not in result.stdout
