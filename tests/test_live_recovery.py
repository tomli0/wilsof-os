"""Recovery account is generated at boot, before and independently of the GUI."""
import importlib.machinery
import importlib.util
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def load_console():
    path = ROOT / 'runtime/live-console-setup'
    assert path.is_file(), 'Missing independent live console setup'
    loader = importlib.machinery.SourceFileLoader('live_console', str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    m = importlib.util.module_from_spec(spec)
    loader.exec_module(m)
    return m


def test_recovery_password_is_runtime_only_and_not_in_command_arguments(tmp_path, monkeypatch):
    m = load_console()
    calls = []
    def run(argv, **kw):
        calls.append((argv, kw))
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(m.subprocess, 'run', run)
    m.prepare_console(tmp_path)
    issue = (tmp_path / 'etc/issue').read_text()
    password_call = next(c for c in calls if c[0] == ['chpasswd'])
    password = password_call[1]['input'].split(':', 1)[1].strip()
    assert len(password) >= 12
    assert password not in str([c[0] for c in calls])
    assert password in issue and 'live' in issue and 'Ctrl+Alt+F2' in issue
    assert password_call[1]['check'] is True
    assert not list(tmp_path.rglob('*.secret'))


def test_materialized_console_precedes_gui_but_does_not_depend_on_it(tmp_path):
    import runpy
    prepare = runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare']
    upstream = tmp_path / 'upstream'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    prepare(upstream, output, ROOT, 'a' * 40)
    root = output / 'airootfs'
    console = (root / 'etc/systemd/system/wilsof-live-console.service').read_text()
    assert 'Before=wilsof-live-setup.service getty@tty2.service greetd.service' in console
    assert 'Requires=wilsof-live-setup' not in console
    assert (root / 'etc/systemd/system/getty.target.wants/getty@tty2.service').is_symlink()
    service = (root / 'etc/systemd/system/wilsof-live-setup.service').read_text()
    assert 'Requires=wilsof-live-console.service' in service
    assert 'OnFailure=wilsof-live-failure.service' in service
    sudo = (root / 'etc/sudoers.d/wilsof-live-installer').read_text()
    assert 'wilsof-live-recover' in sudo
    assert 'NOPASSWD: ALL' not in sudo
    assert not (root / 'usr/share/wilsof/source/runtime/live-console-setup').exists()


def test_live_console_is_independent_and_installed_policy_unchanged():
    # Runtime must not need the boot-media mount that copytoram removes.
    m = load_console()
    assert callable(m.prepare_console)
    provision = (ROOT / 'runtime/provision-target').read_text()
    assert 'chpasswd' not in provision and 'live-console-setup' not in provision
    recovery = (ROOT / 'runtime/live-recover').read_text()
    assert 'shell=True' not in recovery
    assert 'sys.argv[1:]' in recovery
