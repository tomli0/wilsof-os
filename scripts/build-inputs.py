#!/usr/bin/env python3
"""Freeze the verified repository transaction and record traceable build inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil

HERE = Path(__file__).resolve().parent
inventory = runpy.run_path(str(HERE / 'prepare-iso.py'))['inventory']
package_tools = runpy.run_path(str(HERE / 'package-preflight.py'))
command = package_tools['command']


def freeze(profile, source, epoch, version):
    profile, source = Path(profile).resolve(), Path(source).resolve()
    destination = profile / 'BUILD-INPUTS.json'
    if destination.exists() or destination.is_symlink():
        raise ValueError('Refusing existing reserved provenance path')
    installed = sorted(command(['pacman', '-Q']).splitlines())
    if not any(re.fullmatch(r'archiso 91-[A-Za-z0-9.]+', p) for p in installed):
        raise ValueError('Supported build tool is Archiso 91; refuse other versions')
    conf = profile / 'pacman.conf'
    # pacman-conf expands Include and effective defaults. Never read mirrors or
    # signature configuration from the build host's default pacman invocation.
    expanded = command(['pacman-conf', '--config', str(conf)])
    policies = re.findall(r'^SigLevel\s*=\s*(.*)$', expanded, re.M)
    if (not policies or any(not {'Required', 'PackageRequired'} & set(p.split())
                           or any(t in p.split() for t in ('Never', 'Optional', 'PackageNever', 'PackageOptional', 'TrustAll', 'PackageTrustAll'))
                           for p in policies)):
        raise ValueError('Required trusted package signature policy must be retained')
    if re.search(r'^(Include|XferCommand)\s*=', expanded, re.M):
        raise ValueError('Unexpanded Include/custom downloader is unsupported')
    original_keys = Path(command(['pacman-conf', '--config', str(conf), 'GPGDir']).strip())
    state = profile / '.build-inputs'
    state.mkdir()
    keys = state / 'keyring'
    keys.mkdir(mode=0o700)
    # Public trust material only: never copy secret keys or the host GPG config.
    for name in ('pubring.gpg', 'trustdb.gpg'):
        path = original_keys / name
        if not path.is_file() or path.is_symlink():
            raise ValueError('Required public pacman keyring is unavailable')
        shutil.copyfile(path, keys / name)
    cache, db = state / 'cache', state / 'db'
    conf.write_text(expanded)
    packages = package_tools['preflight'](profile, cache, db, keys)
    repositories = sorted(p.name for p in (db / 'sync').glob('*.db'))
    if not repositories:
        raise ValueError('No synchronized repository databases to freeze')
    for name in repositories:
        for suffix in ('', '.sig'):
            path = db / 'sync' / (name + suffix)
            if path.exists():
                if path.is_symlink() or not path.is_file():
                    raise ValueError('Invalid repository database input')
                shutil.copyfile(path, cache / path.name)
    # mkarchiso now consumes only the downloaded closure and the exact DBs that
    # resolved it. No live mirror refresh can silently select newer packages.
    frozen = []
    for line in expanded.splitlines():
        directive = line.split('=', 1)[0].strip()
        if directive in ('CacheDir', 'DBPath', 'LogFile', 'GPGDir', 'RootDir', 'HookDir', 'CacheServer'):
            continue
        if directive == 'Server':
            line = 'Server = ' + cache.as_uri()
        frozen.append(line)
        if line.strip() == '[options]':
            frozen.extend(['CacheDir = ' + str(cache), 'GPGDir = ' + str(keys)])
    conf.write_text('\n'.join(frozen) + '\n')
    # Record content identity without binding it to this machine's output path.
    normalized = conf.read_text().replace(str(profile), '<profile>')
    profile_files = inventory(profile)
    profile_files = {k: v for k, v in profile_files.items()
                     if not k.startswith('.build-inputs/') and k not in ('pacman.conf', 'BUILD-INPUTS.json')}
    record = {
        'schema': 1,
        'source': json.loads((profile / 'BUILD-SOURCE.json').read_text()),
        'configuration': {'source_date_epoch': epoch, 'iso_version': version, 'architecture': 'x86_64'},
        'tools': {'packages': installed, 'kernel': os.uname().release,
                  'os_release_sha256': hashlib.sha256(Path('/etc/os-release').read_bytes()).hexdigest()},
        'profile': profile_files,
        'original_pacman_conf': expanded,
        'frozen_pacman_conf': normalized,
        'repositories': {name: info for name, info in inventory(cache).items() if name.endswith(('.db', '.db.sig'))},
        'keyring': {k: v for k, v in inventory(keys).items() if k in ('pubring.gpg', 'trustdb.gpg')},
        'packages': packages,
        'limitations': ['Traceable inputs, not independently demonstrated byte-identical ISO reproducibility',
                        'Host tools/kernel, package hooks, filesystem timestamps and ISO tooling still affect output',
                        'Internal Hypridle is the existing SHA256-pinned local trust exception, not an Arch-signed package'],
    }
    with destination.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(record, indent=2, sort_keys=True) + '\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', type=Path)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    freeze(args.profile, args.source, os.environ['SOURCE_DATE_EPOCH'], os.environ['WILSOF_ISO_VERSION'])


if __name__ == '__main__':
    main()
