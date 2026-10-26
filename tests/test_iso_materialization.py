import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_profile_uses_supported_archiso_bootmode_and_desktop_manifest():
    profile = (ROOT / 'iso/profiledef.sh').read_text()
    assert 'bootmodes=("uefi.systemd-boot")' in profile
    assert 'airootfs_image_type="squashfs"' in profile
    prepare = (ROOT / 'scripts/prepare-iso.py').read_text()
    assert "runtime/desktop-packages.txt" in prepare
    assert "packages.update((source / 'runtime/desktop-packages.txt')" in prepare


def test_profile_keeps_boot_dependencies_but_removes_remote_access_and_host_data(tmp_path):
    upstream = tmp_path / 'upstream'
    upstream.mkdir()
    (upstream / 'packages.x86_64').write_text('base\nmkinitcpio-archiso\nopenssh\ncloud-init\n')
    remote = upstream / 'airootfs/etc/systemd/system/multi-user.target.wants'
    remote.mkdir(parents=True)
    (remote / 'sshd.service').symlink_to('/usr/lib/systemd/system/sshd.service')
    (upstream / 'airootfs/root').mkdir()
    (upstream / 'airootfs/root/.automated_script.sh').write_text('untrusted network script')
    destination = tmp_path / 'profile'
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/prepare-iso.py'), '--upstream', str(upstream), '--output', str(destination), '--source', str(ROOT), '--commit', 'a' * 40], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    packages = (destination / 'packages.x86_64').read_text().splitlines()
    assert 'mkinitcpio-archiso' in packages
    assert 'openssh' not in packages and 'cloud-init' not in packages
    assert not (destination / 'airootfs/etc/systemd/system/multi-user.target.wants/sshd.service').is_symlink()
    assert not (destination / 'airootfs/root/.automated_script.sh').exists()
    payload = destination / 'airootfs/usr/share/wilsof/source'
    assert not (payload / '.git').exists()
    assert not (payload / 'scripts/install-arch-test-vm.sh').exists()
    assert (payload / 'runtime/desktop.py').exists()
    assert (payload / 'SOURCE_COMMIT').read_text().strip() == 'a' * 40
    assert (destination / 'airootfs/etc/greetd/config.toml').is_file()


def test_payload_manifest_excludes_private_extras_and_rejects_symlinks(tmp_path):
    import shutil
    source = tmp_path / 'source'
    for folder in ('runtime', 'bin', 'config', 'assets', 'schemas', 'iso'):
        shutil.copytree(ROOT / folder, source / folder)
    (source / 'bin/private-note').write_text('private fixture, not image data')
    upstream = tmp_path / 'upstream'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('mkinitcpio-archiso\n')
    args = [sys.executable, str(ROOT / 'scripts/prepare-iso.py'), '--upstream', str(upstream), '--source', str(source), '--commit', 'a' * 40]
    result = subprocess.run(args + ['--output', str(tmp_path / 'good')], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / 'good/airootfs/usr/share/wilsof/source/bin/private-note').exists()
    (source / 'bin/wilsof-doctor').unlink()
    (source / 'bin/wilsof-doctor').symlink_to(source / 'bin/private-note')
    result = subprocess.run(args + ['--output', str(tmp_path / 'bad')], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Refusing source symlink' in result.stderr
