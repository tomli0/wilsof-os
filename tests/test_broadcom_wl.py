"""BCM4360 image/target contract; tool substitution is not hardware acceptance."""
from pathlib import Path
import runpy
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load():
    helper = ROOT / 'runtime/broadcom-wl.py'
    assert helper.is_file(), 'Missing fail-closed Broadcom kernel/module acceptance gate'
    return runpy.run_path(str(helper))


@pytest.fixture
def installed(tmp_path):
    module = tmp_path / 'usr/lib/modules/7.2.11-arch1-1'
    module.mkdir(parents=True)
    (module / 'pkgbase').write_text('linux\n')
    headers = module / 'build/include/config'
    headers.mkdir(parents=True)
    (headers / 'kernel.release').write_text('7.2.11-arch1-1\n')
    (module / 'updates/dkms').mkdir(parents=True)
    (module / 'updates/dkms/wl.ko.zst').write_bytes(b'module fixture')
    return tmp_path, module


def test_correct_kernel_headers_module_and_pci_alias_are_required(installed):
    root, module = installed
    calls = []
    def command(target, *argv):
        calls.append(argv)
        if argv[:2] == ('pacman', '-Q'):
            return 'linux 7.2.11.arch1-1\nlinux-headers 7.2.11.arch1-1\nbroadcom-wl-dkms 6.30.223.271-50\ndkms 3.4.4-1\n'
        return {'filename':'/lib/modules/7.2.11-arch1-1/updates/dkms/wl.ko.zst',
                'vermagic':'7.2.11-arch1-1 SMP preempt mod_unload',
                'alias':'pci:v*d*sv*sd*bc02sc80i*\n',
                'depends':'cfg80211'}[argv[argv.index('-F') + 1]]
    info = load()['verify'](root, command=command)
    assert info['kernel_release'] == '7.2.11-arch1-1'
    assert info['pci_id'] == '14e4:43a0'
    assert info['dependencies'] == ['cfg80211']
    assert all(c[0] in ('pacman', 'modinfo') for c in calls)


def test_image_signing_material_is_not_distributed_or_followed(tmp_path):
    seal = load()['discard_image_signing_key']
    keys = tmp_path / 'var/lib/dkms'
    keys.mkdir(parents=True)
    (keys / 'mok.key').write_bytes(b'synthetic image-only signing fixture')
    (keys / 'mok.pub').write_bytes(b'synthetic certificate')
    seal(tmp_path)
    assert not (keys / 'mok.key').exists()
    assert not (keys / 'mok.pub').exists()
    outside = tmp_path / 'outside'
    outside.write_bytes(b'preserve unrelated fixture')
    (keys / 'mok.key').symlink_to(outside)
    with pytest.raises(ValueError, match='signing'):
        seal(tmp_path)
    assert outside.read_bytes() == b'preserve unrelated fixture'


def test_materialized_live_and_target_packages_have_narrow_driver_policy(tmp_path):
    import shutil
    upstream = tmp_path / 'releng'
    shutil.copytree(ROOT / 'tests/fixtures/archiso92', upstream)
    output = tmp_path / 'profile'
    runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare'](upstream, output, ROOT, 'a' * 40)
    live = output / 'airootfs'
    for manifest in (output / 'packages.x86_64', live / 'usr/share/wilsof/desktop-packages.txt'):
        assert {'linux-headers', 'broadcom-wl-dkms'} <= set(manifest.read_text().splitlines())
    policy = (live / 'etc/modprobe.d/broadcom-wl-dkms.conf').read_text()
    assert 'blacklist' not in policy
    assert 'softdep bcma pre: wl' in policy
    assert 'MODULES+=(wl)' in (live / 'etc/mkinitcpio.conf.d/wilsof-wl.conf').read_text()
    assert (live / 'usr/share/wilsof/source/runtime/broadcom-wl.py').is_file()


@pytest.mark.parametrize('defect', ['headers', 'unsupported-kernel', 'abi', 'alias', 'module', 'build-failed'])
def test_failed_module_acceptance_never_loads_or_repairs(installed, defect):
    root, module = installed
    if defect == 'headers':
        (module / 'build/include/config/kernel.release').unlink()
    if defect == 'unsupported-kernel':
        (module / 'pkgbase').write_text('linux-omarchy\n')
    calls = []
    def command(target, *argv):
        calls.append(argv)
        if argv[0] == 'pacman':
            return 'linux 7.2.11.arch1-1\nlinux-headers 7.2.11.arch1-1\nbroadcom-wl-dkms 6.30.223.271-50\ndkms 3.4.4-1\n'
        if defect == 'build-failed':
            import subprocess
            raise subprocess.CalledProcessError(1, argv)
        values = {'filename':'/lib/modules/7.2.11-arch1-1/updates/dkms/wl.ko.zst',
                  'vermagic':'7.2.11-arch1-1 SMP', 'alias':'pci:v*d*sv*sd*bc02sc80i*', 'depends':'cfg80211'}
        values.update({'vermagic':'wrong SMP'} if defect == 'abi' else {})
        values.update({'alias':'pci:v00008086d*'} if defect == 'alias' else {})
        values.update({'filename':'/outside/wl.ko'} if defect == 'module' else {})
        return values[argv[argv.index('-F') + 1]]
    import subprocess
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        load()['verify'](root, command=command)
    assert all(c[0] in ('pacman', 'modinfo') for c in calls)
