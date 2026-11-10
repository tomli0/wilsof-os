#!/usr/bin/env python3
"""Host-only, explicit-manifest artifact maintenance. Default: inventory."""
import argparse
import contextlib
import fcntl
import errno
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
import stat
import signal
import selectors
import tempfile
import time
import sys


class Refusal(ValueError):
    """A safety prerequisite could not be established."""


def canonical(value):
    if not isinstance(value, str) or not value.startswith('/') or str(Path(value)) != value:
        raise Refusal('non-canonical absolute path')
    if '..' in Path(value).parts or any(ord(c) < 32 for c in value):
        raise Refusal('ambiguous path')
    return Path(value)


def directory(path):
    """Open every ancestor without following symlinks."""
    path = canonical(str(path))
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def metadata(s):
    return {k: getattr(s, 'st_' + k) for k in
            ('dev', 'ino', 'mode', 'uid', 'gid', 'size', 'nlink', 'mtime_ns', 'ctime_ns', 'blocks')}


def load_policy(path):
    policy = json.loads(Path(path).read_text())
    if policy.get('version') != 1 or not policy.get('roots'):
        raise Refusal('version 1 and explicit roots required')
    for value in policy['roots']:
        root = canonical(value)
        if len(root.parts) < 4:
            raise Refusal('root is too broad')
        os.close(directory(root))
    return policy


def inventory(policy):
    classes = {a['path']: a['classification'] for a in policy['artifacts']}
    protected = [canonical(x) for x in policy['protected']]
    protected += [canonical(x['path']) for x in policy.get('pins', [])]
    files = []
    for root in policy['roots']:
        def fail(error):
            raise error
        for parent, dirs, names in os.walk(root, followlinks=False, onerror=fail):
            dirs[:] = sorted(d for d in dirs if not Path(parent, d).is_symlink())
            for name in sorted(names):
                p = Path(parent, name)
                s = p.lstat()
                files.append({'path': str(p), 'classification': 'PROTECTED' if any(
                    within(p, pin) for pin in protected) else classes.get(str(p), 'UNKNOWN'),
                              'allocated_bytes': s.st_blocks * 512, 'identity': metadata(s)})
    return {'files': files, 'allocated_bytes': sum(f['allocated_bytes'] for f in files)}



def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def fingerprint(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def file_record(value):
    path = canonical(value)
    parent = directory(path.parent)
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, 'rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise Refusal('not a regular file: ' + value)
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            if metadata(before) != metadata(os.fstat(stream.fileno())):
                raise Refusal('file changed while reading: ' + value)
        return {'path': value, 'sha256': digest, 'identity': metadata(before)}
    finally:
        os.close(parent)


def within(path, root):
    return path == root or path.is_relative_to(root)




def proof_record(proof, retained_cache=None):
    kept = (retained_cache or {}).get(proof['path'])
    if kept is None:
        kept = file_record(proof['path'])
    else:
        kept = dict(kept)
        if metadata(os.stat(proof['path'], follow_symlinks=False)) != kept['identity']:
            raise Refusal('retained archive identity changed')
    if 'member' not in proof:
        return kept
    member = str(canonical(proof['member']))
    # Stream retained ISO bytes; never extract into the host tree or execute a shell.
    format_name = proof.get('format', 'iso')
    if format_name == 'iso':
        command = ['xorriso', '-no_rc', '-abort_on', 'FAILURE', '-return_with', 'SORRY', '32',
                   '-indev', proof['path'], '-osirrox', 'on', '-concat', 'overwrite', '-', member, '--']
    elif format_name == 'squashfs':
        command = ['unsquashfs', '-processors', '1', '-cat', proof['path'], member.lstrip('/')]
    else:
        raise Refusal('unsupported retained archive format')
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors)
        try:
            digest = hashlib.sha256()
            deadline = time.monotonic() + 180
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not selector.select(remaining):
                        raise Refusal('ISO member verification timed out')
                    data = os.read(process.stdout.fileno(), 1024 * 1024)
                    if not data:
                        break
                    digest.update(data)
            if process.wait(timeout=max(0.1, deadline - time.monotonic())) != 0:
                raise Refusal('ISO member read failed')
            kept.update(member=member, content_sha256=digest.hexdigest())
            if 'format' in proof:
                kept['format'] = format_name
            return kept
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
            process.stdout.close()


def validate_target(policy, artifact, all_targets, retained_cache=None):
    path = canonical(artifact['path'])
    roots = [canonical(x) for x in policy['roots']]
    if not any(path != r and within(path, r) for r in roots):
        raise Refusal('outside owned roots: ' + str(path))
    protected = [canonical(x) for x in policy['protected']]
    protected += [canonical(x['path']) for x in policy['pins']]
    if any(within(path, p) for p in protected):
        raise Refusal('protected path: ' + str(path))
    if any(os.path.lexists(p / '.git') for p in path.parents):
        raise Refusal('source repository is protected')
    workflow = artifact['workflow']
    if (not workflow['id'] or workflow['state'] != 'completed' or
            workflow['result'] != 'success' or workflow['pending_acceptance'] is not False):
        raise Refusal('unfinished workflow or unresolved evidence')
    record = file_record(str(path))
    if record['identity']['nlink'] != 1 or record['sha256'] != artifact['sha256']:
        raise Refusal('identity/hash or hardlink refusal')
    proof = artifact['proof']
    kept_path = canonical(proof['path'])
    if str(kept_path) in all_targets or within(kept_path, path):
        raise Refusal('retained proof is selected for deletion')
    if 'member' in proof and str(kept_path) not in {x['path'] for x in policy['pins']}:
        raise Refusal('ISO duplicate proof must be pinned')
    kept = proof_record(proof, retained_cache)
    content_sha = kept.get('content_sha256', kept['sha256'])
    if (content_sha != proof['sha256'] or content_sha != record['sha256'] or
            (kept['identity']['dev'], kept['identity']['ino']) ==
            (record['identity']['dev'], record['identity']['ino'])):
        raise Refusal('retained duplicate is not independently verified')
    return dict(record, id=artifact['id'], proof=kept)



def backing_guard(policy, targets):
    backings = set()
    catalog = []
    def fail(error):
        raise error
    for root in policy['image_roots']:
        os.close(directory(canonical(root)))
        for parent, dirs, names in os.walk(root, followlinks=False, onerror=fail):
            dirs[:] = [d for d in dirs if not Path(parent, d).is_symlink()]
            for name in names:
                path = Path(parent, name)
                s = path.lstat()
                if stat.S_ISLNK(s.st_mode) and path.suffix in ('.qcow', '.qcow2', '.vmdk'):
                    raise Refusal('ambiguous symlink image catalog entry')
                if not stat.S_ISREG(s.st_mode):
                    continue
                with path.open('rb') as stream:
                    magic = stream.read(4)
                if magic != b'QFI\xfb' and path.suffix not in ('.qcow', '.qcow2', '.vmdk'):
                    continue
                cp = subprocess.run(['qemu-img', 'info', '--output=json', '--backing-chain', str(path)],
                                    check=True, capture_output=True, text=True, timeout=30)
                chain = json.loads(cp.stdout)
                if not isinstance(chain, list) or not chain:
                    raise Refusal('unknown backing chain')
                nodes = []
                for node in chain:
                    node_path = canonical(node['filename'])
                    parent_fd = directory(node_path.parent)
                    try:
                        image_fd = os.open(node_path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
                        os.close(image_fd)
                    finally:
                        os.close(parent_fd)
                    nodes.append(str(node_path))
                    if 'backing-filename' in node:
                        backing = node.get('full-backing-filename')
                        if not backing:
                            backing = str(node_path.parent / node['backing-filename'])
                        backings.add(str(canonical(backing)))
                catalog.append({'path': str(path), 'chain': nodes})
    if backings.intersection(t['path'] for t in targets):
        raise Refusal('target is a required QEMU backing image')
    return sorted(catalog, key=lambda x: x['path'])




def host_visibility(policy):
    """Require an independently pinned initial host namespace, not PID enumeration alone."""
    expected = policy.get('host_identity')
    if not isinstance(expected, dict) or not expected:
        raise Refusal('approved host identity is required for destructive process inspection')
    if os.geteuid() != 0:
        raise Refusal('host-wide inspection requires authenticated root')
    status = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines())
    required_caps = (1 << 19) | (1 << 21)  # CAP_SYS_PTRACE and CAP_SYS_ADMIN
    if int(status['CapEff'].strip(), 16) & required_caps != required_caps:
        raise Refusal('host inspection capabilities are incomplete')
    if len(status.get('NSpid', '').split()) != 1:
        raise Refusal('nested PID namespace is unsupported')
    if Path('/proc/self/uid_map').read_text().split() != ['0', '0', '4294967295']:
        raise Refusal('non-initial user mapping is unsupported')
    actual = {'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    for kind in ('pid', 'user'):
        own = Path('/proc/self/ns') / kind
        first = Path('/proc/1/ns') / kind
        if own.stat().st_ino != first.stat().st_ino:
            raise Refusal('procfs PID1 namespace does not match caller')
        actual[kind + '_namespace_inode'] = own.stat().st_ino
        fd = os.open(own, os.O_RDONLY)
        try:
            try:
                parent = fcntl.ioctl(fd, 0xb702)  # Linux NS_GET_PARENT
            except OSError as error:
                if error.errno != errno.EPERM:
                    raise Refusal('cannot establish initial namespace') from error
            else:
                os.close(parent)
                raise Refusal('non-initial namespace is unsupported')
        finally:
            os.close(fd)
    mounts = []
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        left, right = line.split(' - ', 1)
        fields = left.split()
        if fields[4] == '/proc':
            mounts.append((fields, right.split()))
        elif re.match(r'^/proc/[0-9]+(?:/|$)', fields[4]):
            raise Refusal('masked process mount is unsupported')
    if len(mounts) != 1:
        raise Refusal('ambiguous procfs mount')
    fields, extra = mounts[0]
    options = fields[5].split(',') + extra[2].split(',')
    if fields[3] != '/' or extra[0] != 'proc' or any(
            value.startswith(('hidepid=', 'subset=')) and value != 'hidepid=0' for value in options):
        raise Refusal('filtered procfs is unsupported')
    actual['proc_device'] = Path('/proc').stat().st_dev
    if expected != actual:
        raise Refusal('approved host identity does not match current host namespace/boot')
    return actual


def process_guard(policy, targets, strict=False):
    """Read procfs; unobservable processes are NOT clearance to apply."""
    if strict:
        host_visibility(policy)
    identities = {(t['identity']['dev'], t['identity']['ino']) for t in targets}
    roots = [canonical(r) for r in policy['roots']]
    hidden = set()
    for process in Path('/proc').iterdir():
        if not process.name.isdecimal():
            continue
        try:
            for field in ('cwd', 'root'):
                value = Path(os.readlink(process / field))
                if any(within(value, root) for root in roots):
                    raise Refusal('active process directory: ' + process.name)
            command = (process / 'cmdline').read_bytes()
            if any(str(r).encode() in command for r in roots):
                raise Refusal('active workflow command: ' + process.name)
            for fd in (process / 'fd').iterdir():
                try:
                    s = fd.stat()
                    if (s.st_dev, s.st_ino) in identities:
                        raise Refusal('active process file: ' + process.name)
                except FileNotFoundError:
                    continue
            for line in (process / 'maps').read_text().splitlines():
                parts = line.split(None, 5)
                if len(parts) < 5:
                    raise Refusal('unparseable process mapping')
                major, minor = (int(value, 16) for value in parts[3].split(':'))
                if (os.makedev(major, minor), int(parts[4])) in identities:
                    raise Refusal('active mapped file: ' + process.name)
            for line in (process / 'mountinfo').read_text().splitlines():
                fields = line.split()
                for encoded_path in (fields[3], fields[4]):
                    value = Path(re.sub(r'\\([0-7]{3})', lambda m: chr(int(m[1], 8)), encoded_path))
                    if str(value) == '/':
                        continue
                    if any(within(value, r) for r in roots) and any(
                            within(canonical(t['path']), value) or within(value, canonical(t['path']))
                            for t in targets):
                        raise Refusal('active mount dependency: ' + process.name)
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError:
            hidden.add(process.name)
    if strict and hidden:
        raise Refusal('incomplete process visibility; authenticated root inspection required')
    return not hidden


def plan(policy):
    if policy.get('version') != 1 or not policy.get('roots'):
        raise Refusal('explicit versioned policy required')
    for root in policy['roots']:
        if len(canonical(root).parts) < 4:
            raise Refusal('root is too broad')
        os.close(directory(root))
    artifacts = [a for a in policy['artifacts'] if a['classification'] == 'DISPOSABLE']
    all_targets = {a['path'] for a in artifacts}
    if len(all_targets) != len(artifacts) or len({a['id'] for a in artifacts}) != len(artifacts):
        raise Refusal('duplicate target path or ID')
    pins = []
    for pin in policy['pins']:
        record = file_record(pin['path'])
        if record['sha256'] != pin['sha256']:
            raise Refusal('pinned artifact changed: ' + pin['path'])
        pins.append(record)
    retained_cache = {p['path']: p for p in pins}
    targets = [validate_target(policy, a, all_targets, retained_cache) for a in artifacts]
    images = backing_guard(policy, targets)
    process_guard(policy, targets)
    root_identities = {}
    for value in policy['roots']:
        fd = directory(value)
        try:
            root_identities[value] = {k: v for k, v in metadata(os.fstat(fd)).items()
                                      if k in ('dev', 'ino', 'mode', 'uid', 'gid')}
        finally:
            os.close(fd)
    result = {'version': 1, 'policy_sha256': fingerprint(policy), 'pins': pins, 'images': images,
              'root_identities': root_identities,
              'targets': targets, 'estimated_recoverable_bytes':
              sum(t['identity']['blocks'] * 512 for t in targets)}
    result['plan_sha256'] = fingerprint(result)
    return result



def space(policy):
    result = {}
    for root in policy['roots']:
        s = os.stat(root)
        v = os.statvfs(root)
        result[str(s.st_dev)] = {'total': v.f_blocks * v.f_frsize,
                                 'available': v.f_bavail * v.f_frsize,
                                 'free': v.f_bfree * v.f_frsize}
    return result


def apply_plan(policy, approved_sha, target_ids, audit_path):
    """All-or-refuse preflight; then durable, per-file irreversible unlink."""
    if not policy.get('locks') or not policy.get('pins') or not policy.get('image_roots'):
        raise Refusal('explicit locks, pins and image discovery roots required')
    audit = canonical(audit_path)
    if any(within(audit, canonical(r)) or within(canonical(r), audit) for r in policy['roots']):
        raise Refusal('audit must be outside deletion roots')
    process_guard(policy, [], strict=True)
    with contextlib.ExitStack() as stack:
        for value in sorted(set(policy['locks'])):
            lock = canonical(value)
            parent = directory(lock.parent)
            stack.callback(os.close, parent)
            fd = os.open(lock.name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,
                         0o600, dir_fd=parent)
            stack.callback(os.close, fd)
            s = os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1:
                raise Refusal('ambiguous lock file')
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        current = plan(policy)
        if current['plan_sha256'] != approved_sha:
            raise Refusal('plan changed or approval does not match')
        expected_ids = [t['id'] for t in current['targets']]
        if not target_ids or sorted(target_ids) != sorted(expected_ids):
            raise Refusal('explicit target selection must exactly match plan')
        process_guard(policy, current['targets'], strict=True)
        parent = directory(audit.parent)
        stack.callback(os.close, parent)
        os.mkdir(audit.name, 0o700, dir_fd=parent)
        os.fsync(parent)
        audit_fd = directory(audit)
        stack.callback(os.close, audit_fd)
        fd = os.open('events.jsonl', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=audit_fd)
        log = stack.enter_context(os.fdopen(fd, 'w'))
        os.fsync(audit_fd)
        def event(kind, **fields):
            log.write(json.dumps(dict(event=kind, time_ns=time.time_ns(), **fields), sort_keys=True) + '\n')
            log.flush()
            os.fsync(log.fileno())
        before = space(policy)
        removed = []
        event('start', plan=current, before=before)
        try:
            for target in current['targets']:
                path = canonical(target['path'])
                # Reopen ancestors and bind both hash/identity and unlink to the same parent FD.
                parent_fd = directory(path.parent)
                try:
                    fresh = file_record(str(path))
                    if fresh != {k: target[k] for k in ('path', 'sha256', 'identity')}:
                        raise Refusal('target changed immediately before unlink')
                    proof = proof_record(target['proof'], {p['path']: p for p in current['pins']})
                    if proof != target['proof']:
                        raise Refusal('retained proof changed immediately before unlink')
                    process_guard(policy, [target], strict=True)
                    s = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
                    if metadata(s) != target['identity']:
                        raise Refusal('final descriptor-relative identity mismatch')
                    event('intent', target=target)
                    os.unlink(path.name, dir_fd=parent_fd)
                    os.fsync(parent_fd)
                    removed.append(target)
                    event('removed', id=target['id'], path=str(path), allocated_bytes=s.st_blocks * 512)
                finally:
                    os.close(parent_fd)
            for pin in current['pins']:
                if file_record(pin['path']) != pin:
                    raise Refusal('protected artifact changed during maintenance')
            after = space(policy)
            result = {'removed_count': len(removed), 'allocated_unlinked_bytes':
                      sum(t['identity']['blocks'] * 512 for t in removed),
                      'before': before, 'after': after, 'available_delta_bytes':
                      {dev: after[dev]['available'] - value['available'] for dev, value in before.items()}}
            event('complete', **result)
            return result
        except BaseException as error:
            event('aborted', error=type(error).__name__, removed_ids=[t['id'] for t in removed], after=space(policy))
            raise


def interrupted(signum, frame):
    # A second terminating signal must not interrupt the short audit/FD unwinding path.
    for value in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(value, signal.SIG_IGN)
    raise InterruptedError('maintenance interrupted by signal ' + str(signum))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', required=True)
    parser.add_argument('mode', nargs='?', choices=['inventory', 'plan', 'apply'], default='inventory')
    parser.add_argument('--approve-policy')
    parser.add_argument('--approve-plan')
    parser.add_argument('--targets-file', help='JSON array of exact approved artifact IDs')
    parser.add_argument('--audit', help='new private audit directory (must not exist)')
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy)
        if args.mode == 'inventory':
            result = inventory(policy)
        elif args.mode == 'plan':
            result = plan(policy)
        else:
            if (not args.audit or not args.targets_file or not args.approve_plan or
                    args.approve_policy != fingerprint(policy)):
                raise Refusal('apply requires exact policy/plan approval, targets file and new audit path')
            for value in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
                signal.signal(value, interrupted)
            result = apply_plan(policy, args.approve_plan, json.loads(Path(args.targets_file).read_text()), args.audit)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('REFUSED: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
