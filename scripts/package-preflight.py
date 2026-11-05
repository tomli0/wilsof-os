#!/usr/bin/env python3
"""Verify the image transaction, never the build host's installed package set."""
import base64
import hashlib
from pathlib import Path
import re
import runpy
import subprocess


FORMAT = '%n\t%v\t%a\t%f\t%h\t%g\t%r'


def command(argv):
    """Helper output as strictly decoded UTF-8 text.

    Decoding failures are refusals, never successes: a helper whose output
    cannot be decoded cannot be inspected for the identity this pipeline
    binds to, so raise instead of returning mangled or lossy text.
    """
    try:
        return subprocess.run(list(map(str, argv)), check=True, capture_output=True,
                              text=True, encoding='utf-8', errors='strict').stdout
    except UnicodeDecodeError as error:
        raise ValueError(f'Helper output is not valid UTF-8: {Path(argv[0]).name}: {error}') from None


def gpg_status(argv):
    """Raw [GNUPG:] status bytes; explicit status tokens decide verification.

    OpenPGP user IDs are byte strings, and real trusted packager keys exist
    with non-UTF-8 (latin-1) UIDs. GPG echoes those raw bytes into its human
    diagnostics whenever the active locale cannot convert them, so the GPG
    streams must never be decoded before the VALIDSIG/TRUST token gates have
    accepted or rejected the signature: decoding anything earlier would turn
    a verified signature into an unhandled crash, and silently ignoring decode
    errors would blur the explicit machine-readable verdict.
    """
    result = subprocess.run(list(map(str, argv)), check=True, capture_output=True)
    if not isinstance(result.stdout, (bytes, bytearray)):
        raise ValueError('GPG status capture did not return raw bytes')
    return bytes(result.stdout)


def preflight(profile, cache, db, gpgdir):
    profile, cache, db, gpgdir = map(Path, (profile, cache, db, gpgdir))
    private = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'runtime/private-hyprland.py'))
    private_record = private['embedded'](profile / 'airootfs/usr/share/wilsof')
    targets = [line.split('#', 1)[0].strip() for line in (profile / 'packages.x86_64').read_text().splitlines()]
    targets = [p for p in targets if p]
    if private_record is not None:
        targets = list(dict.fromkeys(targets + private_record['dependency_constraints']))
    return verify_transaction(profile / 'pacman.conf', targets, cache, db, gpgdir, private_record)


def parse_resolved_packages(rows, private_record=None):
    """Preserve numeric epochs and bind each filename to its full identity.

    Native pacman filenames may contain the version epoch (e.g. 1:1.3.2-4).
    Never strip it or allow arbitrary colons/path components. Signature, SHA256
    and archive PKGINFO gates remain mandatory after this metadata parser.
    """
    if not rows:
        raise ValueError('Empty resolved image transaction')
    packages = []
    for row in rows:
        fields = row.split('\t')
        if len(fields) != 7:
            raise ValueError('Cannot identify resolved package')
        name, version, arch, filename, digest, signature, repo = fields
        if (not re.fullmatch(r'[A-Za-z0-9@_+.-]+', name)
                or not re.fullmatch(r'[A-Za-z0-9_.+-]+(?::[A-Za-z0-9_.+-]+)?\.pkg\.tar\.(zst|xz|gz)', filename)
                or not re.fullmatch(r'(?:[0-9]+:)?[A-Za-z0-9_.+]+-[0-9]+(?:\.[0-9]+)*', version)
                or filename not in {f'{name}-{version}-{arch}.pkg.tar.{suffix}' for suffix in ('zst', 'xz', 'gz')}
                or not re.fullmatch(r'[0-9a-f]{64}', digest)
                or arch not in ('any', 'x86_64') or not version or not repo):
            raise ValueError('Invalid resolved package identity')
        packages.append(dict(name=name, version=version, arch=arch, filename=filename,
                             sha256=digest, signature=signature, repository=repo))
    if len({p['name'] for p in packages}) != len(packages) or len({p['filename'] for p in packages}) != len(packages):
        raise ValueError('Duplicate resolved package identity')
    if private_record is not None and any(p['name'] in ('hyprland', private_record['name']) for p in packages):
        raise ValueError('Private Hyprland repository fallback rejected')
    return packages


def verify_transaction(config, targets, cache, db, gpgdir, private_record=None):
    """Same signature/metadata gate for image and pre-destructive target closure."""
    config, cache, db, gpgdir = map(Path, (config, cache, db, gpgdir))
    # A new local database forces dependencies already on the host into the image
    # transaction. Never --needed and never synchronize the host database.
    db.mkdir(parents=True, exist_ok=False)
    (db / 'local').mkdir()
    cache.mkdir(parents=True, exist_ok=True)
    if not targets or any(p.startswith('-') or any(c.isspace() for c in p) for p in targets):
        raise ValueError('Invalid or empty image package manifest')
    common = ['--config', str(config), '--dbpath', str(db),
              '--cachedir', str(cache), '--gpgdir', str(gpgdir), '--arch', 'x86_64',
              '--logfile', str(db / 'pacman.log'), '--noconfirm', '--noprogressbar']
    command(['pacman', '-Sy', *common])
    rows = command(['pacman', '-Sp', *common, '--print-format', FORMAT, '--', *targets]).splitlines()
    packages = parse_resolved_packages(rows, private_record)
    command(['pacman', '-Sw', *common, '--', *targets])
    for package in packages:
        path = cache / package['filename']
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != package['sha256']:
            raise ValueError(f'Missing or corrupt required package: {path.name}')
        signature = path.with_name(path.name + '.sig')
        if signature.is_symlink():
            raise ValueError('Refusing package signature symlink')
        # Repository signatures are embedded in the same frozen sync database.
        # A missing/invalid signature is fatal even if a profile permits Optional.
        signature.write_bytes(base64.b64decode(package.pop('signature'), validate=True))
        status = gpg_status(['gpg', '--no-options', '--homedir', str(gpgdir), '--batch',
                            '--no-auto-key-retrieve', '--auto-key-locate', 'clear',
                            '--status-fd', '1', '--verify', str(signature), str(path)])
        valid = re.findall(rb'^\[GNUPG:\] VALIDSIG ([0-9A-F]{40,64}) ', status, re.M)
        trusted = re.search(rb'^\[GNUPG:\] TRUST_(FULLY|ULTIMATE)\b', status, re.M)
        rejected = re.search(rb'^\[GNUPG:\] (BADSIG|ERRSIG|EXPSIG|EXPKEYSIG|REVKEYSIG|NO_PUBKEY)\b', status, re.M)
        if len(valid) != 1 or not trusted or rejected:
            raise ValueError(f'Untrusted or unverifiable signature: {path.name}')
        command(['bsdtar', '-tf', str(path)])
        info = command(['bsdtar', '-xOf', str(path), '.PKGINFO'])
        for key, expected in [('pkgname', package['name']), ('pkgver', package['version']), ('arch', package['arch'])]:
            if re.findall(r'^' + key + r' = (.+)$', info, re.M) != [expected]:
                raise ValueError(f'Package metadata mismatch: {path.name}: {key}')
        package.update(signature_sha256=hashlib.sha256(signature.read_bytes()).hexdigest(),
                       signer=valid[0].decode('ascii'))
    print(f'build-iso: verified {len(packages)} required repository packages (including dependencies)')
    return sorted(packages, key=lambda p: p['name'])
