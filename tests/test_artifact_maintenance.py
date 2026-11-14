"""Real filesystem tests for the host-only artifact maintenance CLI."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import hashlib
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/artifact-maintenance.py'

def module():
    spec = importlib.util.spec_from_file_location('maintenance', SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def lab(tmp_path):
    root = tmp_path / 'wilsof-completed-run'
    root.mkdir()
    target = root / 'cache.pkg.tar.zst'
    target.write_bytes(b'reproducible package bytes')
    kept = tmp_path / 'retained.pkg.tar.zst'
    kept.write_bytes(target.read_bytes())
    sha = hashlib.sha256(target.read_bytes()).hexdigest()
    p = {'version': 1, 'roots': [str(root)], 'protected': [str(kept)],
         'image_roots': [str(root)], 'locks': [str(tmp_path / 'maintenance.lock')],
         'pins': [{'path': str(kept), 'sha256': sha}],
         'artifacts': [{'id': 'one', 'path': str(target), 'classification': 'DISPOSABLE',
                        'workflow': {'id': 'fixture-passed', 'state': 'completed',
                                     'result': 'success', 'pending_acceptance': False},
                        'sha256': sha, 'proof': {'path': str(kept), 'sha256': sha}}]}
    return module(), p, target, kept


def test_plan_requires_verified_retained_duplicate(lab):
    m, p, target, kept = lab
    assert hasattr(m, 'plan'), 'dry-run planning is missing'
    result = m.plan(p)
    assert result['targets'][0]['path'] == str(target)
    assert result['estimated_recoverable_bytes'] == target.stat().st_blocks * 512
    assert target.exists() and kept.exists()


@pytest.mark.parametrize('change', ['outside', 'dotdot', 'symlink', 'hardlink',
                                   'protected', 'changed', 'proof', 'unfinished', 'source'])
def test_plan_refuses_ambiguous_or_unretained_targets(lab, change):
    m, p, target, kept = lab
    a = p['artifacts'][0]
    if change == 'outside': a['path'] = str(kept)
    if change == 'dotdot': a['path'] = str(target.parent) + '/../' + target.parent.name + '/' + target.name
    if change == 'symlink':
        target.unlink()
        target.symlink_to(kept)
    if change == 'hardlink':
        target.unlink()
        target.hardlink_to(kept)
    if change == 'protected': p['protected'].append(str(target.parent))
    if change == 'changed': target.write_bytes(b'changed')
    if change == 'proof': kept.write_bytes(b'unretained')
    if change == 'unfinished': a['workflow']['pending_acceptance'] = True
    if change == 'source': (target.parent / '.git').write_text('gitdir: preserved')
    assert hasattr(m, 'plan'), 'dry-run planning is missing'
    with pytest.raises((m.Refusal, OSError)):
        m.plan(p)
    assert target.exists()




def test_plan_refuses_live_open_file(lab):
    m, p, target, _ = lab
    with target.open('rb'):
        with pytest.raises(m.Refusal, match='active'):
            m.plan(p)


def test_plan_follows_actual_qcow2_backing(lab):
    m, p, target, kept = lab
    base = target.parent / 'base.qcow2'
    child = target.parent / 'child.qcow2'
    subprocess.run(['qemu-img', 'create', '-f', 'qcow2', str(base), '1M'], check=True, capture_output=True)
    subprocess.run(['qemu-img', 'create', '-f', 'qcow2', '-F', 'qcow2', '-b', str(base), str(child)], check=True, capture_output=True)
    kept.write_bytes(base.read_bytes())
    sha = hashlib.sha256(base.read_bytes()).hexdigest()
    p['artifacts'][0].update(path=str(base), sha256=sha, proof={'path': str(kept), 'sha256': sha})
    p['pins'][0]['sha256'] = sha
    with pytest.raises(m.Refusal, match='backing'):
        m.plan(p)
    assert base.exists() and child.exists()


def test_unknown_qcow2_chain_fails_closed(lab):
    m, p, target, _ = lab
    (target.parent / 'broken.qcow2').write_bytes(b'QFI\xfbnot a valid image')
    with pytest.raises((m.Refusal, subprocess.CalledProcessError)):
        m.plan(p)



def test_apply_requires_exact_approval_then_audits_real_unlink(lab, monkeypatch, tmp_path):
    m, p, target, kept = lab
    approved = m.plan(p)
    assert hasattr(m, 'apply_plan'), 'explicit execution is missing'
    # Procfs visibility of unrelated root services is an external privileged boundary.
    original = m.process_guard
    monkeypatch.setattr(m, 'process_guard', lambda p, t, strict=False: original(p, t, False))
    with pytest.raises(m.Refusal):
        m.apply_plan(p, 'wrong', ['one'], str(tmp_path / 'bad'))
    assert target.exists()
    result = m.apply_plan(p, approved['plan_sha256'], ['one'], str(tmp_path / 'audit'))
    assert not target.exists() and kept.exists()
    assert result['removed_count'] == 1
    assert result['allocated_unlinked_bytes'] == approved['estimated_recoverable_bytes']
    events = [json.loads(x) for x in (tmp_path / 'audit/events.jsonl').read_text().splitlines()]
    assert [x['event'] for x in events] == ['start', 'intent', 'removed', 'complete']


@pytest.mark.parametrize('change', ['changed', 'selection', 'locked', 'audit-symlink'])
def test_apply_refuses_without_removing_anything(lab, monkeypatch, tmp_path, change):
    import fcntl
    m, p, target, _ = lab
    approved = m.plan(p)
    assert hasattr(m, 'apply_plan'), 'explicit execution is missing'
    original = m.process_guard
    monkeypatch.setattr(m, 'process_guard', lambda p, t, strict=False: original(p, t, False))
    ids = ['one']
    audit = tmp_path / 'audit'
    if change == 'changed': target.write_bytes(b'changed after approval')
    if change == 'selection': ids = []
    if change == 'audit-symlink': audit.symlink_to(target.parent, target_is_directory=True)
    with open(p['locks'][0], 'a') as held:
        if change == 'locked': fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises((m.Refusal, OSError)):
            m.apply_plan(p, approved['plan_sha256'], ids, str(audit))
    assert target.exists()


@pytest.mark.parametrize('exception', [KeyboardInterrupt, SystemExit])
def test_interruption_preserves_write_ahead_audit(lab, monkeypatch, tmp_path, exception):
    m, p, target, _ = lab
    approved = m.plan(p)
    assert hasattr(m, 'apply_plan'), 'explicit execution is missing'
    original = m.process_guard
    monkeypatch.setattr(m, 'process_guard', lambda p, t, strict=False: original(p, t, False))
    def interrupt(*args, **kwargs):
        raise exception()
    monkeypatch.setattr(m.os, 'unlink', interrupt)
    with pytest.raises(exception):
        m.apply_plan(p, approved['plan_sha256'], ['one'], str(tmp_path / 'audit'))
    assert target.exists()
    events = [json.loads(x) for x in (tmp_path / 'audit/events.jsonl').read_text().splitlines()]
    assert events[-2]['event'] == 'intent'
    assert events[-1]['event'] == 'aborted'



def test_iso_member_duplicate_is_verified_without_extracting(lab, tmp_path):
    m, p, target, kept = lab
    tree = tmp_path / 'iso-tree'
    tree.mkdir()
    (tree / 'payload.bin').write_bytes(target.read_bytes())
    iso = tmp_path / 'protected.iso'
    subprocess.run(['xorriso', '-no_rc', '-as', 'mkisofs', '-quiet', '-o', str(iso), str(tree)], check=True, capture_output=True)
    p['pins'] = [{'path': str(iso), 'sha256': hashlib.sha256(iso.read_bytes()).hexdigest()}]
    p['protected'] = [str(iso)]
    p['artifacts'][0]['proof'] = {'path': str(iso), 'member': '/payload.bin', 'sha256': p['artifacts'][0]['sha256']}
    result = m.plan(p)
    assert result['targets'][0]['proof']['member'] == '/payload.bin'
    p['artifacts'][0]['proof']['member'] = '/absent'
    with pytest.raises((m.Refusal, subprocess.SubprocessError)):
        m.plan(p)
    assert target.exists()


def test_inventory_pin_overrides_disposable_label(lab):
    m, p, target, _ = lab
    p['protected'].append(str(target))
    assert m.inventory(p)['files'][0]['classification'] == 'PROTECTED'



def test_squashfs_member_proves_generated_build_payload(lab, tmp_path):
    m, p, target, _ = lab
    tree = tmp_path / 'sfs-tree'
    tree.mkdir()
    (tree / 'payload.bin').write_bytes(target.read_bytes())
    sfs = tmp_path / 'retained.sfs'
    subprocess.run(['mksquashfs', str(tree), str(sfs), '-noappend', '-processors', '1', '-quiet'], check=True, capture_output=True)
    p['pins'] = [{'path': str(sfs), 'sha256': hashlib.sha256(sfs.read_bytes()).hexdigest()}]
    p['protected'] = [str(sfs)]
    p['artifacts'][0]['proof'] = {'path': str(sfs), 'member': '/payload.bin', 'format': 'squashfs', 'sha256': p['artifacts'][0]['sha256']}
    result = m.plan(p)
    assert result['targets'][0]['proof']['format'] == 'squashfs'



def test_ancestor_symlink_is_never_followed(lab, tmp_path):
    m, p, target, _ = lab
    link = tmp_path / 'linked'
    link.symlink_to(target.parent, target_is_directory=True)
    p['roots'] = [str(link)]
    p['artifacts'][0]['path'] = str(link / target.name)
    with pytest.raises((m.Refusal, OSError)):
        m.plan(p)
    assert target.exists()


def test_replaced_root_changes_plan_identity(lab):
    m, p, target, _ = lab
    before = m.plan(p)
    old = target.parent
    moved = old.with_name('moved')
    old.rename(moved)
    old.mkdir()
    (moved / target.name).rename(target)
    assert m.plan(p)['plan_sha256'] != before['plan_sha256']


def test_invalid_backing_symlink_is_ambiguous(lab):
    m, p, target, _ = lab
    (target.parent / 'alias.qcow2').symlink_to(target)
    with pytest.raises((m.Refusal, OSError)):
        m.plan(p)


def test_process_visibility_refusal_is_enforced_on_apply(lab, monkeypatch, tmp_path):
    m, p, target, _ = lab
    approved = m.plan(p)
    def hidden(policy, targets, strict=False):
        if strict: raise m.Refusal('incomplete process visibility')
        return False
    monkeypatch.setattr(m, 'process_guard', hidden)
    with pytest.raises(m.Refusal, match='visibility'):
        m.apply_plan(p, approved['plan_sha256'], ['one'], str(tmp_path / 'audit'))
    assert target.exists()


def test_unselected_unknown_and_failed_evidence_are_retained(lab):
    m, p, target, _ = lab
    p['artifacts'][0]['classification'] = 'ARCHIVE'
    assert m.plan(p)['targets'] == []
    assert target.exists()



def test_filtered_proc_cannot_clear_strict_visibility(lab, monkeypatch):
    m, p, _, _ = lab
    original = m.Path.iterdir
    monkeypatch.setattr(m.Path, 'iterdir', lambda x: iter([]) if str(x) == '/proc' else original(x))
    with pytest.raises(m.Refusal, match='host identity'):
        m.process_guard(p, [], strict=True)


def test_mapped_inode_detected_through_alias_path(lab, monkeypatch):
    import os
    m, p, target, _ = lab
    record = m.file_record(str(target))
    pid = str(os.getpid())
    original_iter = m.Path.iterdir
    original_read = m.Path.read_text
    def iterdir(path):
        if str(path) == '/proc': return iter([m.Path('/proc') / pid])
        if str(path) == '/proc/' + pid + '/fd': return iter([])
        return original_iter(path)
    def read_text(path, *args, **kwargs):
        if str(path) == '/proc/' + pid + '/maps':
            s = target.stat()
            return '00400000-00401000 r--p 00000000 %x:%x %d /alternate-mount/alias\n' % (os.major(s.st_dev), os.minor(s.st_dev), s.st_ino)
        return original_read(path, *args, **kwargs)
    monkeypatch.setattr(m.Path, 'iterdir', iterdir)
    monkeypatch.setattr(m.Path, 'read_text', read_text)
    with pytest.raises(m.Refusal, match='mapped'):
        m.process_guard(p, [record])


def test_cached_proof_rejects_symlink_ancestor_even_with_same_inode(lab, tmp_path):
    m, _, target, _ = lab
    original = tmp_path / 'retained-directory'
    original.mkdir()
    proof_path = original / 'retained.bin'
    proof_path.write_bytes(target.read_bytes())
    record = m.file_record(str(proof_path))
    moved = tmp_path / 'moved-retained-directory'
    original.rename(moved)
    original.symlink_to(moved, target_is_directory=True)
    # The bytes, inode and timestamps still match; the ancestor is no longer safe.
    with pytest.raises((m.Refusal, OSError)):
        m.proof_record({'path': str(proof_path)}, {str(proof_path): record})
    assert target.exists() and proof_path.exists()


def test_default_inventory_is_read_only(tmp_path):
    root = tmp_path / 'wilsof-run'
    root.mkdir()
    artifact = root / 'temporary.bin'
    artifact.write_bytes(b'keep until explicitly approved')
    policy = tmp_path / 'policy.json'
    policy.write_text(json.dumps({'version': 1, 'roots': [str(root)], 'protected': [],
                                  'artifacts': [], 'image_roots': [str(root)], 'locks': []}))
    result = subprocess.run([sys.executable, str(SCRIPT), '--policy', str(policy)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report['files'][0]['classification'] == 'UNKNOWN'
    assert artifact.read_bytes() == b'keep until explicitly approved'
    assert sorted(p.name for p in root.iterdir()) == ['temporary.bin']


def test_terminating_signal_is_not_swallowed_by_proof_reader_selector(tmp_path):
    marker = tmp_path / 'continued-after-cancel'
    code = ('import os,runpy,selectors,signal,threading,pathlib\n'
            f'm=runpy.run_path({str(SCRIPT)!r},run_name="fixture")\n'
            'signal.signal(signal.SIGTERM,m["interrupted"])\n'
            'r,w=os.pipe()\n'
            'selector=selectors.DefaultSelector();selector.register(r,selectors.EVENT_READ)\n'
            'timer=threading.Timer(0.1,lambda:os.kill(os.getpid(),signal.SIGTERM));timer.start()\n'
            'selector.select(2)\n'
            f'pathlib.Path({str(marker)!r}).write_text("unsafe continuation")\n')
    result = subprocess.run([sys.executable, '-I', '-c', code], capture_output=True, timeout=5)
    assert result.returncode == 143
    assert not marker.exists(), 'cancellation was swallowed and execution continued'
