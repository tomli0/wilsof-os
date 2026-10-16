from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap-desktop.sh"


def test_bootstrap_is_present_and_fails_fast():
    content = BOOTSTRAP.read_text(encoding="utf-8")
    assert "set -eu" in content
    assert "dnf -y copr enable avengemedia/dms" in content
    assert "dnf -y copr enable ashbuk/Hyprland-Fedora" in content
    assert "dnf -y install dms hyprland hyprlock hypridle xdg-desktop-portal-hyprland" in content
    assert "rpm --checksig" in content
    assert "rpm -q dms hyprland hyprlock hypridle xdg-desktop-portal-hyprland" in content
    assert "systemctl is-enabled gdm" in content
