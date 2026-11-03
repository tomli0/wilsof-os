#!/usr/bin/env python3
"""Extract a minimal native-test fixture from an existing verified ISO; never build it."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def prepare(iso, expected_sha256, output):
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha256) or sha256(iso) != expected_sha256:
        raise ValueError('ISO SHA256 must match the independently recorded artifact')
    if output.exists():
        raise ValueError('Fixture output must be a new disposable directory')
    layout = subprocess.run(['xorriso', '-indev', str(iso), '-find', '/arch/x86_64/airootfs.sfs',
                             '-exec', 'report_lba', '--'], check=True, capture_output=True, text=True).stdout
    extent = re.search(r'File data lba:\s*0\s*,\s*(\d+)\s*,\s*\d+\s*,\s*(\d+)', layout)
    if not extent:
        raise ValueError('Expected a single SFS extent')
    offset = int(extent[1]) * 2048
    root = output / 'root'
    output.mkdir(parents=True, mode=0o700)

    def extract(*paths):
        subprocess.run(['unsquashfs', '-no-progress', '-no-xattrs', '-processors', '1',
                        '-o', str(offset), '-d', str(root), '-f', '-follow-symlinks',
                        str(iso), *paths], check=True, capture_output=True, text=True)

    extract('usr/bin/bash', 'usr/bin/pacman', 'usr/bin/vercmp', 'usr/bin/arch-chroot',
            'usr/lib/ld-linux-x86-64.so.2', 'usr/lib/libc.so.6', 'etc/pacman.conf',
            'etc/passwd', 'etc/group')
    loader = root / 'usr/lib/ld-linux-x86-64.so.2'
    # Ask the target dynamic loader for its real dependencies. Never run a host
    # package transaction or install anything into the host. Bound convergence.
    requested = set()
    for binary in ('bash', 'pacman', 'vercmp'):
        for _ in range(64):
            result = subprocess.run([str(loader), '--library-path', str(root / 'usr/lib'),
                                     '--list', str(root / 'usr/bin' / binary)],
                                    capture_output=True, text=True, env={'LC_ALL': 'C'})
            missing = re.search(r'error while loading shared libraries: ([A-Za-z0-9_.+-]+):', result.stderr)
            names = {missing[1]} if missing else set()
            for name, resolved in re.findall(r'(\S+) => (\S+) \(', result.stdout):
                if resolved != 'not' and not Path(resolved).resolve().is_relative_to(root.resolve()):
                    names.add(name)
            if result.returncode == 0 and not names:
                break
            if not names or names <= requested:
                raise ValueError('Cannot resolve isolated Arch dependencies: ' + result.stderr)
            for name in names:
                if not re.fullmatch(r'[A-Za-z0-9_.+-]+', name):
                    raise ValueError('Unsafe library name')
            requested.update(names)
            extract(*('usr/lib/' + name for name in sorted(names)))
        else:
            raise ValueError('Native dependency extraction did not converge')
    # Preserve the actual package metadata, not a synthesized version assertion.
    # Wildcards are extraction patterns interpreted by unsquashfs, never a shell.
    subprocess.run(['unsquashfs', '-no-progress', '-no-xattrs', '-processors', '1',
                    '-o', str(offset), '-d', str(root), '-f', str(iso),
                    'var/lib/pacman/local/ALPM_DB_VERSION',
                    'var/lib/pacman/local/arch-install-scripts-*/desc'],
                   check=True, capture_output=True, text=True)
    descs = list((root / 'var/lib/pacman/local').glob('arch-install-scripts-*/desc'))
    if len(descs) != 1:
        raise ValueError('Expected exactly one arch-install-scripts package record')
    version = descs[0].read_text().split('%VERSION%\n', 1)[1].splitlines()[0]
    # Squashfs root directories may be 0555; only this new owned fixture is mutable.
    for directory in [root, *(p for p in root.rglob('*') if p.is_dir() and not p.is_symlink())]:
        directory.chmod(directory.stat().st_mode | 0o700)
    for link, target in [('bin', 'usr/bin'), ('lib', 'usr/lib'), ('lib64', 'usr/lib')]:
        (root / link).symlink_to(target)
    for relative in ('proc', 'sys', 'dev/pts', 'dev/shm', 'run/systemd/resolve', 'tmp',
                     'var/log', 'var/cache/pacman/pkg', 'etc/pacman.d', 'usr/share/wilsof/packages'):
        (root / relative).mkdir(parents=True, exist_ok=True)
    (root / 'etc/pacman.d/mirrorlist').write_text('# Offline native contract fixture\n')
    # Keep only root and Pacman's actual DownloadUser identity, never host users.
    for name in ('passwd', 'group'):
        identity = root / 'etc' / name
        records = [line for line in identity.read_text().splitlines() if line.split(':', 1)[0] in {'root', 'alpm'}]
        if not any(line.startswith('alpm:') for line in records):
            raise ValueError('ISO package-manager identity missing')
        identity.write_text('\n'.join(records) + '\n')
    (root / 'etc/mtab').symlink_to('../proc/self/mounts')
    (root / 'etc/resolv.conf').symlink_to('/run/systemd/resolve/stub-resolv.conf')
    (root / 'run/systemd/resolve/stub-resolv.conf').write_text('nameserver 192.0.2.1\n')
    manifest = {'format': 'wilsof-native-chroot-fixture-v1', 'iso_sha256': expected_sha256,
                'arch_install_scripts_version': version,
                'files': {str(p.relative_to(root)): sha256(p) for p in root.rglob('*') if p.is_file() and not p.is_symlink()},
                'links': {str(p.relative_to(root)): str(p.readlink()) for p in root.rglob('*') if p.is_symlink()}}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.iso, args.sha256, args.output)))
