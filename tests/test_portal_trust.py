"""Owner approval and real offline OpenPGP fixtures, never production trust."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import shutil
import tempfile
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    return runpy.run_path(str(ROOT / 'runtime/portal-package.py'))


def test_missing_owner_signer_approval_refused_before_archive_inspection(tmp_path, monkeypatch):
    module = api()
    package = tmp_path / module['NAME']
    package.write_bytes(b'fixture')
    Path(str(package) + '.sig').write_bytes(b'fixture signature')
    monkeypatch.setitem(module['artifact'].__globals__, 'SHA256', hashlib.sha256(b'fixture').hexdigest())
    monkeypatch.setitem(module['artifact'].__globals__, 'member', lambda *args: pytest.fail('Unapproved input was inspected'))
    with pytest.raises(ValueError, match='approval'):
        module['artifact'](package)


def status(fingerprint):
    return ('[GNUPG:] NEWSIG\n[GNUPG:] GOODSIG 123 fixture\n'
            f'[GNUPG:] VALIDSIG {fingerprint} 2026-11-10 1794297600 0 4 0 22 8 00 {fingerprint}\n'
            '[GNUPG:] TRUST_FULLY 0 pgp\n')


def test_other_trusted_signer_refused_before_pacman(tmp_path, monkeypatch):
    from test_portal_package import fixture
    module, package, _ = fixture(tmp_path, monkeypatch)
    base = tmp_path / 'live'
    module['stage'](module['artifact'](package), base)
    target = tmp_path / 'target'
    target.mkdir()
    runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))['stage'](target)
    calls = []
    monkeypatch.setattr(os, 'geteuid', lambda: 0)
    def run(argv, **kwargs):
        calls.append(argv)
        if 'gpg' in argv:
            return subprocess.CompletedProcess(argv, 0, status('B' * 40), '')
        if '-U' in argv:
            pytest.fail('Wrong signer reached package mutation')
        return subprocess.CompletedProcess(argv, 0, '', '')
    monkeypatch.setattr(subprocess, 'run', run)
    with pytest.raises(ValueError, match='signer|signature'):
        module['install'](target, base)
    assert any('gpg' in call for call in calls)


def test_unprivileged_consumer_refuses_before_target_writes(tmp_path, monkeypatch):
    from test_portal_package import fixture
    module, package, _ = fixture(tmp_path, monkeypatch)
    base = tmp_path / 'live'
    module['stage'](module['artifact'](package), base)
    target = tmp_path / 'target'
    target.mkdir()
    runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))['stage'](target)
    monkeypatch.setattr(os, 'geteuid', lambda: 1000)
    monkeypatch.setattr(subprocess, 'run', lambda *args, **kwargs: pytest.fail('Unprivileged execution reached tools'))
    with pytest.raises(PermissionError, match='root'):
        module['install'](target, base)
    assert not (target / 'usr/share/wilsof/packages').exists()


@pytest.fixture(scope='module')
def openpgp():
    if not shutil.which('gpg'):
        pytest.skip('Real offline OpenPGP fixture requires gnupg')
    # Short socket paths; keys are disposable test identities, never production.
    with tempfile.TemporaryDirectory(prefix='wg-', dir=os.environ.get('TMPDIR')) as temporary:
        root = Path(temporary)
        homes = [root / name for name in ('sign', 'trusted', 'untrusted', 'empty')]
        for home in homes:
            home.mkdir(mode=0o700)
        def gpg(home, *args, data=None, check=True):
            return subprocess.run(['gpg', '--no-options', '--batch', '--homedir', str(home),
                                   '--no-auto-key-retrieve', '--no-auto-key-import',
                                   '--trust-model', 'pgp', *args], input=data, capture_output=True,
                                  check=check, timeout=30)
        try:
            fingerprints = []
            for index in range(2):
                uid = f'WILSOF TEST ONLY {index} <fixture-{index}@example.invalid>'
                gpg(homes[0], '--pinentry-mode', 'loopback', '--passphrase', '',
                    '--quick-generate-key', uid, 'ed25519', 'cert', '1d')
                rows = gpg(homes[0], '--with-colons', '--list-keys', uid).stdout.decode().splitlines()
                fingerprint = next(row.split(':')[9] for row in rows if row.startswith('fpr:'))
                fingerprints.append(fingerprint)
                gpg(homes[0], '--pinentry-mode', 'loopback', '--passphrase', '',
                    '--quick-add-key', fingerprint, 'ed25519', 'sign', '1d')
                public = gpg(homes[0], '--export', fingerprint).stdout
                for home in homes[1:3]:
                    gpg(home, '--import', data=public)
                gpg(homes[1], '--import-ownertrust', data=f'{fingerprint}:6:\n'.encode())
            yield {'root': root, 'homes': homes, 'fingerprints': fingerprints, 'gpg': gpg}
        finally:
            for home in homes:
                subprocess.run(['gpgconf', '--homedir', str(home), '--kill', 'all'], capture_output=True, timeout=15)


@pytest.mark.parametrize('case', ['valid', 'modified', 'untrusted', 'missing', 'incorrect-key', 'unknown-key', 'expired'])
def test_real_offline_openpgp_accepts_only_exact_trusted_signer(openpgp, tmp_path, case):
    state = openpgp
    package = tmp_path / 'fixture.pkg'
    package.write_bytes(b'WILSOF TEST ONLY package bytes\n')
    signature = tmp_path / 'fixture.pkg.sig'
    signer = state['fingerprints'][1 if case == 'incorrect-key' else 0]
    state['gpg'](state['homes'][0], '--pinentry-mode', 'loopback', '--passphrase', '',
                 '--local-user', signer, '--digest-algo', 'SHA256', '--output', str(signature),
                 '--detach-sign', str(package))
    if case == 'modified':
        package.write_bytes(b'altered package')
    if case == 'missing':
        signature.unlink()
    home = state['homes'][2] if case == 'untrusted' else state['homes'][3] if case == 'unknown-key' else state['homes'][1]
    args = ['--status-fd', '1']
    if case == 'expired':
        args += ['--faked-system-time', str(int(time.time()) + 172800)]
    proof = state['gpg'](home, *args, '--verify', str(signature), str(package), check=False)
    def accepted():
        if proof.returncode:
            raise ValueError('OpenPGP verification failed')
        return api()['signature_status'](proof.stdout.decode(), state['fingerprints'][0])
    if case == 'valid':
        result = accepted()
        assert result['primary_fingerprint'] == state['fingerprints'][0]
        assert result['signing_fingerprint'] != result['primary_fingerprint']
    else:
        with pytest.raises(ValueError):
            accepted()


@pytest.mark.parametrize('bad', ['BADSIG', 'REVKEYSIG', 'EXPKEYSIG', 'TRUST_UNDEFINED', 'TRUST_MARGINAL', 'ERROR'])
def test_validsig_is_not_itself_trust_or_revocation_acceptance(bad):
    with pytest.raises(ValueError):
        api()['signature_status'](status('A' * 40) + f'[GNUPG:] {bad} fixture\n', 'A' * 40)


@pytest.mark.parametrize('bad', ['lowercase', 'short', 'duplicate', 'wrong-hash', 'schema-bool', 'not-approved', 'symlink'])
def test_malformed_owner_approval_refused_without_staging(tmp_path, monkeypatch, bad):
    from test_portal_package import fixture
    module, package, _ = fixture(tmp_path, monkeypatch)
    path = Path(str(package) + '.approval.json')
    record = json.loads(path.read_text())
    if bad == 'lowercase': record['primary_fingerprint'] = 'a' * 40
    elif bad == 'short': record['primary_fingerprint'] = 'A' * 16
    elif bad == 'wrong-hash': record['package_sha256'] = '0' * 64
    elif bad == 'schema-bool': record['schema'] = True
    elif bad == 'not-approved': record['approval'] = 'pending'
    path.write_text(json.dumps(record))
    if bad == 'duplicate': path.write_text(path.read_text()[:-1] + ',"schema":1}')
    elif bad == 'symlink':
        saved = path.with_suffix('.saved'); path.rename(saved); path.symlink_to(saved)
    base = tmp_path / 'output'
    with pytest.raises(ValueError, match='approval'):
        module['stage'](module['artifact'](package), base)
    assert not base.exists()


@pytest.mark.parametrize('case', ['valid', 'untrusted', 'incorrect-key', 'signature-corrupt'])
def test_consumer_runs_real_gpg_before_substituted_pacman(openpgp, tmp_path, monkeypatch, case):
    from test_portal_package import fixture
    module, package, signature = fixture(tmp_path, monkeypatch)
    state = openpgp
    signature.unlink()
    state['gpg'](state['homes'][0], '--pinentry-mode', 'loopback', '--passphrase', '',
        '--local-user', state['fingerprints'][case == 'incorrect-key'], '--digest-algo', 'SHA256',
        '--output', str(signature), '--detach-sign', str(package))
    if case == 'signature-corrupt': signature.write_bytes(b'invalid signature')
    approval = Path(str(package) + '.approval.json')
    record = json.loads(approval.read_text()); record['primary_fingerprint'] = state['fingerprints'][0]
    approval.write_text(json.dumps(record))
    base = tmp_path / 'live'
    module['stage'](module['artifact'](package), base)
    target = tmp_path / 'target'; target.mkdir()
    runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))['stage'](target)
    original = subprocess.run
    calls = []
    home = state['homes'][2 if case == 'untrusted' else 1]
    def run(argv, **kwargs):
        calls.append(argv)
        if 'gpg' in argv:
            args = argv[3:]
            args[args.index('--homedir') + 1] = str(home)
            args[-2:] = [str(target / path.lstrip('/')) for path in args[-2:]]
            return original(args, **kwargs)
        if '-U' in argv:
            assert any('gpg' in previous for previous in calls[:-1])
            binary = target / 'usr/lib/xdg-desktop-portal-hyprland'
            binary.parent.mkdir(parents=True); binary.write_bytes(b'synthetic ELF')
        out = 'xdg-desktop-portal-hyprland 1.4.1-2.1\n' if '-Q' in argv else 'xdg-desktop-portal-hyprland\n' if '-Qoq' in argv else ''
        return subprocess.CompletedProcess(argv, 0, out, '')
    monkeypatch.setattr(os, 'geteuid', lambda: 0)
    monkeypatch.setattr(subprocess, 'run', run)
    if case == 'valid':
        module['install'](target, base)
        assert any('-U' in command for command in calls)
    else:
        with pytest.raises((ValueError, subprocess.CalledProcessError)):
            module['install'](target, base)
        assert not any('-U' in command for command in calls)
        assert not (target / 'usr/lib/xdg-desktop-portal-hyprland').exists()


def test_orphaned_approval_refuses_repository_fallback(tmp_path):
    module = api()
    package = tmp_path / 'packages' / module['NAME']
    package.parent.mkdir()
    Path(str(package) + '.approval.json').write_text('{}')
    with pytest.raises(ValueError):
        module['embedded'](tmp_path)
