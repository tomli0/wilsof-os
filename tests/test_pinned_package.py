"""Internal package pin: never silently substitute an upstream build."""
import hashlib
from pathlib import Path
import runpy
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_pinned_package_rejects_unverified_bytes_before_running_pacman(tmp_path, monkeypatch):
    api = runpy.run_path(str(ROOT / 'runtime/pinned-package.py'))
    package = tmp_path / api['PACKAGE_NAME']
    package.write_bytes(b'unverified package')
    calls = []
    monkeypatch.setattr(api['subprocess'], 'run', lambda *a, **k: calls.append(a))
    with pytest.raises(ValueError, match='checksum'):
        api['install_package'](tmp_path / 'target', tmp_path)
    assert calls == []


def test_profile_carries_verified_package_and_installs_it_in_build_and_target(tmp_path, monkeypatch):
    helper = runpy.run_path(str(ROOT / 'runtime/pinned-package.py'))
    # A tiny fixture replaces only the pinned checksum, not package flow.
    data = b'fixture package bytes'
    package = tmp_path / helper['PACKAGE_NAME']
    package.write_bytes(data)
    prepare = runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare']
    import runpy as runpy_module
    original = runpy_module.run_path
    def fixture_run_path(path, *a, **k):
        result = original(path, *a, **k)
        if str(path).endswith('pinned-package.py'):
            result['verified_package'].__globals__['PACKAGE_SHA256'] = hashlib.sha256(data).hexdigest()
        return result
    monkeypatch.setattr(runpy_module, 'run_path', fixture_run_path)
    upstream = tmp_path / 'upstream'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    prepare(upstream, output, ROOT, 'a' * 40, hypridle_package=package)
    embedded = output / 'airootfs/usr/share/wilsof/packages' / package.name
    assert embedded.read_bytes() == data
    customize = (output / 'airootfs/root/customize_airootfs.sh').read_text()
    assert 'pinned-package.py' in customize and 'install_package' in customize
    assert 'runtime/pinned-package.py' in (ROOT / 'runtime/image-files.txt').read_text().splitlines()
    provision = (ROOT / 'runtime/provision-target').read_text()
    assert "['install_package'](target" in provision


def test_package_symlink_rejected(tmp_path):
    api = runpy.run_path(str(ROOT / 'runtime/pinned-package.py'))
    original = tmp_path / 'untrusted'
    original.write_bytes(b'anything')
    (tmp_path / api['PACKAGE_NAME']).symlink_to(original)
    with pytest.raises(ValueError, match='symlink'):
        api['verified_package'](tmp_path)


def test_install_copies_exact_verified_bytes_and_checks_binary(tmp_path, monkeypatch):
    api = runpy.run_path(str(ROOT / 'runtime/pinned-package.py'))
    data = b'fixture package'
    api['verified_package'].__globals__['PACKAGE_SHA256'] = hashlib.sha256(data).hexdigest()
    (tmp_path / api['PACKAGE_NAME']).write_bytes(data)
    target = tmp_path / 'target'
    (target / 'usr/bin').mkdir(parents=True)
    (target / 'usr/bin/hypridle').write_bytes(b'fixture binary')
    calls = []
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
    monkeypatch.setattr(api['subprocess'], 'run', run)
    with pytest.raises(ValueError, match='executable checksum'):
        api['install_package'](target, tmp_path)
    assert calls == [(['chroot', str(target), 'pacman', '-U', '--noconfirm', '--needed', '/usr/share/wilsof/packages/' + api['PACKAGE_NAME']], {'check': True})]
    assert (target / 'usr/share/wilsof/packages' / api['PACKAGE_NAME']).read_bytes() == data
    api['install_package'].__globals__['BINARY_SHA256'] = hashlib.sha256(b'fixture binary').hexdigest()
    api['install_package'](target, tmp_path)
