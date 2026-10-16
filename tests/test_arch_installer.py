from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-arch-test-vm.sh"


def test_arch_installer_configures_tuigreet_to_start_hyprland():
    content = INSTALLER.read_text(encoding="utf-8")
    assert "/etc/greetd/config.toml" in content
    assert 'command = "tuigreet --time --cmd Hyprland"' in content
    assert 'user = "greeter"' in content


def test_arch_installer_does_not_embed_desktop_passwords():
    content = INSTALLER.read_text(encoding="utf-8")
    assert "passwd wilsofdev" not in content
    assert "chpasswd" not in content
