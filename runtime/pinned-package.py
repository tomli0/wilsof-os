"""Verified internal Hypridle artifact shared by image and target provisioning."""
import hashlib
from pathlib import Path
import shutil
import subprocess

PACKAGE_NAME = 'hypridle-0.1.8-2.1-x86_64.pkg.tar.zst'
PACKAGE_SHA256 = '3182ffaa24b0382c39614c460e15f90ff730d7da4f60378123d9b3df09c01d04'
BINARY_SHA256 = '3b5b36e21cb88e2939ed42f5d1a87c8b05f3c95876703545dd74dd280ee7fdd9'


def verified_package(directory):
    package = Path(directory) / PACKAGE_NAME
    if any(p.is_symlink() for p in (package, *package.parents)):
        raise ValueError('Refusing package symlink')
    if hashlib.sha256(package.read_bytes()).hexdigest() != PACKAGE_SHA256:
        raise ValueError('Internal Hypridle package checksum mismatch')
    return package


def install_package(target, directory):
    package = verified_package(directory)
    target = Path(target)
    destination = target / 'usr/share/wilsof/packages' / PACKAGE_NAME
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError('Refusing target package symlink')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if package != destination:
        shutil.copyfile(package, destination)
    destination.chmod(0o644)
    inside = '/usr/share/wilsof/packages/' + PACKAGE_NAME
    subprocess.run(['chroot', str(target), 'pacman', '-U', '--noconfirm', '--needed', inside], check=True)
    binary = target / 'usr/bin/hypridle'
    if binary.is_symlink() or hashlib.sha256(binary.read_bytes()).hexdigest() != BINARY_SHA256:
        raise ValueError('Installed Hypridle executable checksum mismatch')
