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


def validate_signature_policy(expanded):
    """Check each effective repository policy, not each serialized list item.

    pacman-conf emits repeated SigLevel lines for one section. Repositories
    without an override inherit [options]; local-file exceptions are separate
    and remain constrained by the exact snapshot and pinned-package consumers.
    """
    sections = {}
    section = None
    for line in expanded.splitlines():
        header = re.fullmatch(r'\[([^\[\]]+)\]', line.strip())
        if header:
            section = header[1]
            if section in sections:
                raise ValueError('Duplicate expanded pacman section')
            sections[section] = []
        else:
            directive = re.fullmatch(r'SigLevel\s*=\s*(.*)', line.strip())
            if directive:
                if section is None or not directive[1].split():
                    raise ValueError('Required trusted package signature policy must be retained')
                sections[section].extend(directive[1].split())
    def checked(tokens, inherited=()):
        policy = set(inherited)
        allowed = {'PackageRequired', 'PackageTrustedOnly', 'DatabaseRequired',
                   'DatabaseOptional', 'DatabaseTrustedOnly'}
        for token in tokens:
            values = ['Package' + token, 'Database' + token] if token in (
                'Required', 'Optional', 'Never', 'TrustedOnly', 'TrustAll') else [token]
            if any(value not in allowed for value in values):
                raise ValueError('Required trusted package signature policy must be retained')
            policy.update(values)
        if not {'PackageRequired', 'PackageTrustedOnly'} <= policy:
            raise ValueError('Required trusted package signature policy must be retained')
        return policy
    if 'options' not in sections:
        raise ValueError('Required trusted package signature policy must be retained')
    defaults = checked(sections['options'])
    for name, tokens in sections.items():
        if name != 'options':
            checked(tokens, defaults)


def freeze(profile, source, epoch, version):
    profile, source = Path(profile).resolve(), Path(source).resolve()
    destination = profile / 'BUILD-INPUTS.json'
    if destination.exists() or destination.is_symlink():
        raise ValueError('Refusing existing reserved provenance path')
    installed = sorted(command(['pacman', '-Q']).splitlines())
    tools = [re.fullmatch(r'archiso (91|92)-[A-Za-z0-9.]+', p) for p in installed if p.startswith('archiso ')]
    if len(tools) != 1 or tools[0] is None:
        raise ValueError('Supported build tools are Archiso 91/92; refuse other versions')
    boot = profile / 'BOOT-CONTRACT.json'
    if boot.is_symlink() or not boot.is_file():
        raise ValueError('Missing reviewed releng boot contract')
    contract = json.loads(boot.read_text())
    if contract != {'archiso_major': int(tools[0][1]), 'early_kms': 'wilsof-explicit'}:
        raise ValueError('Archiso tool/releng contract mismatch')
    conf = profile / 'pacman.conf'
    # pacman-conf expands Include and effective defaults. Never read mirrors or
    # signature configuration from the build host's default pacman invocation.
    expanded = command(['pacman-conf', '--config', str(conf)])
    validate_signature_policy(expanded)
    if re.search(r'^(Include|XferCommand)\s*=', expanded, re.M):
        raise ValueError('Unexpanded Include/custom downloader is unsupported')
    snapshot = runpy.run_path(str(source / 'runtime/repository-snapshot.py'))
    snapshot_record = snapshot['read'](profile / 'airootfs')
    if conf.read_text() != snapshot['CONFIG']:
        raise ValueError('Build repository snapshot differs from live/target policy')
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
        'repository_snapshot': snapshot_record,
        'boot_contract': contract,
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
    private = runpy.run_path(str(source / 'runtime/private-hyprland.py'))
    private_record = private['embedded'](profile / 'airootfs/usr/share/wilsof')
    if private_record is not None:
        record['private_hyprland'] = {k: private_record[k] for k in
                                    ('name', 'version', 'architecture', 'sha256', 'binary_sha256')}
        record['limitations'].append('Private experimental Hyprland: explicit local SHA256 trust input, not upstream acceptance or a signature-policy bypass')
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
