"""Behavioral coverage of the image dependency gate and chroot contracts."""
import runpy
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def pin_api():
    return runpy.run_path(str(ROOT / 'runtime/pinned-package.py'))


def test_dependency_gate_checks_version_and_actual_r_option(monkeypatch):
    api = pin_api()
    calls = []

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        output = 'arch-install-scripts 31-2\n' if argv[0] == 'pacman' else '1\n'
        return subprocess.CompletedProcess(argv, 0, output, '')

    monkeypatch.setattr(subprocess, 'run', run)
    assert api['verify_arch_chroot_support']() == '31-2'
    assert [argv for argv, _ in calls] == [
        ['pacman', '-Q', 'arch-install-scripts'],
        ['vercmp', '31-2', '31'],
        ['arch-chroot', '-r', '-h'],
    ]
    assert all(options == {'check': True, 'capture_output': True, 'text': True}
               for _, options in calls)


@pytest.mark.parametrize('failure', ['old', 'missing', 'no-r', 'malformed'])
def test_dependency_gate_fails_closed_without_fallback(monkeypatch, failure):
    api = pin_api()
    calls = []

    def run(argv, **kwargs):
        calls.append(argv)
        if (failure == 'missing' and argv[0] == 'pacman') or (failure == 'no-r' and argv[0] == 'arch-chroot'):
            raise subprocess.CalledProcessError(1, argv)
        output = ('invalid output\n' if failure == 'malformed' else 'arch-install-scripts 27-1\n') if argv[0] == 'pacman' else '-1\n'
        if failure == 'no-r' and argv[0] == 'vercmp':
            output = '1\n'
        return subprocess.CompletedProcess(argv, 0, output, '')

    monkeypatch.setattr(subprocess, 'run', run)
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        api['verify_arch_chroot_support']()
    expected_count = {'old': 2, 'missing': 1, 'no-r': 3, 'malformed': 1}[failure]
    assert len(calls) == expected_count


@pytest.mark.parametrize('with_package', [False, True])
@pytest.mark.parametrize('gate_fails', [False, True])
def test_materialized_build_runs_gate_before_optional_install(tmp_path, monkeypatch, with_package, gate_fails):
    import hashlib
    import json
    import os
    import sys

    api = pin_api()
    package = tmp_path / api['PACKAGE_NAME']
    package.write_bytes(b'fixture package')
    api['verified_package'].__globals__['PACKAGE_SHA256'] = hashlib.sha256(package.read_bytes()).hexdigest()
    original = runpy.run_path
    prepare = original(str(ROOT / 'scripts/prepare-iso.py'))['prepare']
    monkeypatch.setattr(runpy, 'run_path', lambda path, *a, **k: api if str(path).endswith('pinned-package.py') else original(path, *a, **k))
    upstream = tmp_path / 'upstream'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    prepare(upstream, output, ROOT, 'a' * 40, hypridle_package=package if with_package else None)
    assert 'arch-install-scripts' in (output / 'packages.x86_64').read_text().splitlines()
    # Execute the real generated shell/Python control flow, substituting only the
    # privileged operations, not inspecting source strings or running a build.
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    (bindir / 'python3').symlink_to(sys.executable)
    log = tmp_path / 'calls.jsonl'
    (tmp_path / 'sitecustomize.py').write_text('''import json, os, runpy
from pathlib import Path
def record(name):
    with Path(os.environ['CALL_LOG']).open('a') as f:
        f.write(json.dumps(name) + '\\n')
    if name == 'gate' and os.environ['GATE_FAILS'] == '1':
        raise RuntimeError('unsupported arch-chroot')
runpy.run_path = lambda *a, **k: {
    'verify_arch_chroot_support': lambda: record('gate'),
    'install_package': lambda *a: record('install'),
}
''')
    env = {**os.environ, 'PATH': str(bindir) + os.pathsep + os.environ['PATH'],
           'PYTHONPATH': str(tmp_path), 'CALL_LOG': str(log), 'GATE_FAILS': str(int(gate_fails))}
    result = subprocess.run(['sh', str(output / 'airootfs/root/customize_airootfs.sh')], env=env, capture_output=True, text=True)
    assert bool(result.returncode) == gate_fails
    assert [json.loads(line) for line in log.read_text().splitlines()] == ['gate'] + (['install'] if with_package and not gate_fails else [])


def provision_transaction(tmp_path, monkeypatch, effect='intact', exit_code=0):
    import os
    import sys

    api = runpy.run_path(str(ROOT / 'runtime/provision-target'))
    main = api['main']
    namespace = main.__globals__
    source = tmp_path / 'source'
    (source / 'bin').mkdir(parents=True)
    (source / 'bin/wilsof-config-update').write_text('# fixture\n')
    target = tmp_path / 'target'
    (target / 'etc').mkdir(parents=True)
    (target / 'usr/lib').mkdir(parents=True)
    (target / 'usr/lib/os-release').write_text('ID=arch\n')
    (target / 'etc/passwd').write_text('demo:x:1000:1000::/home/demo:/bin/bash\n')
    (target / 'home/demo').mkdir(parents=True)
    pin = pin_api()
    installed = []
    pin['install_package'] = lambda *args: installed.append(args)
    monkeypatch.setitem(namespace, 'Path', lambda value: source if str(value) == '/usr/share/wilsof/source' else Path(value))
    monkeypatch.setattr(Path, 'is_mount', lambda value: value == target)
    monkeypatch.setattr(os, 'geteuid', lambda: 0)
    monkeypatch.setattr(sys, 'argv', ['provision-target', str(target), 'demo'])
    monkeypatch.setattr(runpy, 'run_path', lambda *a, **k: pin)
    calls = []
    resolver = target / 'etc/resolv.conf'

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        if argv[0] != 'arch-chroot':
            assert argv[0] == 'systemctl'
            return subprocess.CompletedProcess(argv, 0)
        assert resolver.is_symlink()
        assert os.readlink(resolver) == '/run/systemd/resolve/stub-resolv.conf'
        if effect != 'intact':
            resolver.unlink()
            if effect == 'wrong':
                resolver.symlink_to('/run/other-resolver')
            elif effect == 'regular':
                resolver.write_text('nameserver 192.0.2.1\n')
            elif effect == 'directory':
                resolver.mkdir()
        if exit_code:
            raise subprocess.CalledProcessError(exit_code, argv)
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(subprocess, 'run', run)
    return main, resolver, calls, installed, target


def test_provisioning_preserves_expected_dangling_resolver_and_uses_prepared_boundary(tmp_path, monkeypatch):
    import os
    main, resolver, calls, installed, target = provision_transaction(tmp_path, monkeypatch)
    main()
    assert resolver.is_symlink() and os.readlink(resolver) == '/run/systemd/resolve/stub-resolv.conf'
    assert installed == [(target, '/usr/share/wilsof/packages')]
    assert calls[-1] == (['arch-chroot', '-r', str(target), 'runuser', '-u', 'demo', '--',
                         'python3', '/usr/share/wilsof/source/runtime/desktop.py'], {'check': True})


@pytest.mark.parametrize('effect', ['wrong', 'regular', 'missing', 'directory'])
def test_successful_transaction_rejects_resolver_postcondition_failure(tmp_path, monkeypatch, effect):
    main, _, _, _, _ = provision_transaction(tmp_path, monkeypatch, effect)
    with pytest.raises(ValueError, match='resolver'):
        main()


@pytest.mark.parametrize('effect', ['intact', 'wrong'])
def test_failed_transaction_preserves_original_exit_and_reports_resolver_damage(tmp_path, monkeypatch, effect):
    import os
    main, resolver, calls, _, _ = provision_transaction(tmp_path, monkeypatch, effect, 17)
    with pytest.raises(subprocess.CalledProcessError) as failure:
        main()
    assert failure.value.returncode == 17
    assert sum(argv[0] == 'arch-chroot' for argv, _ in calls) == 1
    if effect == 'intact':
        assert os.readlink(resolver) == '/run/systemd/resolve/stub-resolv.conf'
    else:
        assert any('resolver' in note for note in failure.value.__notes__)


def test_resolver_inspection_error_does_not_replace_transaction_failure(tmp_path, monkeypatch):
    main, _, _, _, _ = provision_transaction(tmp_path, monkeypatch, 'intact', 17)

    def denied(_):
        raise PermissionError('resolver inspection denied')

    monkeypatch.setitem(main.__globals__, 'verify_resolver', denied)
    with pytest.raises(subprocess.CalledProcessError) as failure:
        main()
    assert failure.value.returncode == 17
    assert 'resolver inspection denied' in failure.value.__notes__[0]


@pytest.mark.parametrize('case', ['success', 'same-source', 'tampered-package', 'missing-package',
                                  'source-symlink', 'target-symlink', 'pacman-fails',
                                  'bad-binary', 'binary-symlink'])
def test_root_install_package_complete_flow_without_chroot(tmp_path, monkeypatch, case):
    import hashlib
    import shutil

    api = pin_api()
    # Redirect only Path('/') filesystem operations into a real temporary tree.
    # target_command('/') itself also has a separate real-Path contract test.
    build = tmp_path / 'prepared-build-root'
    directory = build / 'usr/share/wilsof/packages' if case == 'same-source' else tmp_path / 'packages'
    directory.mkdir(parents=True)
    data, executable = b'verified package fixture', b'verified binary fixture'
    package = directory / api['PACKAGE_NAME']
    package.write_bytes(data)
    api['verified_package'].__globals__['PACKAGE_SHA256'] = hashlib.sha256(data).hexdigest()
    api['install_package'].__globals__['BINARY_SHA256'] = hashlib.sha256(executable).hexdigest()
    monkeypatch.setitem(api['install_package'].__globals__, 'Path', lambda value: build if Path(value) == Path('/') else Path(value))
    if case == 'tampered-package':
        package.write_bytes(b'wrong bytes')
    elif case == 'missing-package':
        package.unlink()
    elif case == 'source-symlink':
        real = directory / 'real-package'
        package.rename(real)
        package.symlink_to(real)
    elif case == 'target-symlink':
        (build / 'usr/share/wilsof').mkdir(parents=True)
        (build / 'usr/share/wilsof/packages').symlink_to(directory, target_is_directory=True)
    calls = []

    def pacman(argv, **options):
        calls.append((argv, options))
        if case == 'pacman-fails':
            raise subprocess.CalledProcessError(27, argv)
        binary = build / 'usr/bin/hypridle'
        binary.parent.mkdir(parents=True, exist_ok=True)
        if case == 'binary-symlink':
            original = build / 'binary-source'
            original.write_bytes(executable)
            binary.symlink_to(original)
        else:
            binary.write_bytes(b'wrong binary' if case == 'bad-binary' else executable)
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(subprocess, 'run', pacman)
    expected = (ValueError if case in {'tampered-package', 'source-symlink', 'target-symlink', 'bad-binary', 'binary-symlink'}
                else FileNotFoundError if case == 'missing-package'
                else subprocess.CalledProcessError if case == 'pacman-fails' else None)
    if expected:
        with pytest.raises(expected) as error:
            api['install_package'](Path('/'), directory)
        if case == 'pacman-fails':
            assert isinstance(error.value, subprocess.CalledProcessError)
            assert error.value.returncode == 27
    else:
        # Self-copy must not happen when the verified package is already embedded.
        if case == 'same-source':
            monkeypatch.setattr(shutil, 'copyfile', lambda *a: pytest.fail('unexpected package self-copy'))
        api['install_package'](Path('/'), directory)
        destination = build / 'usr/share/wilsof/packages' / api['PACKAGE_NAME']
        assert destination.read_bytes() == data
        assert destination.stat().st_mode & 0o777 == 0o644
        assert (build / 'usr/bin/hypridle').read_bytes() == executable
    if case in {'tampered-package', 'missing-package', 'source-symlink', 'target-symlink'}:
        assert calls == []
    else:
        assert calls == [(['pacman', '-U', '--noconfirm', '--needed', '/usr/share/wilsof/packages/' + api['PACKAGE_NAME']], {'check': True})]
