"""Exercise the real preflight, substituting only external package tools."""
import base64
import hashlib
from pathlib import Path
import runpy
import subprocess
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def transaction(tmp_path, monkeypatch):
    profile = tmp_path / 'profile'
    profile.mkdir()
    (profile / 'packages.x86_64').write_text('base\n')
    snapshot = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
    snapshot['stage'](profile / 'airootfs')
    (profile / 'pacman.conf').write_text(snapshot['CONFIG'])
    cache, db, keys = [tmp_path / name for name in ('alternative-cache', 'empty-db', 'keys')]
    cache.mkdir()
    keys.mkdir()
    for name in ('pubring.gpg', 'trustdb.gpg'):
        (keys / name).write_bytes(b'public keyring fixture: ' + name.encode())
    (profile / 'BOOT-CONTRACT.json').write_text('{"archiso_major": 91, "early_kms": "wilsof-explicit"}\n')
    calls = []
    state = {'missing': False, 'bad_signature': False, 'wrong_identity': False, 'empty': False, 'archiso': '91-1'}
    data = b'deterministic package fixture, not a real signed Arch package'
    rows = []
    for name in ('base', 'dependency'):
        filename = f'{name}-1-1-any.pkg.tar.zst'
        rows.append('\t'.join((name, '1-1', 'any', filename, hashlib.sha256(data).hexdigest(), base64.b64encode(b'signature fixture').decode(), 'core')))

    def fake_run(argv, **kwargs):
        argv = list(map(str, argv))
        calls.append(argv)
        text = ''
        code = 0
        if argv[0] == 'pacman':
            if '-Sp' in argv:
                text = '' if state['empty'] else '\n'.join(rows) + '\n'
            elif '-Sw' in argv and '--dbpath' in argv and '--needed' not in argv:
                target_cache = Path(argv[argv.index('--cachedir') + 1])
                if not state['missing']:
                    for row in rows:
                        (target_cache / row.split('\t')[3]).write_bytes(data)
            elif '-Sy' in argv:
                sync = Path(argv[argv.index('--dbpath') + 1]) / 'sync'
                sync.mkdir()
                (sync / 'core.db').write_bytes(b'frozen repository database fixture')
            elif '-Q' in argv:
                text = 'archiso ' + state['archiso'] + '\npacman 7.1.0-1\narchlinux-keyring 20260101-1\n'
        elif argv[0] == 'pacman-conf':
            text = str(keys) + '\n' if argv[-1] == 'GPGDir' else Path(argv[argv.index('--config') + 1]).read_text()
        elif argv[0] == 'bsdtar' and '-xOf' in argv:
            filename = Path(argv[argv.index('-xOf') + 1]).name
            name = filename.split('-1-1-')[0]
            text = f'pkgname = {"wrong" if state["wrong_identity"] else name}\npkgver = 1-1\narch = any\n'
        elif argv[0] == 'gpg':
            code = int(state['bad_signature'])
            text = '[GNUPG:] VALIDSIG ' + 'A' * 40 + ' 0 0\n[GNUPG:] TRUST_FULLY 0 pgp\n'
        elif argv[0] == 'zstd':
            code = 1  # Unrelated historical cache file must never be examined.
        if kwargs.get('check') and code:
            raise subprocess.CalledProcessError(code, argv)
        return SimpleNamespace(returncode=code, stdout=text, stderr='')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    return profile, cache, db, keys, calls, state


def invoke(transaction, monkeypatch):
    profile, cache, db, keys, _, _ = transaction
    return runpy.run_path(str(ROOT / 'scripts/package-preflight.py'))['preflight'](profile, cache, db, keys)


def test_full_image_transaction_is_independent_of_host_installed_packages(transaction, monkeypatch):
    invoke(transaction, monkeypatch)
    profile, cache, db, _, calls, _ = transaction
    downloads = [a for a in calls if a[0] == 'pacman' and '-Sw' in a]
    assert len(downloads) == 1
    assert '--needed' not in downloads[0]
    assert downloads[0][downloads[0].index('--config') + 1] == str(profile / 'pacman.conf')
    assert downloads[0][downloads[0].index('--cachedir') + 1] == str(cache)
    assert downloads[0][downloads[0].index('--dbpath') + 1] == str(db)
    verified = [a for a in calls if a[0] == 'gpg']
    assert len(verified) == 2, 'Target and transitive dependency must both be verified'


@pytest.mark.parametrize('failure', [None, 'bad_signature', 'wrong_identity', 'bad_sha256'])
def test_epoch_filename_reaches_unchanged_hash_signature_and_archive_identity_gates(transaction, monkeypatch, failure):
    """Native VM112 zlib filename shape; package/signature bytes here are fixtures."""
    profile, cache, db, keys, calls, state = transaction
    if failure in ('bad_signature', 'wrong_identity'):
        state[failure] = True
    original = subprocess.run
    filename = 'zlib-1:1.3.2-4-x86_64.pkg.tar.zst'
    def epoch_package(argv, **kwargs):
        result = original(argv, **kwargs)
        if argv[0] == 'pacman' and '-Sp' in argv:
            lines = result.stdout.splitlines()
            fields = lines[0].split('\t')
            fields[:4] = ['zlib', '1:1.3.2-4', 'x86_64', filename]
            lines[0] = '\t'.join(fields)
            result.stdout = '\n'.join(lines) + '\n'
        elif argv[0] == 'pacman' and '-Sw' in argv:
            (cache/'base-1-1-any.pkg.tar.zst').rename(cache/filename)
            if failure == 'bad_sha256':
                (cache/filename).write_bytes(b'corrupt epoch package fixture')
        elif argv[0] == 'bsdtar' and '-xOf' in argv and filename in str(argv):
            result.stdout = 'pkgname = ' + ('wrong' if state['wrong_identity'] else 'zlib') + '\npkgver = 1:1.3.2-4\narch = x86_64\n'
        return result
    monkeypatch.setattr(subprocess, 'run', epoch_package)
    if failure:
        with pytest.raises((ValueError, subprocess.CalledProcessError)):
            invoke(transaction, monkeypatch)
        assert any(a[0] == 'pacman' and '-Sw' in a for a in calls), 'Refusal must reach the post-parse integrity gates'
        return
    records = invoke(transaction, monkeypatch)
    zlib = next(p for p in records if p['name'] == 'zlib')
    assert zlib['filename'] == filename and zlib['version'] == '1:1.3.2-4'
    assert zlib['signer'] == 'A'*40
    assert zlib['sha256'] == hashlib.sha256((cache/filename).read_bytes()).hexdigest()
    assert len([a for a in calls if a[0] == 'gpg']) == 2


@pytest.mark.parametrize('version,arch,suffix', [
    ('1-1', 'any', 'zst'), ('1:1.3.2-4', 'x86_64', 'zst'),
    ('3:0.8+r3+g68cd5af-2.1', 'x86_64', 'xz'), ('0:2.0-1', 'any', 'gz'),
])
def test_resolved_parser_preserves_full_epoch_version_and_filename(version, arch, suffix):
    parse = runpy.run_path(str(ROOT/'scripts/package-preflight.py'))['parse_resolved_packages']
    filename = f'example-{version}-{arch}.pkg.tar.{suffix}'
    row = '\t'.join(('example', version, arch, filename, 'a'*64, 'c2ln', 'core'))
    result = parse([row])[0]
    assert result['version'] == version and result['filename'] == filename


@pytest.mark.parametrize('field,value', [
    (0, 'other-name'), (1, '1:1.3.2-5'), (2, 'any'),
    (3, '../zlib-1:1.3.2-4-x86_64.pkg.tar.zst'),
    (3, '/zlib-1:1.3.2-4-x86_64.pkg.tar.zst'),
    (3, 'zlib-1.3.2-4-x86_64.pkg.tar.zst'),
    (3, 'zlib-2:1.3.2-4-x86_64.pkg.tar.zst'),
    (3, 'zlib-1::1.3.2-4-x86_64.pkg.tar.zst'),
    (3, 'zlib-1:1.3.2-4-x86_64.pkg.tar.zst.sig'),
    (3, 'zlib-1:1.3.2-4-x86_64.pkg.tar.zip'),
    (4, 'a'*63), (4, 'A'*64), (4, '../'+'a'*61),
    (6, ''),
])
def test_resolved_parser_rejects_inconsistent_or_unsafe_identity(field, value):
    parse = runpy.run_path(str(ROOT/'scripts/package-preflight.py'))['parse_resolved_packages']
    row = ['zlib', '1:1.3.2-4', 'x86_64', 'zlib-1:1.3.2-4-x86_64.pkg.tar.zst', 'a'*64, 'c2ln', 'core']
    row[field] = value
    with pytest.raises(ValueError, match='Invalid resolved package identity'):
        parse(['\t'.join(row)])


@pytest.mark.parametrize('version', ['x:1.3.2-4', '-1:1.3.2-4', '1::1.3.2-4', '1:1.3.2', '1:../x-1', '1:1.3.2-4/extra'])
def test_resolved_parser_never_repairs_malformed_epoch_or_version(version):
    parse = runpy.run_path(str(ROOT/'scripts/package-preflight.py'))['parse_resolved_packages']
    row = '\t'.join(('zlib',version,'x86_64',f'zlib-{version}-x86_64.pkg.tar.zst','a'*64,'c2ln','core'))
    with pytest.raises(ValueError, match='Invalid resolved package identity'):
        parse([row])


def test_resolved_parser_retains_duplicate_and_private_fallback_guards():
    parse = runpy.run_path(str(ROOT/'scripts/package-preflight.py'))['parse_resolved_packages']
    row = '\t'.join(('zlib','1:1.3.2-4','x86_64','zlib-1:1.3.2-4-x86_64.pkg.tar.zst','a'*64,'c2ln','core'))
    with pytest.raises(ValueError, match='Duplicate'):
        parse([row,row])
    for name in ('hyprland','hyprland-as02-private'):
        bad = '\t'.join((name,'1-1','x86_64',f'{name}-1-1-x86_64.pkg.tar.zst','a'*64,'c2ln','extra'))
        with pytest.raises(ValueError, match='fallback'):
            parse([bad], {'name':'hyprland-as02-private'})


def test_unrelated_corrupt_cache_file_is_ignored(transaction, monkeypatch):
    _, cache, _, _, calls, _ = transaction
    (cache / 'unrelated.pkg.tar.zst').write_bytes(b'corrupt')
    # The legacy block searches a different hard-coded cache: expose the same
    # unrelated file there without touching that host path.
    original = Path.glob
    monkeypatch.setattr(Path, 'glob', lambda p, pattern: iter([cache / 'unrelated.pkg.tar.zst']) if str(p) == '/var/cache/pacman/pkg' else original(p, pattern))
    invoke(transaction, monkeypatch)
    assert not any('unrelated.pkg.tar.zst' in ' '.join(a) for a in calls)
    assert (cache / 'unrelated.pkg.tar.zst').read_bytes() == b'corrupt'


@pytest.mark.parametrize('failure', ['missing', 'bad_signature', 'wrong_identity', 'empty'])
def test_incomplete_or_unverifiable_transaction_fails_closed(transaction, monkeypatch, failure):
    transaction[-1][failure] = True
    with pytest.raises((ValueError, SystemExit, subprocess.CalledProcessError)):
        invoke(transaction, monkeypatch)


def test_freeze_binds_package_closure_databases_policy_and_public_keyring(transaction):
    import json
    profile, _, _, keys, calls, _ = transaction
    (profile / 'BUILD-SOURCE.json').write_text('{"source_commit": "' + 'a' * 40 + '"}\n')
    helper = ROOT / 'scripts/build-inputs.py'
    assert helper.is_file(), 'Build must consume frozen inputs, not live mirrors'
    record = runpy.run_path(str(helper))['freeze'](profile, ROOT, '1767225600', 'fixed')
    frozen = (profile / 'pacman.conf').read_text()
    assert 'https://example.invalid' not in frozen
    assert 'Server = file://' in frozen
    assert 'SigLevel = Required TrustedOnly DatabaseOptional' in frozen
    assert (profile / '.build-inputs/cache/core.db').read_bytes() == b'frozen repository database fixture'
    assert len(record['packages']) == 2
    assert record['tools']['packages'][0] == 'archiso 91-1'
    assert record['configuration'] == {'source_date_epoch': '1767225600', 'iso_version': 'fixed', 'architecture': 'x86_64'}
    assert record['keyring']['pubring.gpg']['sha256'] == hashlib.sha256((keys / 'pubring.gpg').read_bytes()).hexdigest()
    assert all(p['signer'] == 'A' * 40 for p in record['packages'])
    assert json.loads((profile / 'BUILD-INPUTS.json').read_text()) == record
    assert any(a[0] == 'pacman-conf' for a in calls)


def test_freeze_accepts_native_multiline_siglevel_without_changing_private_exception(transaction, monkeypatch):
    """pacman-conf 7.1 emits one SigLevel directive per expanded value."""
    profile = transaction[0]
    (profile / 'BUILD-SOURCE.json').write_text('{}\n')
    original = subprocess.run
    def native_expansion(argv, **kwargs):
        result = original(argv, **kwargs)
        if argv[0] == 'pacman-conf' and argv[-1] != 'GPGDir':
            result.stdout = result.stdout.replace(
                'SigLevel = Required TrustedOnly DatabaseOptional\n',
                'SigLevel = PackageRequired\nSigLevel = PackageTrustedOnly\n'
                'SigLevel = DatabaseOptional\nSigLevel = DatabaseTrustedOnly\n')
            result.stdout = result.stdout.replace('LocalFileSigLevel = Optional\n',
                'LocalFileSigLevel = PackageOptional\nLocalFileSigLevel = PackageTrustedOnly\n')
        return result
    monkeypatch.setattr(subprocess, 'run', native_expansion)
    record = runpy.run_path(str(ROOT / 'scripts/build-inputs.py'))['freeze'](
        profile, ROOT, '1767225600', 'fixed')
    assert len(record['packages']) == 2
    conf = (profile / 'pacman.conf').read_text()
    assert 'SigLevel = PackageRequired\nSigLevel = PackageTrustedOnly\n' in conf
    assert 'LocalFileSigLevel = PackageOptional\nLocalFileSigLevel = PackageTrustedOnly\n' in conf
    snapshot = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
    assert (profile / 'airootfs/etc/pacman.conf').read_text() == snapshot['CONFIG']
    assert len([a for a in transaction[4] if a[0] == 'gpg']) == 2


@pytest.mark.parametrize('bad_policy', [
    'PackageOptional', 'PackageNever', 'PackageTrustAll', 'Optional', 'Never',
    'TrustAll', 'Unknown', 'PackageRequired PackageTrustAll',
])
def test_freeze_rejects_one_weak_repo_before_any_transaction(transaction, monkeypatch, bad_policy):
    profile = transaction[0]
    original = subprocess.run
    def weak_repo(argv, **kwargs):
        result = original(argv, **kwargs)
        if argv[0] == 'pacman-conf' and argv[-1] != 'GPGDir':
            result.stdout += '\n[weak-repository]\nSigLevel = ' + bad_policy + '\n'
        return result
    monkeypatch.setattr(subprocess, 'run', weak_repo)
    with pytest.raises(ValueError, match='signature policy'):
        runpy.run_path(str(ROOT / 'scripts/build-inputs.py'))['freeze'](profile, ROOT, '1', 'fixed')
    assert not (profile / '.build-inputs').exists()
    assert not (profile / 'BUILD-INPUTS.json').exists()
    assert not any(a[0] == 'gpg' or (a[0] == 'pacman' and '-Q' not in a) for a in transaction[4])


@pytest.mark.parametrize('expanded', [
    '', '[core]\nSigLevel = Required TrustedOnly\n',
    '[options]\nSigLevel = PackageRequired\n[core]\nSigLevel = PackageTrustedOnly\n',
    '[options]\nSigLevel = PackageTrustedOnly\n[core]\nSigLevel = PackageRequired\n',
    '[options]\nLocalFileSigLevel = Required TrustedOnly\n[core]\n',
    '[options]\nSigLevel =\n[core]\n',
    '[options]\nSigLevel = Required TrustedOnly\n[options]\n',
])
def test_signature_policy_cannot_borrow_required_flags_from_other_sections(expanded):
    validate = runpy.run_path(str(ROOT / 'scripts/build-inputs.py'))['validate_signature_policy']
    with pytest.raises(ValueError):
        validate(expanded)


def test_signature_policy_keeps_database_optional_and_explicit_local_exception_separate():
    validate = runpy.run_path(str(ROOT / 'scripts/build-inputs.py'))['validate_signature_policy']
    validate('[options]\nSigLevel = PackageRequired\nSigLevel = PackageTrustedOnly\n'
             'SigLevel = DatabaseOptional\nSigLevel = DatabaseTrustedOnly\n'
             'LocalFileSigLevel = PackageOptional\nLocalFileSigLevel = PackageTrustedOnly\n'
             '[core]\n[extra]\nSigLevel = PackageRequired\nSigLevel = PackageTrustedOnly\n')


def test_equivalent_frozen_inputs_have_identical_metadata(transaction):
    import shutil
    profile = transaction[0]
    (profile / 'BUILD-SOURCE.json').write_text('{"source_commit": "' + 'a' * 40 + '"}\n')
    other = profile.with_name('second-profile')
    shutil.copytree(profile, other)
    freeze = runpy.run_path(str(ROOT / 'scripts/build-inputs.py'))['freeze']
    first = freeze(profile, ROOT, '1767225600', 'fixed')
    second = freeze(other, ROOT, '1767225600', 'fixed')
    assert first == second
    assert (profile / 'BUILD-INPUTS.json').read_bytes() == (other / 'BUILD-INPUTS.json').read_bytes()


@pytest.mark.parametrize('kind', ['file', 'symlink', 'dangling'])
def test_freeze_refuses_existing_metadata_without_touching_external_target(transaction, kind):
    profile = transaction[0]
    (profile / 'BUILD-SOURCE.json').write_text('{}\n')
    target = profile.parent / 'external-sentinel'
    if kind != 'dangling':
        target.write_bytes(b'preserve external bytes')
    destination = profile / 'BUILD-INPUTS.json'
    if kind == 'file':
        destination.write_bytes(b'existing input evidence')
    else:
        destination.symlink_to(target)
    with pytest.raises(ValueError, match='reserved provenance'):
        runpy.run_path(str(ROOT / 'scripts/build-inputs.py'))['freeze'](profile, ROOT, '1767225600', 'fixed')
    assert not (profile / '.build-inputs').exists()
    if kind == 'dangling':
        assert not target.exists()
    else:
        assert target.read_bytes() == b'preserve external bytes'


@pytest.mark.parametrize('bad_policy', ['Never', 'Optional', 'Required TrustAll'])
def test_freeze_refuses_weak_package_policy(transaction, bad_policy):
    profile = transaction[0]
    (profile / 'pacman.conf').write_text('[options]\nSigLevel = ' + bad_policy + '\n[core]\nServer = https://example.invalid\n')
    helper = ROOT / 'scripts/build-inputs.py'
    assert helper.is_file()
    with pytest.raises(ValueError, match='signature policy'):
        runpy.run_path(str(helper))['freeze'](profile, ROOT, '1767225600', 'fixed')

@pytest.mark.parametrize('version', ['91-1', '92-1', '93-1', '90-1', '92-invalid+release'])
def test_only_supported_archiso_versions_with_matching_releng_are_accepted(transaction, version):
    import json
    profile = transaction[0]
    transaction[-1]['archiso'] = version
    (profile / 'BUILD-SOURCE.json').write_text('{}\n')
    (profile / 'BOOT-CONTRACT.json').write_text(json.dumps({'archiso_major': int(version.split('-')[0]), 'early_kms': 'wilsof-explicit'}))
    freeze = runpy.run_path(str(ROOT / 'scripts/build-inputs.py'))['freeze']
    if version in ('91-1', '92-1'):
        assert 'archiso ' + version in freeze(profile, ROOT, '1767225600', 'fixed')['tools']['packages']
    else:
        with pytest.raises(ValueError, match='Archiso'):
            freeze(profile, ROOT, '1767225600', 'fixed')
        assert not (profile / '.build-inputs').exists()


def test_tool_releng_mismatch_is_rejected_before_package_resolution(transaction):
    transaction[-1]['archiso'] = '92-1'
    freeze = runpy.run_path(str(ROOT / 'scripts/build-inputs.py'))['freeze']
    with pytest.raises(ValueError, match='releng'):
        freeze(transaction[0], ROOT, '1767225600', 'fixed')
    assert not (transaction[0] / '.build-inputs').exists()

@pytest.mark.parametrize('drift', [False, True])
def test_freeze_records_same_runtime_snapshot_and_rejects_build_mirror_escape(transaction, drift):
    import json
    profile = transaction[0]
    snapshot = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
    snapshot['stage'](profile / 'airootfs')
    (profile / 'pacman.conf').write_text(snapshot['CONFIG'])
    (profile / 'BUILD-SOURCE.json').write_text('{}')
    if drift:
        (profile / 'pacman.conf').write_text(snapshot['CONFIG'].replace('2026/11/01', '2026/11/02'))
    freeze = runpy.run_path(str(ROOT / 'scripts/build-inputs.py'))['freeze']
    if drift:
        with pytest.raises(ValueError, match='snapshot'): freeze(profile, ROOT, '1767225600', 'fixed')
        assert not (profile / '.build-inputs').exists()
    else:
        record = freeze(profile, ROOT, '1767225600', 'fixed')
        assert record['repository_snapshot'] == snapshot['read'](profile / 'airootfs')
        assert record['boot_contract']['archiso_major'] == 91
        assert 'file://' not in (profile / 'airootfs/etc/pacman.conf').read_text()


def test_image_solver_receives_full_private_versioned_constraints(transaction, monkeypatch):
    original = runpy.run_path
    record = {'name': 'hyprland-as02-private', 'dependency_constraints': ['libaquamarine.so=14-64']}
    monkeypatch.setattr(runpy, 'run_path', lambda path, *a, **k: {'embedded': lambda base: record} if str(path).endswith('private-hyprland.py') else original(path, *a, **k))
    invoke(transaction, monkeypatch)
    solve = next(c for c in transaction[4] if '-Sp' in c)
    assert solve[-2:] == ['base', 'libaquamarine.so=14-64']
