"""Target review is tested with synthetic inventory; never touch a block device."""
import copy
import importlib
import json

import pytest


def inventory(**changes):
    disk = {'path': '/dev/vda', 'type': 'disk', 'size': 32 * 1024**3,
            'maj:min': '254:0', 'ro': False, 'wwn': None,
            'serial': 'private-test-serial', 'model': 'Example SSD',
            'vendor': 'Example maker', 'tran': 'sata', 'rm': False,
            'pttype': None, 'fstype': None, 'mountpoints': [None]}
    disk.update(changes)
    return {'blockdevices': [disk]}


def test_target_review_binds_human_readable_identity_without_serial():
    m = importlib.import_module('installer.wilsof_installer')
    target = m.assess_inventory('/dev/vda', inventory())
    assert target['display'] == {'manufacturer': 'Example maker',
                                 'model': 'Example SSD',
                                 'transport': 'sata', 'removable': False}
    assert target['size_bytes'] == 32 * 1024**3
    assert 'private-test-serial' not in json.dumps(target)


@pytest.mark.parametrize('transport', ['sata', 'usb', None])
def test_review_displays_target_before_destructive_confirmation(transport):
    m = importlib.import_module('installer.wilsof_installer')
    target = m.assess_inventory('/dev/vda', inventory(tran=transport))
    output, writes = [], []

    class Executor:
        packages = ['base']
        manifest_digest = 'sha256-fixture'

        def execute(self, plan, password, guard):
            guard()
            writes.append(plan)

    def ask(prompt):
        if prompt.startswith('Target'):
            return '/dev/vda'
        if prompt.startswith('New administrator'):
            return 'alice'
        review = '\n'.join(output)
        assert 'Example maker' in review
        assert 'Example SSD' in review
        assert str(32 * 1024**3) in review
        assert json.dumps(transport or 'not reported') in review
        assert 'Whole-disk installation erases all data' in review
        assert 'private-test-serial' not in review
        return 'cancel'

    with pytest.raises(m.Refusal, match='confirmation'):
        m.interactive(Executor(), probe=lambda path: copy.deepcopy(target),
                      ask=ask, secret=lambda prompt: 'test-only', output=output.append)
    assert not writes


@pytest.mark.parametrize('field,value', [('vendor', 'Other maker'), ('model', 'Other SSD'),
                                         ('tran', 'usb'), ('rm', True)])
def test_review_metadata_change_refuses_before_backend_writes(field, value):
    m = importlib.import_module('installer.wilsof_installer')
    before = m.assess_inventory('/dev/vda', inventory())
    after = m.assess_inventory('/dev/vda', inventory(**{field: value}))
    probes = iter([before, after])
    answers = iter(['/dev/vda', 'alice', 'ERASE /dev/vda'])
    writes = []

    class Executor:
        packages = ['base']
        manifest_digest = 'sha256-fixture'

        def execute(self, plan, password, guard):
            guard()
            writes.append(True)

    with pytest.raises(m.Refusal, match='identity or size changed'):
        m.interactive(Executor(), probe=lambda path: next(probes),
                      ask=lambda prompt: next(answers), secret=lambda prompt: 'test-only',
                      output=lambda value: None)
    assert not writes


def test_control_characters_are_escaped_in_review_json():
    m = importlib.import_module('installer.wilsof_installer')
    target = m.assess_inventory('/dev/vda', inventory(model='SSD\x1b[2J\nFAKE'))
    encoded = json.dumps(target, ensure_ascii=True)
    assert '\x1b' not in encoded and '\n' not in encoded
    assert '\\u001b' in encoded and '\\n' in encoded
