"""Isolated TEST ONLY orchestration; external archive/GPG/chroot boundaries only."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

import pytest

from test_portal_package import ROOT, fixture

VERSION = 'candidate-test-only'
PUBLIC = b'-----BEGIN PGP PUBLIC KEY BLOCK-----\nfixture\n-----END PGP PUBLIC KEY BLOCK-----\n'


def isolated_fixture(tmp_path, monkeypatch):
    module, package, signature = fixture(tmp_path, monkeypatch)
    Path(str(package) + '.approval.json').unlink()
    manifest = {'schema': 1, 'mode': 'test-only', 'production_trust': 'pending',
                'build_version': VERSION, 'package_sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
                'primary_fingerprint': 'A' * 40, 'certificate_sha256': hashlib.sha256(PUBLIC).hexdigest()}
    Path(str(package) + '.test-only.json').write_text(json.dumps(manifest))
    Path(str(package) + '.test-only.asc').write_bytes(PUBLIC)
    calls = []
    def gpg(argv, **kwargs):
        calls.append(argv)
        assert argv[0] == 'gpg' and '--import-options' in argv and 'show-only' in argv
        assert '--homedir' in argv and argv[argv.index('--homedir') + 1] != str(Path.home() / '.gnupg')
        return subprocess.CompletedProcess(argv, 0, 'pub:-:255:22:key:0:0:::::\nfpr:::::::::' + 'A' * 40 + ':\n', '')
    monkeypatch.setattr(subprocess, 'run', gpg)
    return module, package, manifest, calls


def test_explicit_test_artifact_stages_public_certificate_without_owner_approval(tmp_path, monkeypatch):
    module, package, manifest, calls = isolated_fixture(tmp_path, monkeypatch)
    record = module['artifact'](package, test_only=True, build_version=VERSION)
    assert 'approval' not in record
    assert record['test_only'] == manifest
    base = tmp_path / 'profile/usr/share/wilsof'
    module['stage'](record, base)
    assert module['embedded'](base, test_only=True, build_version=VERSION)['test_only'] == manifest
    assert (base / 'portal-test-only.json').read_text().strip() == json.dumps(manifest, sort_keys=True)
    assert Path(str(base / 'packages' / module['NAME']) + '.test-only.asc').read_bytes() == PUBLIC
    assert not list(base.rglob('*.approval.json'))
    assert calls


def install_boundary(module, target, monkeypatch):
    """Substitute only native target tools, not the installation policy."""
    from test_portal_trust import status
    calls = []
    original = subprocess.run
    def run(argv, **kwargs):
        if argv[0] == 'gpg':
            return original(argv, **kwargs)  # show-only fixture installed above
        calls.append(argv)
        assert argv[:3] == ['arch-chroot', '-r', str(target)]
        if 'gpg' in argv:
            return subprocess.CompletedProcess(argv, 0, status('A' * 40), '')
        if '-U' in argv:
            binary = target / 'usr/lib/xdg-desktop-portal-hyprland'
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'synthetic ELF')
        out = 'xdg-desktop-portal-hyprland 1.4.1-2.1\n' if '-Q' in argv else 'xdg-desktop-portal-hyprland\n' if '-Qoq' in argv else ''
        return subprocess.CompletedProcess(argv, 0, out, '')
    monkeypatch.setattr(subprocess, 'run', run)
    monkeypatch.setattr(os, 'geteuid', lambda: 0)
    monkeypatch.setattr(Path, 'is_mount', lambda path: path == target)
    return calls


def test_fresh_mounted_target_initializes_only_target_keyring_before_verification(tmp_path, monkeypatch):
    module, package, manifest, _ = isolated_fixture(tmp_path, monkeypatch)
    base = tmp_path / 'live/usr/share/wilsof'
    module['stage'](module['artifact'](package, test_only=True, build_version=VERSION), base)
    target = tmp_path / 'target'
    target.mkdir()
    snapshot = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
    snapshot['stage'](target)
    calls = install_boundary(module, target, monkeypatch)
    module['install'](target, base, test_only=True, build_version=VERSION)
    operations = [call[3:] for call in calls]
    prefix = ['pacman-key', '--gpgdir', '/etc/pacman.d/gnupg']
    assert operations[:4] == [prefix + ['--init'], prefix + ['--populate', 'archlinux'],
                            prefix + ['--add', '/usr/share/wilsof/packages/' + module['NAME'] + '.test-only.asc'],
                            prefix + ['--lsign-key', 'A' * 40]]
    assert operations[4][0] == 'gpg' and '--verify' in operations[4]
    assert next(i for i, op in enumerate(operations) if '-U' in op) > 4
    assert (target / 'etc/pacman.conf').read_text() == snapshot['CONFIG']
    assert json.loads((target / 'usr/share/wilsof/portal-test-only.json').read_text()) == manifest
    for path in ('etc/issue', 'etc/motd'):
        text = (target / path).read_text()
        assert 'TEST ONLY' in text and 'production signing trust pending' in text
    assert Path(str(target / 'usr/share/wilsof/packages' / module['NAME']) + '.test-only.asc').read_bytes() == PUBLIC


@pytest.mark.parametrize('case', ['missing-manifest', 'wrong-fingerprint', 'wrong-cert-hash', 'private-certificate',
                                'production-version', 'version-mismatch', 'duplicate-field', 'owner-approval',
                                'no-opt-in', 'bad-archive', 'missing-signature'])
def test_bad_test_input_never_stages_or_enrolls(tmp_path, monkeypatch, case):
    module, package, manifest, calls = isolated_fixture(tmp_path, monkeypatch)
    path = Path(str(package) + '.test-only.json')
    if case == 'missing-manifest': path.unlink()
    elif case == 'wrong-fingerprint': manifest['primary_fingerprint'] = 'B' * 40
    elif case == 'wrong-cert-hash': manifest['certificate_sha256'] = '0' * 64
    elif case == 'private-certificate':
        Path(str(package) + '.test-only.asc').write_bytes(b'-----BEGIN PGP PRIVATE KEY BLOCK-----\nsecret\n')
        manifest['certificate_sha256'] = hashlib.sha256(Path(str(package) + '.test-only.asc').read_bytes()).hexdigest()
    elif case == 'owner-approval': Path(str(package) + '.approval.json').write_text('{"approval":"owner-approved"}')
    elif case == 'bad-archive': package.write_bytes(b'corrupt')
    elif case == 'missing-signature': Path(str(package) + '.sig').unlink()
    if case != 'missing-manifest': path.write_text(json.dumps(manifest))
    if case == 'duplicate-field': path.write_text(path.read_text()[:-1] + ',"schema":1}')
    version = 'candidate' if case == 'production-version' else 'other-test-only' if case == 'version-mismatch' else VERSION
    base = tmp_path / 'unstaged'
    with pytest.raises(ValueError):
        module['stage'](module['artifact'](package, test_only=case != 'no-opt-in', build_version=version), base)
    assert not base.exists()
    assert all(call[0] == 'gpg' and 'show-only' in call for call in calls)


def test_production_identity_cannot_be_built_with_test_only_version(tmp_path, monkeypatch):
    module, package, _ = fixture(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match='version'):
        module['artifact'](package, build_version=VERSION)


@pytest.mark.parametrize('case', ['missing-marker', 'empty-policy', 'marker-mismatch', 'unmounted', 'root-host',
                                'policy-drift', 'keyring-symlink', 'issue-symlink', 'target-not-fresh', 'no-opt-in'])
def test_invalid_install_context_preserves_target_and_never_enrolls(tmp_path, monkeypatch, case):
    module, package, manifest, _ = isolated_fixture(tmp_path, monkeypatch)
    base = tmp_path / 'live/usr/share/wilsof'
    module['stage'](module['artifact'](package, test_only=True, build_version=VERSION), base)
    target = tmp_path / 'target'
    target.mkdir()
    runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))['stage'](target)
    if case == 'missing-marker': (base / 'portal-test-only.json').unlink()
    elif case == 'empty-policy':
        import shutil
        shutil.rmtree(base)
    elif case == 'marker-mismatch':
        manifest['primary_fingerprint'] = 'B' * 40
        (base / 'portal-test-only.json').write_text(json.dumps(manifest))
    elif case == 'policy-drift': (target / 'etc/pacman.conf').write_text('SigLevel = Never\n')
    elif case in ('keyring-symlink', 'issue-symlink'):
        path = target / ('etc/pacman.d/gnupg' if case == 'keyring-symlink' else 'etc/issue')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(tmp_path / 'must-not-write')
    elif case == 'target-not-fresh':
        (target / 'usr/share/wilsof').mkdir(parents=True, exist_ok=True)
        (target / 'usr/share/wilsof/portal-test-only.json').write_text('sentinel')
    calls = install_boundary(module, target, monkeypatch)
    if case == 'unmounted': monkeypatch.setattr(Path, 'is_mount', lambda path: False)
    before = {str(p.relative_to(target)): p.read_bytes() for p in target.rglob('*') if p.is_file() and not p.is_symlink()}
    with pytest.raises(ValueError):
        module['install'](Path('/') if case == 'root-host' else target, base,
                          test_only=case != 'no-opt-in', build_version=VERSION)
    after = {str(p.relative_to(target)): p.read_bytes() for p in target.rglob('*') if p.is_file() and not p.is_symlink()}
    assert after == before
    assert not calls
    assert not (tmp_path / 'must-not-write').exists()


def test_preparer_binds_test_version_and_persists_public_only_inputs_and_labels(tmp_path, monkeypatch):
    module, package, manifest, _ = isolated_fixture(tmp_path, monkeypatch)
    original = runpy.run_path
    monkeypatch.setattr(runpy, 'run_path', lambda path, *a, **kw:
                        module if str(path).endswith('portal-package.py') else original(path, *a, **kw))
    upstream = tmp_path / 'releng'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    original(str(ROOT / 'scripts/prepare-iso.py'))['prepare'](
        upstream, output, ROOT, 'a' * 40, portal_package=package, portal_test_only=True, build_version=VERSION)
    root = output / 'airootfs'
    base = root / 'usr/share/wilsof'
    assert module['embedded'](base, test_only=True, build_version=VERSION)['test_only'] == manifest
    assert 'TEST ONLY' in (root / 'etc/issue').read_text()
    assert 'TEST ONLY' in (root / 'etc/motd').read_text()
    assert 'Name=Install Wilsof TEST ONLY' in (root / 'usr/share/applications/wilsof-install.desktop').read_text()
    customization = (root / 'root/customize_airootfs.sh').read_text()
    assert "test_only=True" in customization and "build_version='candidate-test-only'" in customization
    assert customization.index("portal['prepare_test_trust']") < customization.index("portal['install']")
    assert not list(base.rglob('*.approval.json'))
    assert module['test_context'](base) == {'test_only': True, 'build_version': VERSION}
    profiledef = (output / 'profiledef.sh').read_text()
    assert 'iso_name="wilsof-test-only"' in profiledef
    assert 'iso_version="candidate-test-only"' in profiledef
    assert '["/usr/share/wilsof/portal-test-only.json"]="0:0:644"' in profiledef
    assert "portal['seal_test_image']" in customization
    (base / 'portal-test-only.json').unlink()
    with pytest.raises(ValueError): module['test_context'](base)


@pytest.mark.parametrize('case', ['valid', 'no-opt-in', 'invalid-opt-in', 'production-version', 'missing-manifest'])
def test_real_build_wrapper_preflight_requires_explicit_test_contract(tmp_path, case):
    from build_fixture import layout
    source, _, _, env = layout(tmp_path)
    portal_module = runpy.run_path(str(ROOT / 'runtime/portal-package.py'))
    old = Path(env['WILSOF_PORTAL_PACKAGE'])
    package = old.with_name(portal_module['NAME'])
    old.rename(package)
    Path(str(old) + '.sig').rename(Path(str(package) + '.sig'))
    env.update(WILSOF_PORTAL_PACKAGE=str(package), WILSOF_PORTAL_TEST_ONLY='1', WILSOF_ISO_VERSION=VERSION)
    manifest = {'schema': 1, 'mode': 'test-only', 'production_trust': 'pending', 'build_version': VERSION,
                'package_sha256': hashlib.sha256(package.read_bytes()).hexdigest(), 'primary_fingerprint': 'A' * 40,
                'certificate_sha256': hashlib.sha256(PUBLIC).hexdigest()}
    Path(str(package) + '.test-only.json').write_text(json.dumps(manifest))
    Path(str(package) + '.test-only.asc').write_bytes(PUBLIC)
    # Real helper, synthetic package identity. Native readers only are replaced.
    helper = (ROOT / 'runtime/portal-package.py').read_text().replace(portal_module['SHA256'], manifest['package_sha256'])
    helper = helper.replace(portal_module['BINARY_SHA256'], hashlib.sha256(b'synthetic ELF').hexdigest())
    (source / 'runtime/portal-package.py').write_text(helper)
    tools = tmp_path / 'tools'
    for name, text in {
        'gpg': "import sys; print('pub:-:255:22:key:0:0:::::'); print('fpr:::::::::' + 'A'*40 + ':')\n",
        'bsdtar': "import sys; sys.stdout.buffer.write(b'pkgname = xdg-desktop-portal-hyprland\\npkgver = 1.4.1-2.1\\narch = x86_64\\n' if sys.argv[-1] == '.PKGINFO' else b'synthetic ELF')\n",
    }.items():
        path = tools / name
        path.write_text('#!' + sys.executable + '\n' + text)
        path.chmod(0o755)
    capture = tmp_path / 'prepare.json'
    with (source / 'scripts/prepare-iso.py').open('a') as stream:
        stream.write('import json\npathlib.Path(' + repr(str(capture)) + ').write_text(json.dumps(sys.argv[1:]))\n')
    if case == 'no-opt-in': env.pop('WILSOF_PORTAL_TEST_ONLY')
    elif case == 'invalid-opt-in': env['WILSOF_PORTAL_TEST_ONLY'] = 'yes'
    elif case == 'production-version': env['WILSOF_ISO_VERSION'] = 'candidate'
    elif case == 'missing-manifest': Path(str(package) + '.test-only.json').unlink()
    result = subprocess.run(['sh', str(source / 'scripts/build-iso.sh'), '--build'], env=env, capture_output=True, text=True)
    if case == 'valid':
        assert result.returncode == 0, result.stderr
        args = json.loads(capture.read_text())
        assert '--portal-test-only' in args
        assert args[args.index('--build-version') + 1] == VERSION
    else:
        assert result.returncode != 0
        assert not capture.exists()
        assert not Path(env['CAPTURE']).exists()
        assert not Path(env['WILSOF_ISO_OUTDIR']).exists()


def test_test_trust_can_be_prepared_before_other_packages_and_reused(tmp_path, monkeypatch):
    module, package, _, _ = isolated_fixture(tmp_path, monkeypatch)
    base = tmp_path / 'live/usr/share/wilsof'
    module['stage'](module['artifact'](package, test_only=True, build_version=VERSION), base)
    target = tmp_path / 'target'
    target.mkdir()
    runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))['stage'](target)
    calls = install_boundary(module, target, monkeypatch)
    module['prepare_test_trust'](target, base, build_version=VERSION)
    assert len(calls) == 4 and all('pacman-key' in call for call in calls)
    module['install'](target, base, test_only=True, build_version=VERSION)
    assert any('-U' in call for call in calls)


@pytest.mark.parametrize('present', [True, False])
def test_signed_hypridle_handoff_preserves_signature_or_refuses_before_writes(tmp_path, monkeypatch, present):
    pin = runpy.run_path(str(ROOT / 'runtime/pinned-package.py'))
    package = tmp_path / pin['PACKAGE_NAME']
    package.write_bytes(b'fixture hypridle')
    pin['verified_package'].__globals__['PACKAGE_SHA256'] = hashlib.sha256(package.read_bytes()).hexdigest()
    pin['install_package'].__globals__['BINARY_SHA256'] = hashlib.sha256(b'fixture executable').hexdigest()
    if present: Path(str(package) + '.sig').write_bytes(b'signed hypridle')
    target = tmp_path / 'target'
    calls = []
    def run(argv, **kwargs):
        calls.append(argv)
        assert Path(str(target / 'usr/share/wilsof/packages' / package.name) + '.sig').read_bytes() == b'signed hypridle'
        binary = target / 'usr/bin/hypridle'
        binary.parent.mkdir(parents=True)
        binary.write_bytes(b'fixture executable')
    monkeypatch.setattr(subprocess, 'run', run)
    if present:
        pin['install_package'](target, tmp_path, require_signature=True)
        assert calls
    else:
        with pytest.raises(ValueError): pin['install_package'](target, tmp_path, require_signature=True)
        assert not target.exists() and not calls


@pytest.mark.parametrize('present', [True, False])
def test_private_compositor_staging_keeps_detached_signature_or_refuses(tmp_path, monkeypatch, present):
    from test_private_hyprland import fixture as private_fixture
    private = runpy.run_path(str(ROOT / 'runtime/private-hyprland.py'))
    package, _, manifest = private_fixture(tmp_path)
    monkeypatch.setitem(private['validate'].__globals__, 'archive', lambda package, member:
                        b'pkgname = hyprland-as02-private\npkgver = 1.0-1\narch = x86_64\n' if member == '.PKGINFO' else b'synthetic executable')
    record = private['validate'](manifest, package)
    if present: Path(str(package) + '.sig').write_bytes(b'signed private compositor')
    base = tmp_path / 'profile'
    if present:
        private['stage'](record, base, require_signature=True)
        assert (base / 'packages/private-hyprland.pkg.tar.zst.sig').read_bytes() == b'signed private compositor'
        target = tmp_path / 'target'
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            if '-U' in argv:
                assert (target / 'usr/share/wilsof/packages/private-hyprland.pkg.tar.zst.sig').read_bytes() == b'signed private compositor'
                binary = target / 'usr/bin/Hyprland'
                binary.parent.mkdir(parents=True)
                binary.write_bytes(b'synthetic executable')
            out = 'hyprland-as02-private 1.0-1' if '-Q' in argv else 'hyprland-as02-private' if '-Qoq' in argv else ''
            return subprocess.CompletedProcess(argv, 0, out, '')
        monkeypatch.setattr(subprocess, 'run', run)
        private['install'](target, base, required=True, require_signature=True)
        assert any('-U' in call for call in calls)
    else:
        with pytest.raises(ValueError): private['stage'](record, base, require_signature=True)
        assert not base.exists()


@pytest.mark.parametrize('missing', [None, 'hypridle', 'private'])
def test_three_package_test_profile_preserves_signatures_and_enrolls_first(tmp_path, monkeypatch, missing):
    from test_private_hyprland import fixture as private_fixture
    module, package, _, _ = isolated_fixture(tmp_path, monkeypatch)
    pin = runpy.run_path(str(ROOT / 'runtime/pinned-package.py'))
    hypridle = tmp_path / pin['PACKAGE_NAME']
    hypridle.write_bytes(b'fixture hypridle')
    pin['verified_package'].__globals__['PACKAGE_SHA256'] = hashlib.sha256(hypridle.read_bytes()).hexdigest()
    Path(str(hypridle) + '.sig').write_bytes(b'signed hypridle')
    private = runpy.run_path(str(ROOT / 'runtime/private-hyprland.py'))
    private_package, contract, _ = private_fixture(tmp_path)
    Path(str(private_package) + '.sig').write_bytes(b'signed private')
    monkeypatch.setenv('WILSOF_PRIVATE_EXPERIMENTAL', '1')
    monkeypatch.setenv('WILSOF_PRIVATE_HYPRLAND_CONTRACT', str(contract))
    monkeypatch.setitem(private['validate'].__globals__, 'archive', lambda package, member:
                        b'pkgname = hyprland-as02-private\npkgver = 1.0-1\narch = x86_64\n' if member == '.PKGINFO' else b'synthetic executable')
    original = runpy.run_path
    modules = {'portal-package.py': module, 'pinned-package.py': pin, 'private-hyprland.py': private}
    monkeypatch.setattr(runpy, 'run_path', lambda path, *a, **kw:
                        modules[Path(path).name] if Path(path).name in modules else original(path, *a, **kw))
    if missing: Path(str(hypridle if missing == 'hypridle' else private_package) + '.sig').unlink()
    upstream = tmp_path / 'releng'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    def prepare():
        original(str(ROOT / 'scripts/prepare-iso.py'))['prepare'](
            upstream, output, ROOT, 'a' * 40, hypridle_package=hypridle, portal_package=package,
            portal_test_only=True, build_version=VERSION)
    if missing:
        with pytest.raises(ValueError): prepare()
        assert not output.exists()
    else:
        prepare()
        packages = output / 'airootfs/usr/share/wilsof/packages'
        assert Path(str(packages / hypridle.name) + '.sig').read_bytes() == b'signed hypridle'
        assert (packages / 'private-hyprland.pkg.tar.zst.sig').read_bytes() == b'signed private'
        script = (output / 'airootfs/root/customize_airootfs.sh').read_text()
        assert script.index("portal['prepare_test_trust']") < script.index("pin['install_package']")
        assert script.index("portal['prepare_test_trust']") < script.index("private['install']")
        assert script.count('require_signature=True') == 2


@pytest.mark.parametrize('case', ['valid', 'missing-marker', 'secret-symlink'])
def test_image_sealing_removes_local_pacman_secrets_but_keeps_public_certificate(tmp_path, monkeypatch, case):
    module, package, _, _ = isolated_fixture(tmp_path, monkeypatch)
    root = tmp_path / 'image'
    base = root / 'usr/share/wilsof'
    module['stage'](module['artifact'](package, test_only=True, build_version=VERSION), base)
    keyring = root / 'etc/pacman.d/gnupg'
    secret = keyring / 'private-keys-v1.d' / ('C' * 40 + '.key')
    secret.parent.mkdir(parents=True)
    secret.write_bytes(b'fixture only; not a key')
    public = keyring / 'pubring.gpg'
    public.write_bytes(b'public fixture')
    calls = []
    original = subprocess.run
    def run(argv, **kwargs):
        if argv[0] == 'gpg': return original(argv, **kwargs)
        calls.append(argv)
        assert argv == ['arch-chroot', '-r', str(root), 'gpgconf', '--homedir', '/etc/pacman.d/gnupg', '--kill', 'gpg-agent']
        return subprocess.CompletedProcess(argv, 0, '', '')
    monkeypatch.setattr(subprocess, 'run', run)
    if case == 'missing-marker': (base / 'portal-test-only.json').unlink()
    elif case == 'secret-symlink':
        secret.unlink()
        secret.symlink_to(public)
    if case == 'valid':
        module['seal_test_image'](root, build_version=VERSION)
        assert not secret.parent.exists()
        assert calls
    else:
        with pytest.raises(ValueError): module['seal_test_image'](root, build_version=VERSION)
        assert not calls
        assert secret.exists()
    assert public.read_bytes() == b'public fixture'
    assert Path(str(base / 'packages' / module['NAME']) + '.test-only.asc').read_bytes() == PUBLIC


def test_fresh_target_entrypoint_enrolls_before_all_three_real_consumers(tmp_path, monkeypatch):
    """Mounted/chroot filesystem paths and native commands are the lab boundary."""
    import shutil
    from test_private_hyprland import fixture as private_fixture
    from test_portal_trust import status
    portal, package, _, _ = isolated_fixture(tmp_path, monkeypatch)
    base = tmp_path / 'live/usr/share/wilsof'
    portal['stage'](portal['artifact'](package, test_only=True, build_version=VERSION), base)
    pin = runpy.run_path(str(ROOT / 'runtime/pinned-package.py'))
    hypridle = base / 'packages' / pin['PACKAGE_NAME']
    hypridle.write_bytes(b'fixture hypridle')
    Path(str(hypridle) + '.sig').write_bytes(b'signed hypridle')
    pin['verified_package'].__globals__['PACKAGE_SHA256'] = hashlib.sha256(hypridle.read_bytes()).hexdigest()
    pin['install_package'].__globals__['BINARY_SHA256'] = hashlib.sha256(b'hypridle binary').hexdigest()
    private = runpy.run_path(str(ROOT / 'runtime/private-hyprland.py'))
    private_package, _, private_manifest = private_fixture(tmp_path)
    Path(str(private_package) + '.sig').write_bytes(b'signed private')
    monkeypatch.setitem(private['validate'].__globals__, 'archive', lambda package, member:
                        b'pkgname = hyprland-as02-private\npkgver = 1.0-1\narch = x86_64\n' if member == '.PKGINFO' else b'synthetic executable')
    private['stage'](private['validate'](private_manifest, private_package), base, require_signature=True)
    source = base / 'source'
    (source / 'runtime').mkdir(parents=True)
    shutil.copy2(ROOT / 'runtime/notices.py', source / 'runtime/notices.py')
    shutil.copytree(ROOT / 'assets/notices', source / 'assets/notices')
    (source / 'bin').mkdir()
    for name in ('wilsof-config-update', 'wilsof-session'):
        (source / 'bin' / name).write_text('# fixture\n')
    target = tmp_path / 'target'
    (target / 'usr/lib').mkdir(parents=True)
    (target / 'usr/lib/os-release').write_text('ID=arch\n')
    (target / 'etc').mkdir()
    (target / 'etc/passwd').write_text('demo:x:1000:1000::/home/demo:/bin/bash\n')
    (target / 'home/demo').mkdir(parents=True)
    snapshot = runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))
    snapshot['stage'](target)
    provision = runpy.run_path(str(ROOT / 'runtime/provision-target'))
    def mapped(value):
        return {'/usr/share/wilsof': base, '/usr/share/wilsof/source': source,
                '/usr/share/wilsof/packages': base / 'packages'}.get(str(value), Path(value))
    monkeypatch.setitem(provision['main'].__globals__, 'Path', mapped)
    monkeypatch.setitem(pin['install_package'].__globals__, 'Path', mapped)
    original_loader = runpy.run_path
    modules = {'portal-package.py': portal, 'pinned-package.py': pin, 'private-hyprland.py': private,
               'repository-snapshot.py': snapshot}
    monkeypatch.setattr(runpy, 'run_path', lambda path, *a, **kw:
                        modules[Path(path).name] if Path(path).name in modules else original_loader(path, *a, **kw))
    original_runner = subprocess.run
    calls = []
    def run(argv, **kwargs):
        if argv[0] == 'gpg': return original_runner(argv, **kwargs)
        calls.append(argv)
        if 'gpg' in argv: return subprocess.CompletedProcess(argv, 0, status('A' * 40), '')
        out = ''
        if '-U' in argv:
            assert any('--lsign-key' in previous for previous in calls[:-1])
            inside = argv[-1]
            assert (target / (inside.lstrip('/') + '.sig')).is_file()
            relative, binary = ('usr/bin/hypridle', b'hypridle binary') if 'hypridle-' in inside else (
                ('usr/bin/Hyprland', b'synthetic executable') if 'private-hyprland' in inside else
                ('usr/lib/xdg-desktop-portal-hyprland', b'synthetic ELF'))
            path = target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(binary)
        elif '-Q' in argv:
            out = argv[-1] + (' 1.0-1' if argv[-1] == 'hyprland-as02-private' else ' 1.4.1-2.1')
        elif '-Qoq' in argv:
            out = 'hyprland-as02-private' if argv[-1] == '/usr/bin/Hyprland' else 'xdg-desktop-portal-hyprland'
        return subprocess.CompletedProcess(argv, 0, out, '')
    monkeypatch.setattr(subprocess, 'run', run)
    monkeypatch.setattr(Path, 'is_mount', lambda path: path == target)
    monkeypatch.setattr(os, 'geteuid', lambda: 0)
    monkeypatch.setattr(sys, 'argv', ['provision-target', str(target), 'demo'])
    provision['main']()
    installs = [command for command in calls if '-U' in command]
    assert len(installs) == 3
    assert (target / 'etc/issue').read_text().startswith(portal['TEST_LABEL'])
    assert portal['test_context'](target / 'usr/share/wilsof')['build_version'] == VERSION


def test_noncanonical_mount_alias_cannot_evade_running_root_guard(tmp_path, monkeypatch):
    module, package, _, _ = isolated_fixture(tmp_path, monkeypatch)
    base = tmp_path / 'live/usr/share/wilsof'
    module['stage'](module['artifact'](package, test_only=True, build_version=VERSION), base)
    (tmp_path / 'mounted').mkdir()
    alias = tmp_path / 'mounted/..'
    runpy.run_path(str(ROOT / 'runtime/repository-snapshot.py'))['stage'](tmp_path)
    monkeypatch.setattr(os, 'geteuid', lambda: 0)
    monkeypatch.setattr(Path, 'is_mount', lambda path: True)
    original = subprocess.run
    calls = []
    def run(argv, **kwargs):
        if argv[0] == 'gpg': return original(argv, **kwargs)
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, '', '')
    monkeypatch.setattr(subprocess, 'run', run)
    with pytest.raises(ValueError, match='anonical'):
        module['prepare_test_trust'](alias, base, build_version=VERSION)
    assert not (tmp_path / 'usr/share/wilsof/packages').exists()
    assert not calls


def test_visible_label_rejects_symlinks_before_modifying_any_notice(tmp_path):
    module = runpy.run_path(str(ROOT / 'runtime/portal-package.py'))
    (tmp_path / 'root/etc').mkdir(parents=True)
    outside = tmp_path / 'outside'
    outside.write_text('preserve outside\n')
    (tmp_path / 'root/etc/issue').write_text('preserve issue\n')
    (tmp_path / 'root/etc/motd').symlink_to(outside)
    with pytest.raises(ValueError): module['label_test_root'](tmp_path / 'root')
    assert outside.read_text() == 'preserve outside\n'
    assert (tmp_path / 'root/etc/issue').read_text() == 'preserve issue\n'
