"""Read-only artifact provenance checks; fixtures are not boot/ISO acceptance."""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / 'scripts/audit-iso.py'
    assert path.is_file(), 'Missing read-only immutable ISO audit entrypoint'
    return runpy.run_path(str(path))


def test_payload_is_compared_to_independent_git_bytes_not_only_embedded_hashes():
    api = load()
    commit = 'a' * 40
    source = {'runtime/image-files.txt': b'bin/wilsof\n', 'bin/wilsof': b'reviewed bytes\n'}
    payload = {'bin/wilsof': source['bin/wilsof'], 'SOURCE_COMMIT': (commit + '\n').encode()}
    files = {'usr/share/wilsof/source/' + name: data for name, data in payload.items()}
    files['usr/share/wilsof/source/FILES.sha256.json'] = json.dumps({
        name: hashlib.sha256(data).hexdigest() for name, data in payload.items()
    }).encode()
    result = api['audit_payload'](files.__getitem__, source.__getitem__, commit)
    assert result['source_commit'] == commit
    assert result['verified_files'] == 1
    # An attacker can rewrite both a payload and its embedded checksum; Git is independent.
    files['usr/share/wilsof/source/bin/wilsof'] = b'changed bytes\n'
    sums = json.loads(files['usr/share/wilsof/source/FILES.sha256.json'])
    sums['bin/wilsof'] = hashlib.sha256(b'changed bytes\n').hexdigest()
    files['usr/share/wilsof/source/FILES.sha256.json'] = json.dumps(sums).encode()
    with pytest.raises(ValueError, match='payload'):
        api['audit_payload'](files.__getitem__, source.__getitem__, commit)


@pytest.fixture
def data_iso(tmp_path):
    # Real data-only ISO/SquashFS fixture. It deliberately is NOT bootable.
    if not all(shutil.which(tool) for tool in ('mksquashfs', 'xorriso', 'unsquashfs')):
        pytest.skip('Read-only ISO tooling not installed')
    root = tmp_path / 'root'
    root.mkdir()
    (root / 'regular file').write_bytes(b'actual squashfs data\n')
    (root / 'link').symlink_to('/etc/passwd')
    iso_tree = tmp_path / 'tree/arch/x86_64'
    iso_tree.mkdir(parents=True)
    subprocess.run(['mksquashfs', str(root), str(iso_tree / 'airootfs.sfs'),
                    '-noappend', '-no-progress', '-processors', '1'],
                   check=True, capture_output=True)
    iso = tmp_path / 'data-only.iso'
    subprocess.run(['xorriso', '-as', 'mkisofs', '-quiet', '-o', str(iso),
                    '-R', str(tmp_path / 'tree')], check=True, capture_output=True)
    return iso, hashlib.sha256(iso.read_bytes()).hexdigest()


def test_real_read_only_tools_require_hash_and_refuse_symlink_reads(data_iso):
    iso, digest = data_iso
    api = load()
    with pytest.raises(ValueError, match='SHA256'):
        api['Image'](iso, '0' * 64)
    image = api['Image'](iso, digest)
    assert image.read('regular file') == b'actual squashfs data\n'
    assert image.squashfs['bytes'] > 0
    assert len(image.squashfs['sha256']) == 64
    with pytest.raises(ValueError, match='regular'):
        image.read('link')
    with pytest.raises(ValueError, match='path'):
        image.read('../etc/passwd')
    assert hashlib.sha256(iso.read_bytes()).hexdigest() == digest


def test_package_inventory_comes_from_real_desc_content():
    api = load()
    class Fixture:
        entries = {'var/lib/pacman/local/linux-1-1/desc': {'mode': '-rw-r--r--'}}
        def read(self, name):
            return b'%NAME%\nlinux\n\n%VERSION%\n1-1\n\n%LICENSE%\nGPL-2.0-only\n\n'
    assert api['package_inventory'](Fixture()) == {
        'linux': {'version': '1-1', 'licenses': ['GPL-2.0-only']}}


@pytest.mark.parametrize('path', ['var/lib/dkms/mok.key', 'root/.ssh/id_ed25519',
                                  'home/qa/.config/private', 'root/.env'])
def test_metadata_scan_finds_private_material_without_reading_it(path):
    api = load()
    entries = {path: {'mode': '-rw-------'}}
    with pytest.raises(ValueError, match='private'):
        api['audit_private_paths'](entries)
    # An empty SSH directory, public keys and system skeleton files are not secrets.
    assert api['audit_private_paths']({'root/.ssh': {'mode': 'drwx------'},
                                      'usr/share/keyrings/arch.gpg': {'mode': '-rw-r--r--'}})['files_scanned'] == 1


def test_cli_rejects_wrong_hash_without_creating_output(data_iso, tmp_path):
    iso, digest = data_iso
    output = tmp_path / 'evidence'
    result = subprocess.run(['python3', str(ROOT / 'scripts/audit-iso.py'),
                             '--iso', str(iso), '--sha256', '0' * 64,
                             '--commit', 'a' * 40, '--source', str(ROOT),
                             '--output', str(output)], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'SHA256' in result.stderr
    assert not output.exists()


@pytest.mark.parametrize('defect', ['wrong-commit', 'missing-file', 'extra-hash',
                                   'unsafe-path', 'duplicate-json-key'])
def test_payload_refuses_malformed_identity_or_receipt(defect):
    api = load()
    commit = 'b' * 40
    source = {'runtime/image-files.txt': b'bin/wilsof\n', 'bin/wilsof': b'reviewed\n'}
    files = {'SOURCE_COMMIT': (commit + '\n').encode(), 'bin/wilsof': source['bin/wilsof']}
    sums = {name: hashlib.sha256(value).hexdigest() for name, value in files.items()}
    if defect == 'wrong-commit':
        files['SOURCE_COMMIT'] = b'c' * 40 + b'\n'
    elif defect == 'missing-file':
        files['bin/wilsof'] = b''
    elif defect == 'extra-hash':
        sums['unapproved-file'] = '0' * 64
    elif defect == 'unsafe-path':
        source['runtime/image-files.txt'] = b'../outside\n'
    receipt = json.dumps(sums)
    if defect == 'duplicate-json-key':
        receipt = receipt[:-1] + ', "bin/wilsof": "' + sums['bin/wilsof'] + '"}'
    files['FILES.sha256.json'] = receipt.encode()
    def read(name):
        return files[name.removeprefix('usr/share/wilsof/source/')]
    with pytest.raises(ValueError):
        api['audit_payload'](read, source.__getitem__, commit)


def test_reader_detects_changed_artifact_and_bounds_tools(data_iso):
    iso, digest = data_iso
    api = load()
    image = api['Image'](iso, digest)
    image.verify_unchanged()
    image.deadline = 0
    with pytest.raises(TimeoutError):
        image.read('regular file')
    with iso.open('ab') as stream:
        stream.write(b'changed disposable fixture')
    with pytest.raises(ValueError, match='changed'):
        image.verify_unchanged()


@pytest.mark.parametrize('value', ['../escape', '/absolute', './dot', 'repeated//slash',
                                 'trailing/', 'line\nbreak'])
def test_ambiguous_paths_are_rejected(value):
    with pytest.raises(ValueError, match='path'):
        load()['relative_path'](value)


def test_cli_never_overwrites_existing_evidence(data_iso, tmp_path):
    iso, digest = data_iso
    output = tmp_path / 'preserved'
    output.mkdir()
    sentinel = output / 'audit.json'
    sentinel.write_bytes(b'preserved earlier evidence')
    commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    result = subprocess.run(['python3', str(ROOT / 'scripts/audit-iso.py'),
                             '--iso', str(iso), '--sha256', digest, '--commit', commit,
                             '--source', str(ROOT), '--output', str(output)],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert sentinel.read_bytes() == b'preserved earlier evidence'
