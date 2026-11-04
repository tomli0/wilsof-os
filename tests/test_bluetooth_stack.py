"""Bluetooth requires a daemon, not only the client library used by DMS."""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]


def test_bluetooth_daemon_is_in_both_materialized_and_installed_package_plans(tmp_path):
    installer = runpy.run_path(str(ROOT / 'installer/wilsof_installer.py'))
    packages = installer['read_manifest'](ROOT / 'runtime/desktop-packages.txt')
    assert 'bluez' in packages, 'bluez-libs alone cannot provide org.bluez'
    upstream = tmp_path / 'upstream'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    output = tmp_path / 'profile'
    runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare'](
        upstream, output, ROOT, 'a' * 40)
    assert 'bluez' in (output / 'packages.x86_64').read_text().splitlines()
    root = output / 'airootfs'
    assert (root / 'etc/systemd/system/dbus-org.bluez.service').readlink() == Path('/usr/lib/systemd/system/bluetooth.service')
    assert (root / 'etc/systemd/system/bluetooth.target.wants/bluetooth.service').readlink() == Path('/usr/lib/systemd/system/bluetooth.service')
    # BlueZ supplies D-Bus activation; do not enable radios or force adapter power.
    assert 'bluetoothctl power on' not in (ROOT / 'runtime/provision-target').read_text()
