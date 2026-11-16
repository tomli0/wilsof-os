"""Fail-closed installed wl gate; module presence is not physical Wi-Fi acceptance.

The official DKMS hooks do the build. A successful Pacman transaction alone is
insufficient: post-transaction hook errors need an explicit module postcondition.
No modprobe, blacklist, signing-policy change or running-kernel assumption here.
"""
import fnmatch
import os
from pathlib import Path
import re
import runpy
import stat
import subprocess

PCI_ID = '14e4:43a0'
# Representative class-0280 alias; owner subsystem IDs are not yet recorded.
MODALIAS = 'pci:v000014E4d000043A0sv00000000sd00000000bc02sc80i00'


def discard_image_signing_key(root=Path('/')):
    """Image customization ONLY; never called for installed systems or updates.

    DKMS creates these default build-local files. The ISO must not distribute a
    shared private key; installed-target DKMS creates its own key independently.
    This does not make the generated module trusted by Secure Boot/lockdown.
    """
    root = Path(root)
    if not root.is_absolute() or root.resolve() != root:
        raise ValueError('Image signing material requires a canonical root')
    paths = [root / 'var/lib/dkms' / name for name in ('mok.key', 'mok.pub')]
    for path in paths:
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError('Unsafe image signing material path')
        if path.exists():
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.geteuid():
                raise ValueError('Unsafe image signing material ownership/type')
    for path in paths:
        path.unlink(missing_ok=True)


def stage(root):
    """Only new build/target roots, never mutate the running host's boot policy."""
    root = Path(root)
    if root == Path('/') or not root.is_absolute() or root.resolve() != root:
        raise ValueError('Broadcom configuration requires a separate canonical target')
    files = {
        # Same basename supersedes Arch's broad vendor-wide deny list. Only bcma
        # shares the confirmed PCI alias; prefer wl without disabling other cards.
        'etc/modprobe.d/broadcom-wl-dkms.conf':
            '# Wilsof BCM4360 preference; other Broadcom drivers remain available.\nsoftdep bcma pre: wl\n',
        # Claim the device before bcma, including in autodetected target initramfs.
        'etc/mkinitcpio.conf.d/wilsof-wl.conf':'# wl and cfg80211 must be available before root switch.\nMODULES+=(wl)\n',
    }
    for relative in files:
        path = root / relative
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError('Broadcom configuration symlink rejected')
        if path.exists() and not path.is_file():
            raise ValueError('Broadcom configuration destination is not a file')
    for relative, data in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)
        path.chmod(0o644)


def target_command(target, *argv):
    pin = runpy.run_path(str(Path(__file__).with_name('pinned-package.py')))
    args = pin['target_command'](target, *argv)
    return subprocess.run(args, capture_output=True, text=True, check=True, timeout=60).stdout


def verify(root=Path('/'), *, command=target_command):
    root = Path(root)
    if not root.is_absolute() or root.resolve() != root:
        raise ValueError('Broadcom target root must be canonical')
    rows = command(root, 'pacman', '-Q', 'linux', 'linux-headers', 'broadcom-wl-dkms', 'dkms')
    packages = dict(line.split() for line in rows.splitlines())
    if set(packages) != {'linux', 'linux-headers', 'broadcom-wl-dkms', 'dkms'}:
        raise ValueError('Required Broadcom packages missing')
    if packages['linux'] != packages['linux-headers']:
        raise ValueError('Broadcom requires matching linux and linux-headers versions')
    modules = root / 'usr/lib/modules'
    kernels = [p for p in modules.iterdir() if (p / 'pkgbase').is_file()
               and (p / 'pkgbase').read_text().strip() == 'linux']
    if len(kernels) != 1 or not re.fullmatch(r'[A-Za-z0-9_.+-]+', kernels[0].name):
        raise ValueError('Broadcom requires one supported Arch linux kernel tree')
    kernel = kernels[0]
    header = kernel / 'build/include/config/kernel.release'
    if not header.is_file() or header.read_text().strip() != kernel.name:
        raise ValueError('Broadcom matching kernel headers missing or unsupported')
    info = {field:command(root, 'modinfo', '-k', kernel.name, '-F', field, 'wl').strip()
            for field in ('filename', 'vermagic', 'alias', 'depends')}
    # Arch merges /lib into /usr/lib; do not resolve an absolute target symlink
    # against the build host when inspecting a mounted installed filesystem.
    filename = info['filename']
    prefix = '/lib/modules/' + kernel.name + '/'
    if filename.startswith(prefix):
        filename = '/usr' + filename
    expected = '/usr/lib/modules/' + kernel.name + '/'
    path = root / filename.lstrip('/')
    if (not filename.startswith(expected) or '..' in Path(filename).parts
            or not path.is_file() or path.is_symlink()):
        raise ValueError('Broadcom module missing from installed kernel filesystem')
    if not info['vermagic'].split() or info['vermagic'].split()[0] != kernel.name:
        raise ValueError('Broadcom module kernel ABI mismatch')
    if not any(fnmatch.fnmatchcase(MODALIAS, alias) for alias in info['alias'].splitlines()):
        raise ValueError('Broadcom module does not match confirmed PCI modalias')
    dependencies = sorted(filter(None, info['depends'].split(',')))
    if dependencies != ['cfg80211']:
        raise ValueError('Broadcom module dependency contract changed; review required')
    return {'pci_id':PCI_ID, 'kernel_release':kernel.name, 'packages':packages,
            'module':filename, 'dependencies':dependencies,
            'physical_acceptance':'PENDING'}
