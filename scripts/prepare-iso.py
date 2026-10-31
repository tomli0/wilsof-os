#!/usr/bin/env python3
"""Materialize a sanitized Archiso 91 profile from upstream plus reviewed sources."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import runpy


def prepare(upstream, output, source, commit, *, hypridle_package=None):
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('An exact source commit is required')
    if output.exists():
        raise ValueError('Output profile must be a new dedicated directory')
    shutil.copytree(upstream, output, symlinks=True)
    shutil.copy2(source / 'iso/profiledef.sh', output / 'profiledef.sh')
    packages = set((upstream / 'packages.x86_64').read_text().splitlines())
    packages.update((source / 'iso/packages.x86_64').read_text().splitlines())
    packages.update((source / 'runtime/desktop-packages.txt').read_text().splitlines())
    packages.update({'archinstall', 'python-jsonschema', 'qemu-guest-agent', 'sudo'})
    packages.difference_update({'openssh', 'cloud-init', 'clonezilla', 'drbl'})
    (output / 'packages.x86_64').write_text('\n'.join(sorted(p for p in packages if p and not p.startswith('#'))) + '\n')
    root = output / 'airootfs'
    (root / 'mnt/wilsof').mkdir(parents=True, exist_ok=True)
    for relative in ('root', 'etc/ssh', 'etc/systemd/network',
                     'etc/systemd/system/getty@tty1.service.d',
                     'etc/systemd/system/cloud-init.target.wants'):
        path = root / relative
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        elif path.exists() or path.is_symlink():
            path.unlink()
    for path in (root / 'etc/systemd/system').rglob('*'):
        if path.is_symlink() and any(name in path.name for name in ('sshd', 'iwd', 'networkd', 'cloud-init', 'cloud-final', 'cloud-config')):
            path.unlink()

    def write(relative, text, mode=0o644):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            path.unlink()
        path.write_text(text)
        path.chmod(mode)

    payload = root / 'usr/share/wilsof/source'
    payload.mkdir(parents=True)
    for relative in (source / 'runtime/image-files.txt').read_text().splitlines():
        parts = Path(relative).parts
        if not parts or Path(relative).is_absolute() or '..' in parts:
            raise ValueError('Image manifest paths must be relative and contained')
        origin = source
        for part in parts:
            origin /= part
            if origin.is_symlink():
                raise ValueError(f'Refusing source symlink: {relative}')
        if not origin.is_file():
            raise ValueError(f'Missing reviewed image input: {relative}')
        dest = payload / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, dest)
    (payload / 'SOURCE_COMMIT').write_text(commit + '\n')
    sums = {str(p.relative_to(payload)): hashlib.sha256(p.read_bytes()).hexdigest() for p in payload.rglob('*') if p.is_file()}
    (payload / 'FILES.sha256.json').write_text(json.dumps(sums, indent=2, sort_keys=True) + '\n')
    # Gate the installed image dependency even when preparing without a local package.
    customization = "import runpy; pin=runpy.run_path('/usr/share/wilsof/source/runtime/pinned-package.py'); pin['verify_arch_chroot_support']()"
    if hypridle_package is not None:
        pin = runpy.run_path(str(source / 'runtime/pinned-package.py'))
        package = pin['verified_package'](hypridle_package.parent)
        if package != hypridle_package:
            raise ValueError('Exact verified Hypridle package filename required')
        packages_dir = root / 'usr/share/wilsof/packages'
        packages_dir.mkdir(parents=True)
        shutil.copyfile(package, packages_dir / package.name)
        customization += "; pin['install_package']('/', '/usr/share/wilsof/packages')"
    # Supported by pinned Archiso 91; removed from the image after execution.
    write('root/customize_airootfs.sh', '#!/bin/sh\nset -eu\npython3 -c "' + customization + '"\n', 0o755)
    lib = root / 'usr/local/lib/wilsof'
    lib.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / 'runtime/provision-target', lib / 'provision-target')
    (lib / 'provision-target').chmod(0o755)
    for name in ('wilsof-install', 'wilsof-config-update', 'wilsof-session'):
        if (source / 'bin' / name).is_file():
            write('usr/local/bin/' + name, (source / 'bin' / name).read_text(), 0o755)
    shutil.copy2(source / 'runtime/desktop-packages.txt', root / 'usr/share/wilsof/desktop-packages.txt')
    write('etc/shadow', 'root:!:14871::::::\n', 0o400)
    write('etc/hostname', 'wilsof-live\n')
    write('etc/greetd/config.toml', '[terminal]\nvt = 1\n[default_session]\ncommand = "tuigreet --cmd /usr/local/bin/wilsof-session"\nuser = "greeter"\n[initial_session]\ncommand = "/usr/local/bin/wilsof-session"\nuser = "live"\n')
    write('usr/local/lib/wilsof/live-setup', '#!/bin/sh\nset -eu\nid live >/dev/null 2>&1 || useradd -m -s /bin/bash live\nrunuser -u live -- dbus-run-session -- gsettings set org.gnome.desktop.media-handling automount false\nrunuser -u live -- dbus-run-session -- gsettings set org.gnome.desktop.media-handling automount-open false\n/usr/local/lib/wilsof/provision-target / live --live\n', 0o755)
    write('etc/sudoers.d/wilsof-live-installer', 'live ALL=(root) NOPASSWD: /usr/local/bin/wilsof-install, /usr/local/bin/wilsof-live-recover "", /usr/local/bin/wilsof-live-recover --restart\n', 0o440)
    write('usr/local/lib/wilsof/live-console-setup', (source / 'runtime/live-console-setup').read_text(), 0o755)
    write('usr/local/bin/wilsof-live-recover', (source / 'runtime/live-recover').read_text(), 0o755)
    write('etc/systemd/system/wilsof-live-console.service', '[Unit]\nDescription=Prepare local Wilsof recovery login\nAfter=systemd-sysusers.service local-fs.target\nBefore=wilsof-live-setup.service getty@tty2.service greetd.service\n[Service]\nType=oneshot\nExecStart=/usr/local/lib/wilsof/live-console-setup\nRemainAfterExit=yes\n[Install]\nWantedBy=multi-user.target\n')
    write('etc/systemd/system/wilsof-live-failure.service', '[Unit]\nDescription=Reveal live startup failure and recovery console\n[Service]\nType=oneshot\nExecStart=/usr/local/bin/wilsof-live-recover --show-failure\n')
    write('etc/systemd/system/getty@tty2.service.d/wilsof.conf', '[Unit]\nRequires=wilsof-live-console.service\nAfter=wilsof-live-console.service\n')
    tty = root / 'etc/systemd/system/getty.target.wants/getty@tty2.service'
    tty.parent.mkdir(parents=True, exist_ok=True)
    tty.symlink_to('/usr/lib/systemd/system/getty@.service')
    write('etc/systemd/system/wilsof-live-setup.service', '[Unit]\nDescription=Prepare ephemeral Wilsof live desktop\nRequires=wilsof-live-console.service\nAfter=systemd-sysusers.service local-fs.target wilsof-live-console.service\nBefore=greetd.service\nOnFailure=wilsof-live-failure.service\n[Service]\nType=oneshot\nExecStart=/usr/local/lib/wilsof/live-setup\nTimeoutStartSec=180\nRemainAfterExit=yes\n[Install]\nWantedBy=multi-user.target\n')
    write('etc/systemd/system/greetd.service.d/live.conf', '[Unit]\nRequires=wilsof-live-setup.service\nAfter=wilsof-live-setup.service\nOnFailure=wilsof-live-failure.service\n')
    write('etc/systemd/system/default.target', '')
    (root / 'etc/systemd/system/default.target').unlink()
    (root / 'etc/systemd/system/default.target').symlink_to('/usr/lib/systemd/system/graphical.target')
    for unit in ('wilsof-live-setup', 'greetd', 'NetworkManager', 'qemu-guest-agent'):
        path = root / 'etc/systemd/system/multi-user.target.wants' / (unit + '.service')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_symlink():
            path.symlink_to('/etc/systemd/system/wilsof-live-setup.service' if unit == 'wilsof-live-setup' else '/usr/lib/systemd/system/' + unit + '.service')
    # Match BlueZ's packaged systemctl enable contract, including its D-Bus alias.
    # The upstream unit's hardware condition handles absent adapters; no power-on.
    for relative in ('dbus-org.bluez.service', 'bluetooth.target.wants/bluetooth.service'):
        link = root / 'etc/systemd/system' / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink():
            link.unlink()
        link.symlink_to('/usr/lib/systemd/system/bluetooth.service')
    write('usr/share/applications/wilsof-install.desktop', '[Desktop Entry]\nType=Application\nName=Install Wilsof\nComment=Erase an explicitly selected empty test disk\nExec=ghostty -e sudo /usr/local/bin/wilsof-install\nIcon=system-software-install\nTerminal=false\nCategories=System;\n')
    write('etc/motd', 'Wilsof internal test image. Live evaluation is unlocked; do not enter private data. Install Wilsof from the launcher.\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('upstream', 'output', 'source'):
        parser.add_argument('--' + flag, type=Path, required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--hypridle-package', type=Path)
    args = parser.parse_args()
    prepare(args.upstream, args.output, args.source, args.commit, hypridle_package=args.hypridle_package)


if __name__ == '__main__':
    main()
