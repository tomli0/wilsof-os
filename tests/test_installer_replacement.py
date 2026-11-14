"""Replacement safety controls use synthetic inventories, never real disks."""
import copy
import json

import pytest
from test_installer_runtime import runtime, disk_inventory, fake_arch, signed_plan


def existing_inventory(fs='btrfs'):
    inventory = disk_inventory()
    inventory['blockdevices'][0].update(pttype='gpt', tran='nvme', rm=False, children=[
        dict(path='/dev/vda1', kname='vda1', type='part', size=1024**3,
             **{'maj:min': '254:1'}, ro=False, fstype='vfat', mountpoints=[None],
             parttype='c12a7328-f81f-11d2-ba4b-00a0c93ec93b'),
        dict(path='/dev/vda2', kname='vda2', type='part', size=30*1024**3,
             **{'maj:min': '254:2'}, ro=False, fstype=fs, mountpoints=[None],
             parttype='0fc63daf-8483-4772-8e79-3d69d8477de4'),
    ])
    return inventory


def test_replacement_reviews_existing_efi_and_btrfs_without_weakening_blank_mode():
    m = runtime()
    assert hasattr(m, 'assess_replacement'), 'Explicit replacement assessment is missing'
    target = m.assess_replacement('/dev/vda', existing_inventory())
    assert target['expected_empty'] is False
    assert target['existing'][1]['filesystem'] == 'vfat'
    assert target['existing'][1]['efi'] is True
    assert target['existing'][2]['filesystem'] == 'btrfs'
    assert target['identity'] == m.assess_inventory('/dev/vda', disk_inventory())['identity']
    with pytest.raises(m.Refusal):
        m.assess_inventory('/dev/vda', existing_inventory())


@pytest.mark.parametrize('case', ['mounted-child', 'swap', 'live-usb', 'mapping', 'duplicate-id',
                                 'wrong-target', 'duplicate-device', 'unknown-table', 'readonly'])
def test_replacement_refuses_unsafe_target_inventories(case):
    m = runtime()
    inventory = existing_inventory()
    disk = inventory['blockdevices'][0]
    if case == 'mounted-child': disk['children'][1]['mountpoints'] = ['/mnt/data']
    elif case == 'swap': disk['children'][1]['mountpoints'] = ['[SWAP]']
    elif case == 'live-usb': disk.update(fstype='iso9660', tran='usb', rm=True)
    elif case == 'mapping': disk['children'][1]['children'] = [dict(type='crypt')]
    elif case == 'duplicate-id':
        other = copy.deepcopy(disk); other.update(path='/dev/vdb', **{'maj:min': '254:16'}); other.pop('children')
        inventory['blockdevices'].append(other)
    elif case == 'duplicate-device': disk['children'][1]['maj:min'] = disk['children'][0]['maj:min']
    elif case == 'unknown-table': disk['pttype'] = 'unknown'
    elif case == 'readonly': disk['children'][1]['ro'] = True
    with pytest.raises(m.Refusal):
        m.assess_replacement('/dev/not-selected' if case == 'wrong-target' else '/dev/vda', inventory)


def test_replacement_probe_binds_layout_signatures_and_device_bytes(monkeypatch):
    m = runtime()
    assert hasattr(m, 'probe_replacement'), 'Replacement probe is missing'
    commands = []
    def query(argv):
        commands.append(argv)
        return existing_inventory() if argv[0] == 'lsblk' else {'signatures': [{'type': 'btrfs', 'offset': '0x10040', 'uuid': 'synthetic-uuid'}]}
    monkeypatch.setattr(m, 'read_json', query)
    monkeypatch.setattr(m, 'has_holders', lambda p: False)
    monkeypatch.setattr(m, 'device_fingerprint', lambda row: 'a'*64)
    monkeypatch.setattr(m, 'live_device_uuids', lambda: set())
    result = m.probe_replacement('/dev/vda')
    assert result['existing'][2]['signatures'][0]['type'] == 'btrfs'
    assert result['existing'][2]['header_sha256'] == 'a'*64
    assert len(commands) == 8
    assert '--tree' in commands[0], 'PATH/KNAME without NAME otherwise produces a flat lsblk JSON inventory'
    assert all(argv[1:3] == ['--no-act', '--json'] for argv in commands if argv[0] == 'wipefs')
    monkeypatch.setattr(m, 'has_holders', lambda p: p == '/dev/vda2')
    with pytest.raises(m.Refusal, match='holder'):
        m.probe_replacement('/dev/vda')


@pytest.mark.parametrize('case', ['success', 'wrong-confirmation', 'wrong-path', 'changed-identity'])
def test_explicit_replacement_review_confirmation_and_reprobe(case):
    m = runtime()
    events, output = [], []
    target = m.assess_replacement('/dev/vda', existing_inventory())
    for row in target['existing']:
        row.update(header_sha256='a'*64, signatures=[])
    class Executor:
        packages = ['base']
        manifest_digest = 'sha256-synthetic'
        def execute(self, plan, password, guard):
            events.append('execute')
            m.validate_plan(plan)
            assert plan['installation_mode'] == 'replace-existing'
            assert plan['target']['expected_empty'] is False
            guard()
            events.append('write')
    answers = iter(['/dev/vda', 'alice'])
    def ask(prompt):
        if not prompt.startswith('Type '): return next(answers)
        assert 'Omarchy' in '\n'.join(output) and 'btrfs' in '\n'.join(output)
        phrase = prompt[len('Type '):].split(' exactly')[0]
        assert phrase.startswith('REPLACE /dev/vda sha256-')
        assert 'transient-test-secret' not in '\n'.join(output)
        return 'ERASE /dev/vda' if case == 'wrong-confirmation' else phrase.replace('/dev/vda', '/dev/vdb') if case == 'wrong-path' else phrase
    probes = []
    def probe(path):
        probes.append(path)
        result = copy.deepcopy(target)
        if len(probes) > 1 and case == 'changed-identity': result['identity'] = 'sha256-changed'
        return result
    if case == 'success':
        m.interactive(Executor(), mode='replace-existing', probe=probe, ask=ask,
                      secret=lambda _: 'transient-test-secret', output=output.append)
        assert events == ['execute', 'write']
    else:
        with pytest.raises(m.Refusal):
            m.interactive(Executor(), mode='replace-existing', probe=probe, ask=ask,
                          secret=lambda _: 'transient-test-secret', output=output.append)
        assert 'write' not in events
        assert bool(events) == (case == 'changed-identity')


@pytest.mark.parametrize('case', ['success', 'changed', 'interrupted', 'foreign-btrfs', 'parent-failed', 'reread-failed', 'settle-failed', 'stale-children'])
def test_erasure_is_confirmed_reprobed_and_confined_to_open_selected_devices(monkeypatch, case):
    from contextlib import contextmanager
    from types import SimpleNamespace
    import subprocess
    m = runtime()
    assert hasattr(m, 'erase_replacement'), 'Replacement erasure boundary is missing'
    from test_installer_runtime import signed_plan
    plan = signed_plan()
    plan['installation_mode'] = 'replace-existing'
    plan['target'] = m.assess_replacement('/dev/vda', existing_inventory())
    for row in plan['target']['existing']: row.update(header_sha256='a'*64, signatures=[])
    plan['review_digest'] = m.review_digest(plan)
    erased = copy.deepcopy(plan['target']);erased['existing'] = [dict(erased['existing'][0], table=None, filesystem=None, signatures=[])]
    count = []
    def probe(path):
        count.append(path)
        if case == 'changed': return dict(plan['target'], identity='sha256-different')
        return copy.deepcopy(plan['target'] if len(count) <= 2 or case == 'stale-children' else erased)
    monkeypatch.setattr(m, 'probe_replacement', probe)
    inventory = existing_inventory()
    if case == 'foreign-btrfs':
        other = copy.deepcopy(inventory['blockdevices'][0]);other['path'] = '/dev/vdb';inventory['blockdevices'].append(other)
    monkeypatch.setattr(m, 'read_json', lambda _: inventory)
    @contextmanager
    def devices(rows):
        assert [p['path'] for p in rows] == ['/dev/vda', '/dev/vda1', '/dev/vda2']
        yield {p['path']: SimpleNamespace(fileno=lambda i=i: 90+i, close=lambda: None) for i,p in enumerate(rows)}
    monkeypatch.setattr(m, 'open_reviewed_devices', devices)
    monkeypatch.setattr(m, 'verify_archinstall_metadata', lambda: None)
    commands = []
    def wipe(fd):
        commands.append(['bound-wipe', fd])
        if case == 'interrupted': raise KeyboardInterrupt
        if case == 'parent-failed' and fd == 90: raise OSError('synthetic I/O failure')
    monkeypatch.setattr(m, 'wipe_bound_fd', wipe)
    def reread(fd):
        commands.append(['reread',fd])
        if case == 'reread-failed': raise OSError('synthetic reread failure')
    monkeypatch.setattr(m, 'reread_partition_table', reread)
    def run(argv, **kw):
        commands.append(argv)
        if case == 'settle-failed': raise subprocess.CalledProcessError(1,argv)
        return subprocess.CompletedProcess(argv,0,'','')
    monkeypatch.setattr(m.subprocess, 'run', run)
    if case == 'success':
        assert m.erase_replacement(plan) == erased
        assert [x[-1] for x in commands if x[0]=='bound-wipe'] == [92,91,90]
        assert commands[-2] == ['reread',90]
    else:
        error = KeyboardInterrupt if case == 'interrupted' else OSError if case in ('parent-failed','reread-failed') else subprocess.CalledProcessError if case == 'settle-failed' else m.Refusal
        with pytest.raises(error):m.erase_replacement(plan)
        assert len(commands) == {'changed':0,'foreign-btrfs':0,'interrupted':1,'parent-failed':3,'reread-failed':4,'settle-failed':5,'stale-children':5}[case]


def test_backend_defers_global_archinstall_import_until_after_authorized_erasure(fake_arch, monkeypatch):
    m, f = runtime(), fake_arch
    events = []
    monkeypatch.setattr(m, 'load_archinstall', lambda: (events.append('import') or f.api))
    monkeypatch.setattr(m, 'check_target_mount', lambda _: None)
    monkeypatch.setattr(m, 'verify_archinstall_metadata', lambda: events.append('metadata'))
    executor = m.ArchinstallExecutor(f.manifest, f.hook, f.target, defer_api=True)
    assert events == ['metadata']
    plan = signed_plan();plan['installation_mode'] = 'replace-existing'
    plan['target'] = m.assess_replacement('/dev/vda', existing_inventory())
    for row in plan['target']['existing']:row.update(header_sha256='a'*64, signatures=[])
    plan['plan_id'] = executor.manifest_digest;plan['review_digest'] = m.review_digest(plan)
    erased = dict(plan['target'], existing=[])
    monkeypatch.setattr(m, 'erase_replacement', lambda p: (events.append('erase') or erased))
    monkeypatch.setattr(m, 'probe_replacement', lambda p: (events.append('final-probe') or erased))
    monkeypatch.setattr(m.subprocess, 'run', lambda *a,**k: None)
    fallback = f.target/'boot/EFI/BOOT/BOOTX64.EFI';fallback.parent.mkdir(parents=True);fallback.write_bytes(b'fixture')
    executor.execute(plan, 'transient-only', lambda:events.append('confirmed-guard'))
    assert events == ['metadata','confirmed-guard','erase','import','final-probe']
    assert f.events[0] == 'format'
    f.api.device_handler.load_devices.assert_not_called()


def test_bound_signature_wipe_survives_actual_path_substitution(tmp_path):
    import hashlib
    import shutil
    import subprocess
    m = runtime()
    assert hasattr(m, 'wipe_bound_fd'), 'Descriptor-bound native erase API is missing'
    if not shutil.which('mkfs.ext4'):
        pytest.skip('mkfs.ext4 unavailable for regular virtual-disk fixture')
    selected, other, original = [tmp_path/n for n in ['selected.img','other.img','original.img']]
    for p in (selected, other):
        with p.open('wb') as f:f.truncate(32*1024**2)
        subprocess.run(['mkfs.ext4','-q','-F',str(p)],check=True,capture_output=True)
    other_hash = hashlib.sha256(other.read_bytes()).hexdigest()
    with selected.open('r+b') as bound:
        selected.rename(original)
        other.rename(selected)  # substitution occurs after descriptor validation
        m.wipe_bound_fd(bound.fileno())
        assert not bound.closed
    assert hashlib.sha256(selected.read_bytes()).hexdigest() == other_hash
    query = lambda p: subprocess.run(['wipefs','--no-act','--json',str(p)],check=True,capture_output=True,text=True)
    assert json.loads(query(original).stdout)['signatures'] == []
    assert json.loads(query(selected).stdout)['signatures'][0]['type'] == 'ext4'


def test_backend_metadata_rejects_missing_or_wrong_version_before_any_wipe(monkeypatch):
    import importlib.metadata
    m = runtime()
    assert hasattr(m, 'verify_archinstall_metadata'), 'Side-effect-free backend version gate is missing'
    monkeypatch.setattr(importlib.metadata, 'version', lambda _: '99.0')
    with pytest.raises(m.Refusal):m.verify_archinstall_metadata()
    def absent(_):raise importlib.metadata.PackageNotFoundError('archinstall')
    monkeypatch.setattr(importlib.metadata, 'version', absent)
    with pytest.raises(m.Refusal):m.verify_archinstall_metadata()


@pytest.mark.parametrize('case', ['lsblk-uuid','signature-uuid','iso-magic'])
def test_live_media_cannot_be_replaced_even_after_copytoram(monkeypatch, case):
    m=runtime();inventory=existing_inventory()
    if case=='lsblk-uuid':inventory['blockdevices'][0]['uuid']='live-uuid'
    def query(argv):
        if argv[0]=='lsblk':return copy.deepcopy(inventory)
        return {'signatures':[{'type':'iso9660' if case=='iso-magic' else 'btrfs',
                               'offset':'0x8001','uuid':'live-uuid' if case=='signature-uuid' else 'test-uuid'}]}
    monkeypatch.setattr(m,'read_json',query)
    monkeypatch.setattr(m,'has_holders',lambda _:False)
    monkeypatch.setattr(m,'device_fingerprint',lambda _:'a'*64)
    monkeypatch.setattr(m,'live_device_uuids',lambda:{'live-uuid'})
    with pytest.raises(m.Refusal):m.probe_replacement('/dev/vda')


@pytest.mark.parametrize('case',['temporary-busy','persistent-busy','permission'])
def test_bound_partition_reread_retries_only_transient_busy(monkeypatch,case):
    import errno,fcntl,time
    m=runtime();calls=[]
    def ioctl(fd,request):
        assert fd==77 and request==0x125f
        calls.append(fd)
        if case=='permission':raise PermissionError(errno.EPERM,'denied')
        if case=='persistent-busy' or len(calls)<3:raise OSError(errno.EBUSY,'reader still open')
        return 0
    monkeypatch.setattr(fcntl,'ioctl',ioctl)
    monkeypatch.setattr(time,'sleep',lambda _:None)
    if case=='temporary-busy':
        m.reread_partition_table(77)
        assert len(calls)==3
    else:
        with pytest.raises(OSError):m.reread_partition_table(77)
        assert len(calls)==(1 if case=='permission' else 10)







