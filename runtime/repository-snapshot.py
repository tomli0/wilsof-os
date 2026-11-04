"""One approved dated repository policy for build, live and fresh-target roots.

No environment override or rolling-mirror fallback. Reading is side-effect free;
materialization is restricted to a separately prepared non-host root.
"""
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import tempfile

DATE = '2026-11-01'
SERVER = 'https://archive.archlinux.org/repos/2026/11/01/$repo/os/$arch'
CONFIG = ('[options]\nArchitecture = x86_64\nCheckSpace\n'
          'SigLevel = Required TrustedOnly DatabaseOptional\n'
          'LocalFileSigLevel = Optional\n\n'
          '[core]\nServer = ' + SERVER + '\n\n[extra]\nServer = ' + SERVER + '\n')
MIRRORS = 'Server = ' + SERVER + '\n'
RECORD = {'schema': 1, 'date': DATE, 'architecture': 'x86_64',
          'repositories': ['core', 'extra'],
          'pacman_conf_sha256': hashlib.sha256(CONFIG.encode()).hexdigest()}
MANIFEST = 'usr/share/wilsof/REPOSITORY-SNAPSHOT.json'


def checked(root, relative):
    root = Path(root)
    if not root.is_absolute() or root.resolve() != root:
        raise ValueError('Repository snapshot root must be canonical and absolute')
    path = root / relative
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Repository snapshot path symlink rejected')
    return path


def content():
    return {MANIFEST: json.dumps(RECORD, sort_keys=True) + '\n',
            'etc/pacman.conf': CONFIG, 'etc/pacman.d/mirrorlist': MIRRORS}


def read(root=Path('/')):
    for relative, expected in content().items():
        path = checked(root, relative)
        if not path.is_file() or path.read_text() != expected:
            raise ValueError('Required repository snapshot missing or changed; no fallback')
    return dict(RECORD)


def stage(root):
    root = Path(root)
    if root == Path('/'):
        raise ValueError('Refusing to configure the running system')
    files = [(checked(root, relative), text) for relative, text in content().items()]
    # Refuse every unsafe destination/ancestor before writing any of them.
    for path, _ in files:
        if path.exists() and not path.is_file():
            raise ValueError('Invalid repository snapshot destination')
        if any(p.exists() and not p.is_dir() for p in path.parents):
            raise ValueError('Invalid repository snapshot ancestor')
    for path, text in files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        path.chmod(0o644)
    return read(root)

def command(argv):
    return subprocess.run(list(map(str, argv)), check=True, capture_output=True, text=True).stdout


def preflight(root, packages, private_record, *, directory=Path('/var/tmp')):
    """Verify/download the target closure before any disk operation, in a new DB."""
    record = read(root)
    config = checked(root, 'etc/pacman.conf')
    original_keys = Path(command(['pacman-conf', '--config', str(config), 'GPGDir']).strip())
    targets = list(dict.fromkeys(packages + (private_record['dependency_constraints'] if private_record else [])))
    tools = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/package-preflight.py'))
    with tempfile.TemporaryDirectory(prefix='wilsof-target-inputs-', dir=directory) as temporary:
        state = Path(temporary)
        keys = state / 'keyring'; keys.mkdir(mode=0o700)
        # Public trust only; no host configuration or secret key material.
        for name in ('pubring.gpg', 'trustdb.gpg'):
            origin = checked(original_keys, name)
            if not origin.is_file():
                raise ValueError('Accepted public pacman keyring missing')
            shutil.copyfile(origin, keys / name)
        resolved = tools['verify_transaction'](config, targets, state / 'cache', state / 'db', keys, private_record)
    if read(root) != record:
        raise ValueError('Repository snapshot changed during target preflight')
    return {'snapshot': record, 'packages': resolved}

def verify_installed(target, receipt):
    """Before local private-package replacement, attest the signed transaction."""
    if read(target) != receipt['snapshot']:
        raise ValueError('Installed repository snapshot differs from reviewed inputs')
    rows = receipt['packages']
    if not rows or any(not re.fullmatch(r'[A-Za-z0-9@_+.-]+', row['name']) or not row['version'] for row in rows):
        raise ValueError('Invalid reviewed repository transaction')
    expected = sorted(row['name'] + ' ' + row['version'] for row in rows)
    if len({row['name'] for row in rows}) != len(rows):
        raise ValueError('Duplicate reviewed repository transaction')
    pin = runpy.run_path(str(Path(__file__).with_name('pinned-package.py')))
    actual = command(pin['target_command'](target, 'pacman', '-Q', '--', *[row['name'] for row in rows]))
    if sorted(actual.splitlines()) != expected:
        raise ValueError('Installed packages differ from reviewed repository transaction')
    destination = checked(target, 'usr/share/wilsof/REPOSITORY-INPUTS.json')
    with destination.open('x') as stream:
        stream.write(json.dumps(receipt, sort_keys=True) + '\n')
    destination.chmod(0o644)
