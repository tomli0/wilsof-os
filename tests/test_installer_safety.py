"""Installer safety regressions; only temporary files and synthetic inventories."""
from pathlib import Path
import runpy

import pytest

from installer import wilsof_installer as installer
from test_installer_runtime import signed_plan

ROOT = Path(__file__).resolve().parents[1]
RESERVED = ('root', 'greeter', 'greetd', 'daemon', 'bin', 'sys', 'sync', 'mail',
            'ftp', 'http', 'dbus', 'uuidd', 'avahi', 'polkitd', 'rtkit',
            'systemd-network', 'systemd-resolve', 'systemd-timesync',
            'systemd-coredump', 'brltty', 'nobody', 'named', 'nbd', 'openvpn',
            'partimag', 'pcscd', 'rpcuser')


def plan_for(username):
    plan = signed_plan()
    plan['account']['username'] = username
    plan['review_digest'] = installer.review_digest(plan)
    return plan


def target_for(tmp_path, username, uid=1000, home=None):
    (tmp_path / 'etc').mkdir()
    (tmp_path / 'usr/lib').mkdir(parents=True)
    (tmp_path / 'usr/lib/os-release').write_text('ID=arch\n')
    home = home if home is not None else f'/home/{username}'
    (tmp_path / 'etc/passwd').write_text(f'{username}:x:{uid}:1000::{home}:/bin/bash\n')
    return tmp_path


@pytest.mark.parametrize('username', RESERVED)
def test_reserved_username_rejected_by_installer_and_provisioner(tmp_path, username):
    with pytest.raises(installer.Refusal, match='username'):
        installer.validate_plan(plan_for(username))
    validate = runpy.run_path(str(ROOT / 'runtime/provision-target'))['validate_target']
    # Even a high UID/home must not make a reserved system name acceptable.
    target = target_for(tmp_path, username)
    with pytest.raises(ValueError, match='username'):
        validate(target, username, False)


@pytest.mark.parametrize('username', ['alice', 'demo', 'alice-2', '_desktop', 'a' * 32, 'live'])
def test_normal_username_accepted_at_both_boundaries(tmp_path, username):
    assert installer.validate_plan(plan_for(username))['account']['username'] == username
    validate = runpy.run_path(str(ROOT / 'runtime/provision-target'))['validate_target']
    target = target_for(tmp_path, username)
    assert validate(target, username, False) == target


@pytest.mark.parametrize('uid,home', [(999, '/home/alice'), (1000, '/var/lib/alice')])
def test_target_still_requires_desktop_uid_and_home(tmp_path, uid, home):
    validate = runpy.run_path(str(ROOT / 'runtime/provision-target'))['validate_target']
    target = target_for(tmp_path, 'alice', uid, home)
    with pytest.raises(ValueError, match='dedicated home'):
        validate(target, 'alice', False)


@pytest.mark.parametrize('username', ['greeter', 'daemon'])
def test_reserved_username_stops_before_confirmation_and_execution(username):
    class Executor:
        manifest_digest = 'sha256-fixture'
        packages = ['base']

        def execute(self, *args):
            pytest.fail('reserved username reached destructive executor')

    answers = iter(['/dev/vda', username])
    with pytest.raises(installer.Refusal, match='username'):
        installer.interactive(
            Executor(), probe=lambda _: signed_plan()['target'],
            ask=lambda _: next(answers),
            secret=lambda _: pytest.fail('reserved username reached password prompt'),
            output=lambda _: None,
        )


@pytest.mark.parametrize('mount_kind', ['target', 'descendant'])
def test_parent_symlink_cannot_hide_mount(tmp_path, monkeypatch, mount_kind):
    real = tmp_path / 'real'
    target = real / 'target'
    target.mkdir(parents=True)
    alias = tmp_path / 'alias'
    alias.symlink_to(real, target_is_directory=True)
    mounted = target if mount_kind == 'target' else target / 'nested'
    monkeypatch.setattr(installer, 'read_json', lambda _: {
        'filesystems': [{'target': str(mounted)}],
    })
    with pytest.raises(installer.Refusal, match='Target mount directory'):
        installer.check_target_mount(alias / 'target')


def test_mount_table_alias_is_compared_canonically(tmp_path, monkeypatch):
    real = tmp_path / 'real'
    target = real / 'target'
    target.mkdir(parents=True)
    alias = tmp_path / 'alias'
    alias.symlink_to(real, target_is_directory=True)
    monkeypatch.setattr(installer, 'read_json', lambda _: {
        'filesystems': [{'target': str(alias / 'target')}],
    })
    with pytest.raises(installer.Refusal, match='Target mount directory'):
        installer.check_target_mount(target)


@pytest.mark.parametrize('error', [PermissionError('denied'), RuntimeError('symlink loop')])
@pytest.mark.parametrize('failure_at', ['target', 'mount'])
def test_mount_resolution_errors_fail_closed(tmp_path, monkeypatch, error, failure_at):
    target = tmp_path / 'target'
    target.mkdir()
    unrelated = tmp_path / 'unrelated'
    unrelated.mkdir()
    original = Path.resolve

    def resolve(path, *args, **kwargs):
        if path == (target if failure_at == 'target' else unrelated):
            raise error
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'resolve', resolve)
    monkeypatch.setattr(installer, 'read_json', lambda _: {
        'filesystems': [{'target': str(unrelated)}],
    })
    with pytest.raises(installer.Refusal, match='Target mount directory'):
        installer.check_target_mount(target)


def test_unmounted_canonical_target_is_accepted(tmp_path, monkeypatch):
    target = tmp_path / 'target'
    target.mkdir()
    monkeypatch.setattr(installer, 'read_json', lambda _: {
        'filesystems': [{'target': str(tmp_path / 'unrelated')}],
    })
    installer.check_target_mount(target)


def test_materialized_payload_contains_executable_shared_policy(tmp_path):
    import subprocess
    import sys
    prepare = runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare']
    upstream = tmp_path / 'upstream'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    prepare(upstream, output, ROOT, 'a' * 40)
    payload = output / 'airootfs/usr/share/wilsof/source'
    assert (payload / 'installer/accounts.py').read_bytes() == (ROOT / 'installer/accounts.py').read_bytes()
    code = ("import runpy; ns=runpy.run_path(" + repr(str(payload / 'runtime/provision-target'))
            + "); ns['validate_username']('alice'); ns['validate_username']('greeter')")
    result = subprocess.run([sys.executable, '-I', '-c', code], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Unsupported or reserved username' in result.stderr
    assert 'FileNotFoundError' not in result.stderr


def test_copied_provisioner_uses_fixed_payload_policy(tmp_path, monkeypatch):
    import shutil
    helper = tmp_path / 'usr/local/lib/wilsof/provision-target'
    helper.parent.mkdir(parents=True)
    shutil.copy2(ROOT / 'runtime/provision-target', helper)
    original = runpy.run_path
    calls = []

    def load(path, *args, **kwargs):
        if str(path) == '/usr/share/wilsof/source/installer/accounts.py':
            calls.append(str(path))
            return original(str(ROOT / 'installer/accounts.py'))
        return original(path, *args, **kwargs)

    monkeypatch.setattr(runpy, 'run_path', load)
    namespace = runpy.run_path(str(helper))
    assert calls == ['/usr/share/wilsof/source/installer/accounts.py']
    with pytest.raises(ValueError, match='username'):
        namespace['validate_username']('greeter')
