"""Synthetic-only private compositor contract; never install real packages."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    path = ROOT / 'runtime/private-hyprland.py'
    assert path.is_file(), 'Missing private Hyprland input contract'
    return runpy.run_path(str(path))


def fixture(tmp_path):
    package = tmp_path / 'synthetic.pkg.tar.zst'
    package.write_bytes(b'synthetic archive, never a private artifact')
    record = dict(schema=1, package=str(package), name='hyprland-as02-private',
                  version='1.0-1', architecture='x86_64',
                  sha256=hashlib.sha256(package.read_bytes()).hexdigest(),
                  binary_sha256=hashlib.sha256(b'synthetic executable').hexdigest())
    contract = tmp_path / 'contract.json'
    contract.write_text(json.dumps(record))
    return package, contract, record


def test_valid_input_requires_explicit_opt_in_and_exact_identity(tmp_path, monkeypatch):
    module = api()
    package, contract, record = fixture(tmp_path)
    monkeypatch.setitem(module['load'].__globals__, 'archive', lambda p, member: (
        b'pkgname = hyprland-as02-private\npkgver = 1.0-1\narch = x86_64\ndepend = wayland>=1\n'
        if member == '.PKGINFO' else b'synthetic executable'))
    loaded = module['load']({'WILSOF_PRIVATE_EXPERIMENTAL': '1',
                             'WILSOF_PRIVATE_HYPRLAND_CONTRACT': str(contract)})
    assert loaded['sha256'] == record['sha256']
    assert loaded['dependencies'] == ['wayland']
    assert module['load']({}) is None


@pytest.mark.parametrize('bad', ['opt-in', 'missing-contract', 'missing-package',
                                'sha256', 'name', 'version', 'architecture',
                                'malformed', 'symlink', 'binary'])
def test_invalid_input_fails_closed(tmp_path, monkeypatch, bad):
    module = api()
    package, contract, record = fixture(tmp_path)
    env = {'WILSOF_PRIVATE_EXPERIMENTAL': '1', 'WILSOF_PRIVATE_HYPRLAND_CONTRACT': str(contract)}
    metadata = 'pkgname = hyprland-as02-private\npkgver = 1.0-1\narch = x86_64\n'
    if bad == 'opt-in': env.pop('WILSOF_PRIVATE_EXPERIMENTAL')
    elif bad == 'missing-contract': contract.unlink()
    elif bad == 'missing-package': package.unlink()
    elif bad == 'sha256': record['sha256'] = '0' * 64
    elif bad == 'name': metadata = metadata.replace('hyprland-as02-private', 'unexpected')
    elif bad == 'version': metadata = metadata.replace('1.0-1', '2.0-1')
    elif bad == 'architecture': metadata = metadata.replace('x86_64', 'aarch64')
    elif bad == 'malformed': record['sha256'] = 'invalid'
    elif bad == 'symlink':
        original = tmp_path / 'original'; package.rename(original); package.symlink_to(original)
    elif bad == 'binary': record['binary_sha256'] = '0' * 64
    if contract.exists(): contract.write_text(json.dumps(record))
    monkeypatch.setitem(module['load'].__globals__, 'archive',
                        lambda p, member: metadata.encode() if member == '.PKGINFO' else b'synthetic executable')
    with pytest.raises(ValueError, match='Private Hyprland'):
        module['load'](env)


def configure(tmp_path, monkeypatch):
    package, contract, record = fixture(tmp_path)
    monkeypatch.setenv('WILSOF_PRIVATE_EXPERIMENTAL', '1')
    monkeypatch.setenv('WILSOF_PRIVATE_HYPRLAND_CONTRACT', str(contract))
    original = runpy.run_path
    def load(path, *args, **kwargs):
        result = original(path, *args, **kwargs)
        if str(path).endswith('private-hyprland.py'):
            result['load'].__globals__['archive'] = lambda p, member: (
                b'pkgname = hyprland-as02-private\npkgver = 1.0-1\narch = x86_64\ndepend = wayland>=1\n'
                if member == '.PKGINFO' else b'synthetic executable')
        return result
    monkeypatch.setattr(runpy, 'run_path', load)
    return record


def test_live_profile_carries_policy_exact_bytes_and_excludes_upstream(tmp_path, monkeypatch):
    record = configure(tmp_path, monkeypatch)
    upstream = tmp_path / 'releng'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\nhyprland\n')
    prepare = runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare']
    output = tmp_path / 'profile'
    prepare(upstream, output, ROOT, 'a' * 40)
    base = output / 'airootfs/usr/share/wilsof'
    assert (base / 'packages/private-hyprland.pkg.tar.zst').read_bytes() == Path(str(record['package'])).read_bytes()
    assert (base / 'private-hyprland.required').is_file()
    packages = (output / 'packages.x86_64').read_text().splitlines()
    assert 'hyprland' not in packages and 'wayland' in packages
    desktop = (base / 'desktop-packages.txt').read_text().splitlines()
    assert 'hyprland' not in desktop and 'wayland' in desktop
    customize = (output / 'airootfs/root/customize_airootfs.sh').read_text()
    assert 'private-hyprland.py' in customize and 'required=True' in customize
    assert str(tmp_path) not in (base / 'packages/PRIVATE-HYPRLAND.json').read_text()


def test_invalid_private_profile_input_leaves_output_absent(tmp_path, monkeypatch):
    configure(tmp_path, monkeypatch)
    monkeypatch.delenv('WILSOF_PRIVATE_EXPERIMENTAL')
    upstream = tmp_path / 'releng'; upstream.mkdir()
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    with pytest.raises(ValueError, match='Private Hyprland'):
        runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare'](upstream, output, ROOT, 'a' * 40)
    assert not output.exists()


def test_private_contract_is_connected_to_target_and_preformat_selection():
    provision = (ROOT / 'runtime/provision-target').read_text()
    installer = (ROOT / 'installer/wilsof_installer.py').read_text()
    assert "private['install'](target" in provision
    assert "private['verify'](target" in provision
    assert "private['selection'](self.packages" in installer
    assert "private['embedded']" in installer


def test_private_upstream_resolution_is_rejected_before_download(tmp_path, monkeypatch):
    profile = tmp_path / 'profile'; profile.mkdir()
    (profile / 'packages.x86_64').write_text('base\n')
    # Package preflight must consult the actual embedded policy before downloads.
    source = (ROOT / 'scripts/package-preflight.py').read_text()
    assert "private['embedded']" in source
    assert "Private Hyprland repository fallback rejected" in source


@pytest.mark.parametrize('case', ['valid', 'upstream', 'install-failed', 'binary-mismatch', 'version-mismatch', 'owner-mismatch', 'dependency-mismatch'])
def test_target_uses_exact_local_package_or_aborts_without_fallback(tmp_path, monkeypatch, case):
    configure(tmp_path, monkeypatch)
    module = api()
    record = module['load']()
    live = tmp_path / 'live/usr/share/wilsof'
    module['stage'](record, live)
    target = tmp_path / 'target'
    calls = []
    def run(argv, **kwargs):
        calls.append(argv)
        assert argv[:4] == ['arch-chroot', '-r', str(target), 'pacman']
        assert not any(x in argv for x in ('-S', '-Sy', '-Syu', '--nodeps', '--assume-installed'))
        text = ''
        if '-Qq' in argv:
            text = 'hyprland\n' if case == 'upstream' else 'wayland\n'
        elif '-T' in argv:
            assert argv[-1] == 'wayland>=1'
            if case == 'dependency-mismatch': raise subprocess.CalledProcessError(127, argv)
        elif '-U' in argv:
            assert argv[-1] == '/usr/share/wilsof/packages/private-hyprland.pkg.tar.zst'
            assert kwargs['check'] is True
            assert '--config' not in argv and '--needed' not in argv
            assert (target / 'usr/share/wilsof/packages/private-hyprland.pkg.tar.zst').read_bytes() == Path(record['package']).read_bytes()
            if case == 'install-failed': raise subprocess.CalledProcessError(1, argv)
            binary = target / 'usr/bin/Hyprland'; binary.parent.mkdir(parents=True)
            binary.write_bytes(b'wrong' if case == 'binary-mismatch' else b'synthetic executable')
        elif '-Q' in argv:
            text = record['name'] + (' 2.0-1' if case == 'version-mismatch' else ' 1.0-1')
        elif '-Qoq' in argv:
            text = 'unexpected' if case == 'owner-mismatch' else record['name']
        else:
            pytest.fail('Unexpected package operation')
        return subprocess.CompletedProcess(argv, 0, text, '')
    monkeypatch.setattr(subprocess, 'run', run)
    if case == 'valid':
        module['install'](target, live, required=True)
        assert sum('-U' in c for c in calls) == 1
        assert (target / 'usr/share/wilsof/private-hyprland.required').is_file()
    else:
        with pytest.raises(ValueError, match='Private Hyprland'):
            module['install'](target, live, required=True)
        assert sum('-U' in c for c in calls) == (0 if case in ('upstream', 'dependency-mismatch') else 1)


@pytest.mark.parametrize('missing', ['marker', 'manifest', 'package'])
def test_damaged_embedded_policy_never_becomes_public_mode(tmp_path, monkeypatch, missing):
    configure(tmp_path, monkeypatch)
    module = api(); record = module['load']()
    base = tmp_path / 'live'; module['stage'](record, base)
    paths = {'marker': base / 'private-hyprland.required',
             'manifest': base / 'packages/PRIVATE-HYPRLAND.json',
             'package': base / 'packages/private-hyprland.pkg.tar.zst'}
    paths[missing].unlink()
    with pytest.raises(ValueError, match='Private Hyprland'):
        module['embedded'](base)


def test_public_mode_has_no_local_package_side_effects(tmp_path, monkeypatch):
    module = api()
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: pytest.fail('Public mode must not invoke pacman'))
    module['install'](tmp_path / 'target', tmp_path / 'absent')
    assert not (tmp_path / 'target').exists()
    assert module['selection'](['base', 'hyprland'], None) == ['base', 'hyprland']


def test_resolved_upstream_dependency_aborts_before_download(tmp_path, monkeypatch):
    module = runpy.run_path(str(ROOT / 'scripts/package-preflight.py'))
    profile = tmp_path / 'profile'; profile.mkdir()
    (profile / 'packages.x86_64').write_text('base\n')
    original = runpy.run_path
    monkeypatch.setattr(runpy, 'run_path', lambda path, *a, **k:
                        {'embedded': lambda base: {'name': 'hyprland-as02-private'}}
                        if str(path).endswith('private-hyprland.py') else original(path, *a, **k))
    calls = []
    def command(argv):
        calls.append(argv)
        if '-Sp' in argv:
            return '\t'.join(['hyprland', '1.0-1', 'x86_64', 'hyprland-1.pkg.tar.zst', '0' * 64, 'c2ln', 'extra'])
        return ''
    monkeypatch.setitem(module['preflight'].__globals__, 'command', command)
    with pytest.raises(ValueError, match='repository fallback'):
        module['preflight'](profile, tmp_path / 'cache', tmp_path / 'db', tmp_path / 'keys')
    assert not any('-Sw' in argv for argv in calls)


@pytest.mark.parametrize('opt_in', [True, False])
def test_real_wrapper_private_input_guard_before_outputs(tmp_path, monkeypatch, opt_in):
    import shutil
    from build_fixture import layout
    source, _, _, env = layout(tmp_path)
    shutil.copy2(ROOT / 'runtime/private-hyprland.py', source / 'runtime/private-hyprland.py')
    _, contract, _ = fixture(tmp_path)
    tool = tmp_path / 'tools/bsdtar'
    tool.write_text('#!/bin/sh\ncase "$3" in .PKGINFO) printf "pkgname = hyprland-as02-private\\npkgver = 1.0-1\\narch = x86_64\\n";; *) printf "synthetic executable";; esac\n')
    tool.chmod(0o755)
    env['WILSOF_PRIVATE_HYPRLAND_CONTRACT'] = str(contract)
    if opt_in: env['WILSOF_PRIVATE_EXPERIMENTAL'] = '1'
    result = subprocess.run(['sh', str(source / 'scripts/build-iso.sh'), '--build'], env=env, capture_output=True, text=True)
    assert (result.returncode == 0) == opt_in, result.stderr
    assert Path(env['CAPTURE']).exists() == opt_in
    assert Path(env['WILSOF_ISO_OUTDIR']).exists() == opt_in
