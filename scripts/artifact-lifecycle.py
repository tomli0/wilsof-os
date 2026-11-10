#!/usr/bin/env python3
"""Host-only storage admission/catalog. Never deletes files or authorizes builds."""
import argparse
import contextlib
import collections
import stat
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time

GIB = 1024 ** 3
RESERVE = 5 * GIB
MAX_BUDGET = 25 * GIB
LIMITS = {'iso': 2, 'qa-disk': 2, 'build-workspace': 1}
CACHE_LIMIT = 6 * GIB
EVIDENCE_LIMIT = 256 * 1024 ** 2
LOG_DAYS = 7


@contextlib.contextmanager
def locked(path):
    canonical(str(path))
    fd = os.open(str(path) + '.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as stream:
        identity = os.fstat(stream.fileno())
        if not stat.S_ISREG(identity.st_mode) or identity.st_nlink != 1:
            raise ValueError('ambiguous catalog lock')
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        canonical(str(path))
        yield


def usage(path):
    if not path.exists():
        return 0, []
    entries = [path]
    if path.is_dir():
        def fail(error):
            raise error
        for parent, dirs, files in os.walk(path, followlinks=False, onerror=fail):
            dirs[:] = [d for d in dirs if not Path(parent, d).is_symlink()]
            entries.extend(Path(parent, n) for n in dirs)
            entries.extend(Path(parent, n) for n in files)
    seen = set()
    total = 0
    files = []
    for entry in entries:
        s = entry.lstat()
        if stat.S_ISLNK(s.st_mode):
            continue  # Never read or recurse through an alias outside this artifact.
        key = (s.st_dev, s.st_ino)
        if key not in seen:
            total += s.st_blocks * 512
            seen.add(key)
        if stat.S_ISREG(s.st_mode):
            files.append((str(entry), s.st_mtime))
    return total, files


def audit(catalog, state=None) -> dict:
    path = canonical(catalog)
    if state is None:
        state = json.loads(path.read_text()) if path.exists() else {'schema': 1, 'workflows': []}
    if type(state.get('schema')) is not int or state['schema'] != 1 or not isinstance(state.get('workflows'), list):
        raise ValueError('invalid catalog')
    totals = collections.Counter()
    counts = collections.Counter()
    reservations = collections.Counter()
    filesystems = {}
    workflow_usage = []
    violations = []
    now = time.time()
    for workflow in state['workflows']:
        observed = 0
        device = None
        for artifact in workflow['artifacts']:
            target = canonical(artifact['path'])
            size, files = usage(target)
            observed += size
            parent = target.parent
            while not parent.exists():
                parent = parent.parent
            device = parent.stat().st_dev
            if device not in filesystems:
                space = os.statvfs(parent)
                filesystems[device] = space.f_bavail * space.f_frsize
            exception = (artifact['classification'] in ('PROTECTED', 'ARCHIVE') and
                         artifact.get('exception_reason'))
            totals[artifact['kind']] += size
            if not exception and (target.exists() or workflow['state'] in ('ACTIVE', 'CLEANUP_PENDING')):
                counts[artifact['kind']] += (max(1, sum(p.endswith('.iso') for p, _ in files))
                                             if artifact['kind'] == 'iso' else 1)
            if exception:
                continue
            if artifact['kind'] == 'log' and any(now - modified > LOG_DAYS * 86400 for _, modified in files):
                violations.append('ordinary logs older than 7 days: ' + artifact['path'])
            if artifact['kind'] == 'evidence' and size > EVIDENCE_LIMIT:
                violations.append('failure evidence exceeds bounded receipt/reproducer budget: ' + artifact['path'])
        budget = workflow['budget_bytes']
        workflow_usage.append(dict(workflow=workflow['workflow'], allocated_bytes=observed, budget_bytes=budget))
        # Zero-budget ARCHIVE records are explicit imported historical custody, not new allocation.
        if budget > 0 and observed > budget:
            violations.append('workflow budget exceeded: ' + workflow['workflow'])
        if device is not None and workflow['state'] == 'ACTIVE':
            reservations[device] += max(0, budget - observed)
    for device, available in filesystems.items():
        if available < RESERVE + reservations[device]:
            violations.append('emergency reserve or outstanding reservation capacity exhausted: ' + str(device))
    if totals['cache'] > CACHE_LIMIT:
        violations.append('cache exceeds 6 GiB; classify/clean exact regenerable entries before continuing')
    for kind, limit in LIMITS.items():
        if counts[kind] > limit:
            violations.append('artifact limit exceeded: ' + kind)
    return dict(allocated_bytes=dict(totals), active_counts=dict(counts),
                workflow_usage=workflow_usage, available_bytes=filesystems, violations=violations)


def canonical(value):
    path = Path(value)
    if not path.is_absolute() or str(path) != value or '..' in path.parts:
        raise ValueError('canonical absolute path required')
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('symlink path refused')
    return path


def save(path, state):
    temporary = path.with_name(path.name + '.new-' + str(os.getpid()))
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(state, stream, sort_keys=True, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if temporary.exists():
            temporary.unlink()  # Only this invocation's exclusive tiny catalog staging file.


def complete(catalog, workflow, exit_code):
    path = canonical(catalog)
    with locked(path):
        state = json.loads(path.read_text())
        matches = [w for w in state['workflows'] if w['workflow'] == workflow]
        if len(matches) != 1 or type(exit_code) is not int:
            raise ValueError('exact workflow and integer exit code required')
        record = matches[0]
        remaining = [a['path'] for a in record['artifacts']
                     if a['classification'] == 'DISPOSABLE' and canonical(a['path']).exists()]
        record.update(state=('RETAIN' if exit_code else 'CLEANUP_PENDING' if remaining else 'COMPLETE'),
                      exit_code=exit_code, finished_ns=time.time_ns(), cleanup_pending=remaining)
        record['violations'] = audit(catalog, state)['violations']
        if record['violations']:
            record['state'] = 'RETAIN'
        save(path, state)
        return record


def register(catalog, spec):
    path = canonical(catalog)
    if not isinstance(spec, dict) or type(spec.get('schema')) is not int or (spec.get('schema') != 1 or not all(isinstance(spec.get(k), str) and spec[k].strip()
                                         for k in ('owner', 'workflow', 'purpose'))):
        raise ValueError('workflow custody required')
    if not spec.get('artifacts'):
        raise ValueError('explicit artifacts required')
    budget = spec.get('budget_bytes')
    if type(budget) is not int or not 0 < budget <= MAX_BUDGET:
        raise ValueError('bounded positive workflow budget required')
    parent = canonical(spec['artifacts'][0]['path']).parent
    while not parent.exists():
        parent = parent.parent
    space = os.statvfs(parent)
    if space.f_bavail * space.f_frsize < budget + RESERVE:
        raise ValueError('insufficient capacity for peak allocation and emergency reserve')
    paths = [a['path'] for a in spec['artifacts']]
    if len(paths) != len(set(paths)):
        raise ValueError('duplicate artifact path')
    for artifact in spec['artifacts']:
        target = canonical(artifact['path'])
        nearest = target.parent
        while not nearest.exists():
            nearest = nearest.parent
        if nearest.stat().st_dev != parent.stat().st_dev:
            raise ValueError('one workflow budget must use one filesystem')
        if target == path or path.is_relative_to(target):
            raise ValueError('catalog must be outside allocated artifacts')
        if target.exists():
            raise ValueError('new allocation must not already exist')
        if (artifact.get('kind') not in (*LIMITS, 'cache', 'log', 'evidence') or
                artifact.get('classification') not in ('PROTECTED', 'DISPOSABLE', 'ARCHIVE') or
                not isinstance(artifact.get('dependencies'), list) or
                not artifact.get('cleanup_condition')):
            raise ValueError('artifact retention/dependencies/cleanup condition required')
    with locked(path):
        status = audit(catalog)
        if status['violations']:
            raise ValueError('; '.join(status['violations']))
        state = json.loads(path.read_text()) if path.exists() else {'schema': 1, 'workflows': []}
        old_paths = {a['path'] for w in state['workflows'] for a in w['artifacts']}
        if old_paths.intersection(paths):
            raise ValueError('duplicate catalog artifact path')
        if any(w['workflow'] == spec['workflow'] for w in state['workflows']):
            raise ValueError('workflow already registered')
        record: dict = dict(spec, created_ns=time.time_ns(), state='ACTIVE')
        for kind, limit in LIMITS.items():
            if sum(a['kind'] == kind and not (
                    a['classification'] in ('PROTECTED', 'ARCHIVE') and
                    a.get('exception_reason')) for a in record['artifacts']) + status['active_counts'].get(kind, 0) > limit:
                raise ValueError('artifact limit exceeded: ' + kind)
        pending = sum(w['budget_bytes'] for w in state['workflows']
                      if w['state'] == 'ACTIVE')
        space = os.statvfs(parent)
        if space.f_bavail * space.f_frsize < budget + pending + RESERVE:
            raise ValueError('insufficient capacity after concurrent reservations')
        state['workflows'].append(record)
        save(path, state)
        return record


def validate_build_admission(catalog, receipt, workflow, source, work, out):
    """Read-only handoff from a host supervisor that holds the real project lock.

    The isolated root cannot inspect hidden historical host artifacts. Admission
    and finalization therefore occur on the host; never re-inventory an empty
    sandbox or mark its incomplete view as a completed host catalog.
    """
    receipt=canonical(receipt)
    info=receipt.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or stat.S_IMODE(info.st_mode)!=0o400 or info.st_nlink!=1 or info.st_size>4096:
        raise ValueError('root-owned immutable host admission receipt required')
    data=json.loads(receipt.read_text())
    raw=canonical(catalog).read_bytes()
    expected=dict(schema=1,scope='host-admitted-isolated-build',catalog_sha256=hashlib.sha256(raw).hexdigest(),workflow=workflow,source_commit=source,work=work,out=out)
    if data!=expected:raise ValueError('host admission identity/catalog changed')
    state=json.loads(raw)
    matches=[w for w in state.get('workflows',[]) if w['workflow']==workflow]
    if state.get('inventory_complete') is not True or len(matches)!=1:
        raise ValueError('existing inventoried host admission required')
    record=matches[0]
    expected_paths=[(work,'build-workspace','DISPOSABLE'),(work+'-profile','cache','DISPOSABLE'),(out,'iso','PROTECTED')]
    if (record['state']!='ACTIVE' or record['budget_bytes']!=MAX_BUDGET or
            record['purpose']!='Sequential isolated ISO build from '+source or
            [(a['path'],a['kind'],a['classification']) for a in record['artifacts']]!=expected_paths):
        raise ValueError('host build reservation changed')
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('register', 'check', 'complete', 'build-begin'))
    parser.add_argument('--catalog', required=True)
    parser.add_argument('--spec')
    parser.add_argument('--workflow')
    parser.add_argument('--exit-code', type=int)
    parser.add_argument('--work')
    parser.add_argument('--out')
    parser.add_argument('--source')
    args = parser.parse_args()
    try:
        # Initialization/import is a separate inventoried maintenance operation.
        existing = canonical(args.catalog)
        if not existing.is_file():
            raise ValueError('existing inventoried catalog required; implicit initialization refused')
        if json.loads(existing.read_text()).get('inventory_complete') is not True:
            raise ValueError('existing catalog has no completed inventory')
        if args.mode == 'register':
            result = register(args.catalog, json.loads(Path(args.spec).read_text()))
        elif args.mode == 'complete':
            result = complete(args.catalog, args.workflow, args.exit_code)
        elif args.mode == 'check':
            result = audit(args.catalog)
        else:
            if not all((args.workflow, args.source, args.work, args.out)):
                raise ValueError('build workflow/source/work/output required')
            artifacts = []
            for value, kind, classification in (
                    (args.work, 'build-workspace', 'DISPOSABLE'),
                    (args.work + '-profile', 'cache', 'DISPOSABLE'),
                    (args.out, 'iso', 'PROTECTED')):
                artifacts.append(dict(path=value, kind=kind, classification=classification,
                                      dependencies=[args.source], cleanup_condition=(
                    'Preserve candidate/input manifest; retire only after replacement acceptance'
                    if classification == 'PROTECTED' else
                    'Namespace exited, image and essential inputs preserved, exact maintenance apply verified')))
            result = register(args.catalog, dict(schema=1, owner='wilsof-build', workflow=args.workflow,
                              purpose='Sequential isolated ISO build from ' + args.source,
                              budget_bytes=MAX_BUDGET, artifacts=artifacts))
        print(json.dumps(result, sort_keys=True))
        if result.get('violations'):
            parser.exit(1)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, 'REFUSED: ' + str(error) + '\n')
