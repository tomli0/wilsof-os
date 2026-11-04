"""Opt-in native contract test; default CI never starts Docker or mounts."""
import os
from pathlib import Path
import runpy

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'tests/integration/arch_chroot_lab.py'


def test_native_lab_refuses_unproven_rootless_isolation():
    verify = runpy.run_path(str(LAB))['verify_isolation']
    valid = {'uid_map': '0 1000 1\n1 100000 65536\n', 'cap_eff': 0x2400c1,
             'block_nodes': [], 'root_readonly': True, 'network_interfaces': ['lo']}
    verify(valid)
    for key, value in [('uid_map', '0 0 4294967295\n'), ('cap_eff', valid['cap_eff'] | (1 << 27)),
                       ('block_nodes', ['/dev/sda']), ('root_readonly', False),
                       ('network_interfaces', ['lo', 'eth0'])]:
        with pytest.raises(ValueError, match='isolation'):
            verify({**valid, key: value})


@pytest.mark.skipif(os.environ.get('WILSOF_RUN_ARCH_CHROOT_TEST') != '1',
                    reason='explicit rootless native-lab opt-in required')
def test_real_arch_chroot_transaction_and_teardown():
    fixture = Path(os.environ['WILSOF_ARCH_CHROOT_FIXTURE'])
    image = os.environ['WILSOF_ARCH_CHROOT_IMAGE']
    report = runpy.run_path(str(LAB))['run_lab'](fixture, image)
    assert report['dependency_version'] == report['fixture_version']
    assert report['api_mounts']
    assert report['physical_block_devices_exposed'] is False
    assert report['pacman_install_exit'] == 0
    assert report['pacman_failure_exit'] != 0
    assert report['command_failure_exit'] == 23
    assert report['setup_failure_exit'] != 0
    assert report['resolver_preserved']
    assert report['cleanup_after_success_and_failures']
    assert report['container_removed']
    output = os.environ.get('WILSOF_ARCH_CHROOT_REPORT')
    if output:
        import json
        Path(output).write_text(json.dumps(report, indent=2) + '\n')
