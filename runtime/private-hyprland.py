"""Opt-in private compositor input, shared by image and target provisioning.

No package bytes or pins belong in Git. The embedded marker is an explicit
private-image policy, not independent security approval or a signature bypass.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess

MANIFEST = 'PRIVATE-HYPRLAND.json'
MARKER = 'private-hyprland.required'
PACKAGE = 'private-hyprland.pkg.tar.zst'
FIELDS = {'schema', 'package', 'name', 'version', 'architecture', 'sha256', 'binary_sha256'}


def fail():
    raise ValueError('Private Hyprland input or installed identity rejected; no fallback') from None


def regular(path):
    path = Path(path)
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        fail()
    return path


def archive(package, member):
    # Read only selected archive members; never extract package paths on the host.
    return subprocess.run(['bsdtar', '-xOf', str(package), member], check=True,
                          capture_output=True).stdout


def validate(record, package):
    if (not isinstance(record, dict) or set(record) != FIELDS or type(record['schema']) is not int or record['schema'] != 1
            or record['name'] != 'hyprland-as02-private'
            or record['architecture'] != 'x86_64'
            or not isinstance(record['version'], str)
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._+:-]{0,127}', record['version'])
            or any(not isinstance(record[k], str) or not re.fullmatch(r'[0-9a-f]{64}', record[k])
                   for k in ('sha256', 'binary_sha256'))):
        fail()
    package = regular(package)
    with package.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != record['sha256']:
            fail()
    info = archive(package, '.PKGINFO').decode('utf-8')
    for key, value in [('pkgname', record['name']), ('pkgver', record['version']), ('arch', record['architecture'])]:
        if re.findall(r'^' + key + r' = (.+)$', info, re.M) != [value]:
            fail()
    if hashlib.sha256(archive(package, 'usr/bin/Hyprland')).hexdigest() != record['binary_sha256']:
        fail()
    dependencies = []
    for dependency in re.findall(r'^depend = (.+)$', info, re.M):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9@._+:-]*(?:[<>=]+[A-Za-z0-9._+:-]+)?', dependency):
            fail()
        name = re.split(r'[<>=]', dependency, maxsplit=1)[0]
        if name in ('hyprland', record['name']):
            fail()
        dependencies.append(name)
    return dict(record, package=str(package), dependencies=sorted(set(dependencies)),
                dependency_constraints=re.findall(r'^depend = (.+)$', info, re.M))


def load(env=None):
    env = os.environ if env is None else env
    mode = env.get('WILSOF_PRIVATE_EXPERIMENTAL')
    path = env.get('WILSOF_PRIVATE_HYPRLAND_CONTRACT')
    if mode is None and path is None:
        return None
    try:
        if mode != '1' or not path:
            fail()
        record = json.loads(regular(path).read_text())
        return validate(record, record.get('package', ''))
    except (OSError, ValueError, TypeError, AttributeError, UnicodeError, subprocess.SubprocessError):
        fail()


def stage(record, base, *, require_signature=False):
    """Copy into a NEW image or target private namespace; no overwrite/reuse."""
    base = Path(base)
    folder = base / 'packages'
    destinations = [folder / PACKAGE, folder / MANIFEST, base / MARKER]
    pin = runpy.run_path(str(Path(__file__).with_name('pinned-package.py')))
    signature = pin['detached_signature'](record['package'], required=require_signature)
    signature_destination = folder / (PACKAGE + '.sig')
    if signature_destination.exists() or signature_destination.is_symlink():
        fail()
    if any(p.exists() or p.is_symlink() or any(a.is_symlink() for a in p.parents) for p in destinations):
        fail()
    folder.mkdir(parents=True, exist_ok=True)
    package, manifest, marker = destinations
    with package.open('xb') as output, regular(record['package']).open('rb') as source:
        shutil.copyfileobj(source, output)
    if signature is not None:
        with signature_destination.open('xb') as output, signature.open('rb') as source:
            shutil.copyfileobj(source, output)
        signature_destination.chmod(0o600)
    clean = {k: record[k] for k in FIELDS}
    clean['package'] = PACKAGE  # Never embed the builder's private source path.
    data = (json.dumps(clean, sort_keys=True) + '\n').encode()
    with manifest.open('xb') as output:
        output.write(data)
    with marker.open('x') as output:
        output.write(hashlib.sha256(data).hexdigest() + '\n')
    for path in destinations:
        path.chmod(0o600)
    return embedded(base, required=True)


def embedded(base, *, required=False):
    base = Path(base)
    marker, manifest = base / MARKER, base / 'packages' / MANIFEST
    if not required and not any(p.exists() or p.is_symlink() for p in (marker, manifest, base / 'packages' / PACKAGE)):
        return None
    try:
        data = regular(manifest).read_bytes()
        if regular(marker).read_text().strip() != hashlib.sha256(data).hexdigest():
            fail()
        record = json.loads(data)
        if record.get('package') != PACKAGE:
            fail()
        return validate(record, base / 'packages' / PACKAGE)
    except (OSError, ValueError, TypeError, AttributeError, UnicodeError, subprocess.SubprocessError):
        fail()


def selection(packages, record):
    if record is None:
        return packages
    return list(dict.fromkeys([p for p in packages if p != 'hyprland'] + record['dependencies']))


def verify(target, record):
    target = Path(target)
    pin = runpy.run_path(str(Path(__file__).with_name('pinned-package.py')))
    def query(*args):
        return subprocess.run(pin['target_command'](target, 'pacman', *args),
                              check=True, capture_output=True, text=True).stdout.strip()
    try:
        if query('-Q', record['name']) != record['name'] + ' ' + record['version']:
            fail()
        if query('-Qoq', '/usr/bin/Hyprland') != record['name']:
            fail()
        binary = regular(target / 'usr/bin/Hyprland')
        with binary.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != record['binary_sha256']:
                fail()
    except (OSError, ValueError, subprocess.SubprocessError):
        fail()


def install(target, base, *, required=False, require_signature=False):
    record = embedded(base, required=required)
    if record is None:
        return
    target = Path(target)
    pin = runpy.run_path(str(Path(__file__).with_name('pinned-package.py')))
    try:
        # Repository Hyprland must never be the selected compositor in private mode.
        pin['detached_signature'](record['package'], required=require_signature)
        result = subprocess.run(pin['target_command'](target, 'pacman', '-Qq'),
                                check=True, capture_output=True, text=True)
        if 'hyprland' in result.stdout.splitlines():
            fail()
        if record['dependency_constraints']:
            # All dependencies/ABIs must already be supplied by the verified
            # image/target transaction; never let -U resolve a second closure.
            result = subprocess.run(pin['target_command'](target, 'pacman', '-T',
                                    '--', *record['dependency_constraints']),
                                    check=True, capture_output=True, text=True)
            if result.stdout.strip():
                fail()
        destination = target / 'usr/share/wilsof'
        if Path(base).resolve() != destination.resolve():
            record = stage(record, destination, require_signature=require_signature)
        # Same standard local-package policy as Hypridle; no SigLevel override.
        # Full dependency/version checks stay enabled; missing ABI/signature fails.
        subprocess.run(pin['target_command'](target, 'pacman', '-U', '--noconfirm',
                        '--', '/usr/share/wilsof/packages/' + PACKAGE),
                       check=True, capture_output=True)
        verify(target, record)
    except (OSError, ValueError, subprocess.SubprocessError):
        fail()
