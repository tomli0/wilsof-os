#!/usr/bin/env python3
"""Read-only Wilsof ISO evidence; never boot, mount, install or execute image code."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time


def command(argv, *, timeout=60.0):
    return subprocess.run(list(map(str, argv)), check=True, capture_output=True,
                          timeout=timeout, env=dict(os.environ, LC_ALL='C', TZ='UTC')).stdout


def hash_region(path, offset=0, size=None):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        stream.seek(offset)
        remaining = stream.seek(0, 2) - offset if size is None else size
        stream.seek(offset)
        while remaining:
            data = stream.read(min(8 * 1024 * 1024, remaining))
            if not data:
                raise ValueError('Truncated ISO extent')
            digest.update(data)
            remaining -= len(data)
    return digest.hexdigest()


class Image:
    """Read exact regular SFS members using host tools, with no filesystem extraction."""

    def __init__(self, iso, expected_sha256):
        self.iso = Path(iso).absolute()
        if not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
            raise ValueError('Exact expected ISO SHA256 required')
        if not stat.S_ISREG(self.iso.lstat().st_mode):
            raise ValueError('ISO must be a regular non-symlink file')
        self.identity = self.iso.stat()
        if hash_region(self.iso) != expected_sha256:
            raise ValueError('ISO SHA256 differs from independently expected artifact')
        self.sha256 = expected_sha256
        self.deadline = time.monotonic() + 900
        layout = self.run(['xorriso', '-indev', self.iso, '-find',
                           '/arch/x86_64/airootfs.sfs', '-exec', 'report_lba', '--']).decode()
        rows = re.findall(r'^File data lba:\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,.*$',
                          layout, re.M)
        if len(rows) != 1 or rows[0][0] != '0':
            raise ValueError('Expected one contiguous SquashFS extent')
        _, lba, blocks, size = map(int, rows[0])
        self.offset = lba * 2048
        if size <= 0 or size > blocks * 2048 or self.offset + size > self.identity.st_size:
            raise ValueError('Invalid SquashFS extent bounds')
        self.squashfs = {'offset': self.offset, 'bytes': size,
                         'sha256': hash_region(self.iso, self.offset, size)}
        listing = self.run(['unsquashfs', '-no-progress', '-processors', '1',
                            '-o', self.offset, '-lln', '-UTC', self.iso]).decode()
        self.entries = {}
        for line in listing.splitlines():
            match = re.fullmatch(r'([dlbcp s-][rwxstST-]{9})\s+(\d+)/(\d+)\s+(\d+)\s+'
                                 r'\d{4}-\d\d-\d\d\s+\d\d:\d\d\s+squashfs-root/(.+)', line)
            if not match:
                # The root entry itself has no slash. Reject unparsed descendants.
                if ' squashfs-root/' in line:
                    raise ValueError('Unrecognized SquashFS metadata')
                continue
            mode, uid, gid, size, name = match.groups()
            target = None
            if mode[0] == 'l':
                name, target = name.split(' -> ', 1)
            relative_path(name)
            if name in self.entries:
                raise ValueError('Duplicate SquashFS path')
            self.entries[name] = {'mode': mode, 'uid': int(uid), 'gid': int(gid),
                                  'bytes': int(size), 'target': target}

    def run(self, argv):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('ISO audit exceeded 900-second tool budget')
        return command(argv, timeout=min(60, remaining))

    def read(self, name):
        relative_path(name)
        entry = self.entries.get(name)
        if not entry or entry['mode'][0] != '-':
            raise ValueError('Expected regular immutable file: ' + name)
        if entry['bytes'] > 32 * 1024 * 1024:
            raise ValueError('Immutable inspection member exceeds 32 MiB bound')
        for parent in PurePosixPath(name).parents:
            if str(parent) != '.' and self.entries.get(str(parent), {}).get('mode', '')[:1] != 'd':
                raise ValueError('Non-directory immutable ancestor')
        data = self.run(['unsquashfs', '-no-progress', '-processors', '1',
                         '-o', self.offset, '-no-wildcards', '-cat', self.iso, name])
        if len(data) != entry['bytes']:
            raise ValueError('Immutable member length differs from metadata')
        return data

    def verify_unchanged(self):
        now = self.iso.stat()
        if ((now.st_dev, now.st_ino, now.st_size, now.st_mtime_ns, now.st_ctime_ns)
                != (self.identity.st_dev, self.identity.st_ino, self.identity.st_size,
                    self.identity.st_mtime_ns, self.identity.st_ctime_ns)
                or hash_region(self.iso) != self.sha256):
            raise ValueError('ISO changed during read-only audit')


def relative_path(value):
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or '..' in path.parts
            or str(path) != value or any(ord(c) < 32 for c in value)):
        raise ValueError('Invalid payload path')
    return value


def audit_payload(read, source_blob, commit):
    """Compare every allowlisted byte to Git, independently of the image's receipt."""
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Exact source commit required')
    prefix = 'usr/share/wilsof/source/'
    expected_marker = (commit + '\n').encode()
    if read(prefix + 'SOURCE_COMMIT') != expected_marker:
        raise ValueError('Image source commit differs from expected source')
    paths = source_blob('runtime/image-files.txt').decode().splitlines()
    if not paths or len(paths) != len(set(paths)):
        raise ValueError('Invalid payload manifest')
    expected = {'SOURCE_COMMIT': hashlib.sha256(expected_marker).hexdigest()}
    for name in paths:
        relative_path(name)
        data = source_blob(name)
        expected[name] = hashlib.sha256(data).hexdigest()
        if read(prefix + name) != data:
            raise ValueError('Image payload differs from independent source: ' + name)
    def unique_object(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError('Duplicate payload checksum key')
        return result

    embedded = json.loads(read(prefix + 'FILES.sha256.json'), object_pairs_hook=unique_object)
    if embedded != expected:
        raise ValueError('Image payload checksum manifest differs from source')
    return {'source_commit': commit, 'verified_files': len(paths), 'sha256': expected}


def package_inventory(image):
    result = {}
    for name in sorted(image.entries):
        if not re.fullmatch(r'var/lib/pacman/local/[^/]+/desc', name):
            continue
        raw = image.read(name).decode()
        fields = dict(re.findall(r'^%([A-Z0-9_]+)%\n(.*?)(?=\n\n|\Z)', raw, re.M | re.S))
        package, version = fields.get('NAME', ''), fields.get('VERSION', '')
        if (not re.fullmatch(r'[A-Za-z0-9@_+.-]+', package) or not version
                or '\n' in version or package in result):
            raise ValueError('Invalid or duplicate immutable package metadata')
        result[package] = {'version': version, 'licenses': fields.get('LICENSE', '').splitlines()}
    if not result:
        raise ValueError('Immutable package inventory missing')
    return result


def audit_private_paths(entries):
    """Scoped filename scan, NOT a complete content/security audit. Never read secrets."""
    scanned = 0
    for name, entry in entries.items():
        if entry['mode'].startswith('d'):
            continue
        scanned += 1
        parts = PurePosixPath(name).parts
        if (name.startswith('home/') or '.git' in parts or '.ssh' in parts
                or '.aws' in parts or '.env' in parts or 'private-keys-v1.d' in parts
                or name in {'var/lib/dkms/mok.key', 'var/lib/dkms/mok.pub'}
                or re.fullmatch(r'etc/ssh/ssh_host_.*_key', name)):
            raise ValueError('Unexpected private material path; inspect privately: ' + name)
    return {'files_scanned': scanned, 'scope': 'known private filenames only; not full security clearance'}


def audit(iso, expected_sha256, source, commit, output):
    # Authenticate the artifact before creating any evidence output.
    image = Image(iso, expected_sha256)
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Exact source commit required')
    source, output = Path(source).resolve(strict=True), Path(output).absolute()
    actual = command(['git', '-C', source, 'rev-parse', '--verify', commit + '^{commit}']).decode().strip()
    if actual != commit:
        raise ValueError('Independent Git commit does not match requested source')
    if output.resolve().is_relative_to(source) or any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError('Evidence must be outside source and without symlink ancestors')
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    report = {'schema': 1, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'iso': {'filename': image.iso.name, 'bytes': image.identity.st_size, 'sha256': image.sha256},
              'squashfs': image.squashfs, 'expected_source': commit,
              'scope': 'read-only artifact provenance and scoped inventory, not acceptance',
              'boot_install_physical_acceptance': 'NOT RUN', 'checks': {}}

    def source_blob(name):
        relative_path(name)
        return command(['git', '-C', source, 'show', commit + ':' + name])

    def check(name, operation):
        try:
            report['checks'][name] = {'status': 'PASS', 'evidence': operation()}
        except (ValueError, OSError, subprocess.SubprocessError, TimeoutError) as error:
            report['checks'][name] = {'status': 'FAIL', 'error': str(error)}

    def payload():
        result = audit_payload(image.read, source_blob, commit)
        expected = set(result['sha256']) | {'FILES.sha256.json'}
        prefix = 'usr/share/wilsof/source/'
        actual_paths = {name[len(prefix):] for name, entry in image.entries.items()
                        if name.startswith(prefix) and not entry['mode'].startswith('d')}
        if actual_paths != expected:
            raise ValueError('Unexpected or absent immutable source payload members')
        return result

    check('independent_source_payload', payload)
    check('package_inventory', lambda: package_inventory(image))
    check('scoped_private_path_scan', lambda: audit_private_paths(image.entries))
    check('unchanged_iso', lambda: (image.verify_unchanged(), {'sha256': image.sha256})[1])
    report['status'] = 'PASS' if all(row['status'] == 'PASS' for row in report['checks'].values()) else 'FAIL'
    path = output / 'audit.json'
    with path.open('x') as stream:
        os.chmod(path, 0o600)
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--source', type=Path, required=True, help='Independent Git checkout; dirty files are not read')
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True, help='New private directory outside the source tree')
    args = parser.parse_args()
    try:
        report = audit(args.iso, args.sha256, args.source, args.commit, args.output)
    except (ValueError, OSError, subprocess.SubprocessError, TimeoutError) as error:
        print('audit-iso: ' + str(error), file=sys.stderr)
        return 1
    print('Static audit ' + report['status'] + '; evidence: ' + str(args.output / 'audit.json'))
    print('Boot/install/physical acceptance: NOT RUN. This is not full security or release clearance.')
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
