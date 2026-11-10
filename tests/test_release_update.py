"""Source-only package/process boundary tests; not native pacman acceptance."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from typing import Callable

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'bin/wilsof-release-update'


def load():
    assert HELPER.exists(), 'explicit coherent snapshot-advance helper is missing'
    return runpy.run_path(str(HELPER))


def test_companion_is_in_image_source_allowlist():
    assert 'bin/wilsof-release-update' in (ROOT / 'runtime/image-files.txt').read_text().splitlines()


@pytest.fixture(autouse=True)
def file_modes():
    old = os.umask(0o022)
    yield
    os.umask(old)


@pytest.fixture
def system(tmp_path):
    root = tmp_path / 'root'
    snapshot = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
    snapshot['stage'](root)
    for relative, value in {
        'usr/share/wilsof/source/SOURCE_COMMIT': '1' * 40 + '\n',
        'usr/lib/os-release': 'ID=arch\n',
        'usr/share/wilsof/portal-test-only.json': json.dumps({
            'schema': 1, 'mode': 'test-only', 'production_trust': 'pending',
            'build_version': 'fixture-test-only', 'primary_fingerprint': 'F' * 40,
            'package_sha256': 'd3d2dba441324ed467574ea27f5d2432f7f10cf851e1cc46aaf73bed2d8e7fd0',
            'certificate_sha256': 'a' * 64}),
        'var/lib/pacman/local/demo-1-1/desc': '%NAME%\ndemo\n\n%VERSION%\n1-1\n',
        'etc/pacman.d/gnupg/pubring.gpg': 'public',
        'etc/pacman.d/gnupg/trustdb.gpg': 'trust',
    }.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
    # Ownership is strict even for fixtures, including each ancestor to root.
    for path in [root, *root.rglob('*')]:
        path.chmod(0o755 if path.is_dir() else 0o644)
    return root


class NativeBoundary:
    def __init__(self):
        self.calls = []
        self.installed = 'demo 1-1\n'
        self.fail: Callable[[list[str]], bool] | None = None

    def __call__(self, argv, **kwargs):
        argv = list(map(str, argv)); self.calls.append((argv, kwargs))
        if self.fail and self.fail(argv):
            raise subprocess.CalledProcessError(1, argv)
        out = ''
        if argv[0].endswith('pacman'):
            if '-Q' in argv:
                out = self.installed
            elif '-Sup' in argv:
                out = 'demo\t2-1\tdemo-2-1-x86_64.pkg.tar.zst\t' + hashlib.sha256(b'archive').hexdigest() + '\n'
            elif '-Suw' in argv:
                cache = Path(argv[argv.index('--cachedir') + 1]); cache.mkdir(exist_ok=True)
                (cache / 'demo-2-1-x86_64.pkg.tar.zst').write_bytes(b'archive')
            elif '-Syu' in argv:
                self.installed = 'demo 2-1\n'
        elif argv[0].endswith('bsdtar'):
            out = 'pkgname = demo\npkgver = 2-1\narch = x86_64\ndepend = libc.so=6-64\n'
        elif argv[0].endswith('gpg'):
            out = ('[GNUPG:] NEWSIG\n[GNUPG:] GOODSIG fixture\n'
                   '[GNUPG:] VALIDSIG ' + 'F' * 40 + ' 2026-11-10 1 0 4 0 1 10 00 ' + 'F' * 40 + '\n'
                   '[GNUPG:] TRUST_FULLY 0 pgp\n')
        return subprocess.CompletedProcess(argv, 0, out, '')


def test_plan_is_isolated_and_binds_native_full_upgrade(system, tmp_path):
    api = load(); native = NativeBoundary(); plan = system / 'plan'
    before = (system / 'etc/pacman.conf').read_bytes()
    api['plan'](system, '2026-11-02', plan, run=native)
    record = json.loads((plan / 'manifest.json').read_text())
    assert record['from_date'] == '2026-11-01'
    assert record['target_date'] == '2026-11-02'
    assert record['scope'] == 'test-only' and record['production_trust'] == 'pending'
    assert record['source_commit'] == '1' * 40
    assert record['baseline_sha256'] == hashlib.sha256(b'demo 1-1\n').hexdigest()
    assert record['final_inventory'] == ['demo 2-1']
    assert record['packages'][0]['dependencies'] == ['libc.so=6-64']
    assert record['packages'][0]['sha256'] == hashlib.sha256(b'archive').hexdigest()
    assert (system / 'etc/pacman.conf').read_bytes() == before
    pacman = [argv for argv, _ in native.calls if argv[0].endswith('pacman')]
    assert any('-Sy' in argv and str(plan / 'db') in argv for argv in pacman)
    assert any('-Suw' in argv and str(plan / 'db') in argv for argv in pacman)
    assert not any('-Syu' in argv for argv in pacman)
    assert (plan / 'db/local/demo-1-1/desc').read_bytes() == (system / 'var/lib/pacman/local/demo-1-1/desc').read_bytes()


def proposal(api, system, native):
    folder = system / 'plan'
    api['plan'](system, '2026-11-02', folder, run=native)
    (folder / 'manifest.json.sig').write_bytes(b'detached test boundary')
    native.calls.clear()
    return folder


def test_execute_validates_signed_plan_then_upgrades_then_activates(system):
    api = load(); native = NativeBoundary(); folder = proposal(api, system, native)
    before_source = (system / 'usr/share/wilsof/source/SOURCE_COMMIT').read_bytes()
    api['execute'](system, folder, run=native)
    assert api['policy'](system)['date'] == '2026-11-02'
    assert (system / 'usr/share/wilsof/source/SOURCE_COMMIT').read_bytes() == before_source
    assert json.loads((system / api['STATE'] / 'transaction.json').read_text())['phase'] == 'complete'
    actual = [(argv, kw) for argv, kw in native.calls if '-Syu' in argv]
    assert len(actual) == 1
    argv, kwargs = actual[0]
    assert '--config' in argv and str(folder / 'pacman.conf') in argv
    assert '--noconfirm' not in argv and '--dbpath' not in argv
    assert 'capture_output' not in kwargs  # Pacman's normal terminal review/confirmation.
    assert native.calls[0][0][0] == '/usr/bin/gpg'


@pytest.mark.parametrize('defect', ['bad-signature', 'wrong-primary', 'weak-signature', 'plan-link',
                                    'writable-plan-parent', 'unsafe-output', 'unknown-field',
                                    'unknown-package-field', 'changed-local-constraints', 'changed-final-set',
                                    'solver-abi', 'stale-lock'])
def test_refusal_preserves_policy_before_real_upgrade(system, defect):
    api = load(); native = NativeBoundary(); folder = proposal(api, system, native)
    runner = native
    watched = ['etc/pacman.conf', 'etc/pacman.d/mirrorlist', api['SNAPSHOT'],
               'usr/share/wilsof/source/SOURCE_COMMIT']
    original = {p: (system / p).read_bytes() for p in watched}
    if defect == 'bad-signature':
        native.fail = lambda argv: argv[0].endswith('gpg')
    elif defect == 'wrong-primary':
        marker = system / 'usr/share/wilsof/portal-test-only.json'
        marker.write_text(marker.read_text().replace('F' * 40, 'A' * 40))
    elif defect == 'weak-signature':
        def weak(argv, **kwargs):
            result = native(argv, **kwargs)
            if str(argv[0]).endswith('gpg'):
                result.stdout = result.stdout.replace(' 1 10 00 ', ' 1 2 00 ')
            return result
        runner = weak
    elif defect == 'plan-link':
        path = folder / 'manifest.json'; target = folder / 'other'
        path.rename(target); path.symlink_to(target)
    elif defect == 'writable-plan-parent':
        folder.chmod(0o777)
    elif defect == 'unsafe-output':
        (system / 'etc/pacman.d/mirrorlist').chmod(0o666)
    elif defect in {'unknown-field', 'unknown-package-field', 'changed-final-set'}:
        path = folder / 'manifest.json'; record = json.loads(path.read_text())
        if defect == 'unknown-field': record['extra'] = True
        elif defect == 'unknown-package-field': record['packages'][0]['extra'] = True
        else: record['final_inventory'] = ['demo 9000-1']
        path.write_text(json.dumps(record))
    elif defect == 'changed-local-constraints':
        (system / 'var/lib/pacman/local/demo-1-1/desc').write_text('changed constraints, same version\n')
    elif defect == 'solver-abi':
        native.fail = lambda argv: '-Suw' in argv
    else:
        (system / 'var/lib/pacman/db.lck').write_text('owned elsewhere')
    with pytest.raises((ValueError, OSError, subprocess.SubprocessError)):
        api['execute'](system, folder, run=runner)
    calls = native.calls
    assert not any('-Syu' in argv for argv, _ in calls)
    assert all((system / p).read_bytes() == content for p, content in original.items())


def test_failed_transaction_has_no_retry_and_recovery_requires_completed_set(system):
    api = load(); native = NativeBoundary(); folder = proposal(api, system, native)
    before = (system / 'etc/pacman.conf').read_bytes()
    native.fail = lambda argv: '-Syu' in argv
    with pytest.raises(subprocess.CalledProcessError):
        api['execute'](system, folder, run=native)
    assert (system / 'etc/pacman.conf').read_bytes() == before
    native.fail = None; native.calls.clear()
    with pytest.raises(ValueError, match='explicit'):
        api['execute'](system, folder, run=native)
    with pytest.raises(ValueError, match='incomplete'):
        api['execute'](system, folder, recover=True, run=native)
    assert not any('-Syu' in argv for argv, _ in native.calls)
    # Models a transaction that completed before the wrapper lost completion.
    native.installed = 'demo 2-1\n'
    api['execute'](system, folder, recover=True, run=native)
    assert not any('-Syu' in argv for argv, _ in native.calls)


def test_active_policy_is_signed_and_existing_reader_can_consume_it(system):
    api = load(); native = NativeBoundary(); folder = proposal(api, system, native)
    api['execute'](system, folder, run=native)
    assert api['read_active'](system, run=native)['date'] == '2026-11-02'
    policy = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
    # The real reader loads only a safe installed source companion.
    target = system / 'usr/share/wilsof/source/bin/wilsof-release-update'
    target.parent.mkdir(); target.write_bytes(HELPER.read_bytes()); target.chmod(0o755)
    old_run = subprocess.run
    try:
        subprocess.run = native
        assert policy['read'](system)['date'] == '2026-11-02'
    finally:
        subprocess.run = old_run
    (folder / 'manifest.json').write_text('{}')
    with pytest.raises(ValueError):
        api['read_active'](system, run=native)


def test_cli_help_and_unprivileged_mutation_refusal():
    help_result = subprocess.run([sys.executable, str(HELPER), '--help'], text=True, capture_output=True)
    assert help_result.returncode == 0 and '--recover' in help_result.stdout and '--plan' in help_result.stdout
    if os.geteuid() != 0:
        result = subprocess.run([sys.executable, str(HELPER), '--execute', '/no/such/plan'], text=True, capture_output=True)
        assert result.returncode == 78 and 'root' in result.stderr


@pytest.mark.parametrize('defect', ['unsafe-output', 'unsafe-source', 'unsafe-state', 'malformed-marker', 'unsafe-write-temporary'])
def test_all_guards_precede_trust_and_package_processes(system, defect):
    api = load(); native = NativeBoundary(); folder = proposal(api, system, native)
    if defect == 'unsafe-output':
        (system / 'etc/pacman.d/mirrorlist').chmod(0o666)
    elif defect == 'unsafe-source':
        (system / 'usr/share/wilsof/source/SOURCE_COMMIT').chmod(0o666)
    elif defect == 'unsafe-state':
        state = system / api['STATE']; state.mkdir(); state.chmod(0o777)
    elif defect == 'unsafe-write-temporary':
        (system / 'etc/pacman.conf.new').symlink_to(system / 'etc/pacman.conf')
    else:
        marker = system / 'usr/share/wilsof/portal-test-only.json'
        record = json.loads(marker.read_text()); record['schema'] = 999
        marker.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        api['execute'](system, folder, run=native)
    assert native.calls == []


def test_recovery_rechecks_immutable_source_and_keeps_stale_lock(system):
    api = load(); native = NativeBoundary(); folder = proposal(api, system, native)
    native.fail = lambda argv: '-Syu' in argv
    with pytest.raises(subprocess.CalledProcessError):
        api['execute'](system, folder, run=native)
    native.fail = None; native.installed = 'demo 2-1\n'
    lock = system / 'var/lib/pacman/db.lck'; lock.write_text('manual owner review required')
    with pytest.raises(ValueError, match='lock'):
        api['execute'](system, folder, recover=True, run=native)
    assert lock.read_text() == 'manual owner review required'
    lock.unlink()  # Test owner reviews/releases its own synthetic lock.
    (system / 'usr/share/wilsof/source/SOURCE_COMMIT').write_text('2' * 40 + '\n')
    with pytest.raises(ValueError, match='source'):
        api['execute'](system, folder, recover=True, run=native)
    assert api['policy'](system)['date'] == '2026-11-01'


def test_planning_refuses_package_removals_before_real_upgrade(system):
    api = load(); native = NativeBoundary(); native.installed += 'victim 1-1\n'
    victim = system / 'var/lib/pacman/local/victim-1-1/desc'
    victim.parent.mkdir(); victim.write_text('%NAME%\nvictim\n\n%PROVIDES%\nvictim-abi=1\n\n')
    def replacing(argv, **kwargs):
        result = native(argv, **kwargs)
        if str(argv[0]).endswith('bsdtar'):
            result.stdout += 'conflict = victim-abi\n'
        return result
    with pytest.raises(ValueError, match='removal'):
        api['plan'](system, '2026-11-02', system / 'plan', run=replacing)
    assert api['policy'](system)['date'] == '2026-11-01'
    assert not any('-Syu' in argv for argv, _ in native.calls)


def test_coherent_but_unapproved_current_snapshot_cannot_seed_a_plan(system):
    api = load(); text, mirror, record = api['config']('2026-11-02')
    (system / 'etc/pacman.conf').write_text(text)
    (system / 'etc/pacman.d/mirrorlist').write_text(mirror)
    (system / api['SNAPSHOT']).write_text(json.dumps(record))
    native = NativeBoundary()
    with pytest.raises(ValueError, match='receipt'):
        api['plan'](system, '2026-11-03', system / 'plan', run=native)
    assert native.calls == []


def test_baseline_race_during_download_refuses_before_upgrade(system):
    api = load(); native = NativeBoundary(); folder = proposal(api, system, native)
    def raced(argv, **kwargs):
        result = native(argv, **kwargs)
        if '-Suw' in argv:
            native.installed = 'demo 3-1\n'
        return result
    with pytest.raises(ValueError, match='baseline'):
        api['execute'](system, folder, run=raced)
    assert not any('-Syu' in argv for argv, _ in native.calls)
    assert api['policy'](system)['date'] == '2026-11-01'


def test_source_change_by_transaction_is_not_promoted(system):
    api = load(); native = NativeBoundary(); folder = proposal(api, system, native)
    def changed(argv, **kwargs):
        result = native(argv, **kwargs)
        if '-Syu' in argv:
            (system / 'usr/share/wilsof/source/SOURCE_COMMIT').write_text('2' * 40 + '\n')
        return result
    with pytest.raises(ValueError, match='source'):
        api['execute'](system, folder, run=changed)
    assert api['policy'](system)['date'] == '2026-11-01'


def test_recovery_preserves_unrelated_policy_edits(system):
    api = load(); native = NativeBoundary(); folder = proposal(api, system, native)
    native.fail = lambda argv: '-Syu' in argv
    with pytest.raises(subprocess.CalledProcessError):
        api['execute'](system, folder, run=native)
    native.fail = None; native.installed = 'demo 2-1\n'
    mirror = system / 'etc/pacman.d/mirrorlist'; mirror.write_text('owner-reviewed unrelated policy\n')
    with pytest.raises(ValueError, match='policy'):
        api['execute'](system, folder, recover=True, run=native)
    assert mirror.read_text() == 'owner-reviewed unrelated policy\n'

