#!/usr/bin/env python3
"""Opt-in real user-manager regression. Run only in a disposable QEMU guest.

Retains fixtures/journals under HOME; cleans only its own new unit links/jobs.
No DMS, desktop, real graphical target, disk or existing unit is started/stopped.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import unittest
import uuid

SOURCE = None
EVIDENCE = None


def run(*args, check=True):
    return subprocess.run(args, check=check, capture_output=True, text=True, timeout=20)


def wait_for(predicate, message, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(.2)
    raise AssertionError(message)


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.prefix = 'wilsof-qa37-' + uuid.uuid4().hex[:12]
        self.case = EVIDENCE / self.prefix
        self.case.mkdir(mode=0o700, parents=True)
        self.names = {key: self.prefix + '-' + key + suffix for key, suffix in
                      [('dms', '.service'), ('wallpaper', '.service'),
                       ('session', '.target'), ('graphical', '.target')]}
        self.links = []

    def tearDown(self):
        for name in self.names.values():
            run('systemctl', '--user', 'stop', name, check=False)
        journal = run('journalctl', '--user', '--no-pager', '-o', 'short-iso',
                      *sum((['-u', name] for name in self.names.values()), []), check=False)
        (self.case / 'journal.log').write_text(journal.stdout + journal.stderr)
        for name in self.names.values():
            run('systemctl', '--user', 'reset-failed', name, check=False)
        for link in self.links:
            if link.is_symlink() and link.readlink().parent == self.case:
                link.unlink()
        run('systemctl', '--user', 'daemon-reload')

    def count(self, name):
        p = self.case / (name + '.count')
        return int(p.read_text()) if p.exists() else 0

    def active(self, key):
        return run('systemctl', '--user', 'is-active', self.names[key], check=False).stdout.strip()

    def prepare(self, *, use_current=True, fail_first=True, permanent=False,
                helper_failure=False, condition=True, post_failure=False, delay=0):
        stub = self.case / 'daemon.py'
        stub.write_text('import pathlib,subprocess,time\n'
                        f'p=pathlib.Path({str(self.case / "dms.count")!r})\n'
                        'n=int(p.read_text())+1 if p.exists() else 1\n'
                        'pending=p.with_suffix(".next")\npending.write_text(str(n))\npending.replace(p)\n'
                        f'if {permanent!r} or ({fail_first!r} and n==1): raise SystemExit(1)\n'
                        f'time.sleep({delay})\n'
                        'subprocess.run(["systemd-notify","--ready"],check=True)\n'
                        'while True:time.sleep(1)\n')
        helper = self.case / 'wallpaper.py'
        helper.write_text('from pathlib import Path\n'
                          f'p=Path({str(self.case / "wallpaper.count")!r})\n'
                          'n=int(p.read_text())+1 if p.exists() else 1\n'
                          'pending=p.with_suffix(".next")\npending.write_text(str(n))\npending.replace(p)\n'
                          f'raise SystemExit({1 if helper_failure else 0})\n')
        dropin = (SOURCE / 'config/systemd/dms-wilsof.conf').read_text() if use_current else '[Service]\n'
        hook = '\n'.join(l for l in dropin.splitlines() if l.startswith('ExecStartPost='))
        if post_failure:
            self.assertTrue(hook.startswith('ExecStartPost=-'))
            hook = 'ExecStartPost=-/usr/bin/false'
        hook = hook.replace('wilsof-wallpaper.service', self.names['wallpaper'])
        dms = ('[Unit]\nStartLimitIntervalSec=20\nStartLimitBurst=3\n'
               f'PartOf={self.names["graphical"]}\n'
               '[Service]\nType=notify\nNotifyAccess=all\nRestart=on-failure\nRestartSec=.2\n'
               f'ExecStart=/usr/bin/python3 {stub}\nTimeoutStartSec=10\n{hook}\n')
        wallpaper = (SOURCE / 'config/systemd/wilsof-wallpaper.service').read_text()
        wallpaper = wallpaper.replace('dms.service', self.names['dms'])
        wallpaper = wallpaper.replace('wilsof-session.target', self.names['session'])
        wallpaper = wallpaper.replace('ExecCondition=/usr/bin/test -x /usr/bin/dms',
                                      'ExecCondition=/usr/bin/' + ('true' if condition else 'false'))
        wallpaper = wallpaper.replace('ExecStart=%h/.local/bin/wilsof-apply-wallpaper',
                                      f'ExecStart=/usr/bin/python3 {helper}')
        session = (SOURCE / 'config/systemd/wilsof-session.target').read_text()
        for old, key in [('graphical-session.target', 'graphical'), ('dms.service', 'dms'),
                         ('wilsof-wallpaper.service', 'wallpaper')]:
            session = session.replace(old, self.names[key])
        definitions = {'dms': dms, 'wallpaper': wallpaper, 'session': session,
                       'graphical': '[Unit]\nDescription=Disposable QA graphical target\n'}
        link_root = Path.home() / '.config/systemd/user'
        link_root.mkdir(parents=True, exist_ok=True)
        for key, text in definitions.items():
            unit = self.case / self.names[key]
            unit.write_text(text)
            link = link_root / unit.name
            assert not link.exists() and not link.is_symlink()
            link.symlink_to(unit)
            self.links.append(link)
        run('systemctl', '--user', 'daemon-reload')
        verification = run('systemd-analyze', '--user', 'verify',
                           *[str(self.case / n) for n in self.names.values()], check=False)
        (self.case / 'verify.log').write_text(verification.stdout + verification.stderr)
        self.assertEqual(verification.returncode, 0, verification.stderr)
        run('systemctl', '--user', '--no-block', 'start', self.names['session'])

    def test_original_dependency_job_is_not_reactivated(self):
        self.prepare(use_current=False)
        wait_for(lambda: self.active('dms') == 'active', 'mock DMS did not recover')
        time.sleep(1)
        self.assertEqual(self.count('dms'), 2)
        self.assertEqual(self.count('wallpaper'), 0)
        j = run('journalctl', '--user', '-u', self.names['wallpaper'], '--no-pager').stdout
        self.assertIn('dependency', j)

    def test_current_dropin_recovers_and_explicit_restart_runs_once(self):
        self.prepare()
        wait_for(lambda: self.active('dms') == 'active', 'mock DMS did not recover')
        wait_for(lambda: self.count('wallpaper') >= 1, 'wallpaper not reactivated after dependency failure')
        time.sleep(.5)
        self.assertEqual(self.count('wallpaper'), 1, 'duplicate activation/retry storm')
        run('systemctl', '--user', 'restart', self.names['dms'])
        wait_for(lambda: self.count('wallpaper') >= 2, 'explicit restart did not reactivate wallpaper')
        time.sleep(.5)
        self.assertEqual(self.count('wallpaper'), 2)
        self.assertEqual(self.active('dms'), 'active')

    def test_cosmetic_failure_is_not_a_dms_restart_loop(self):
        self.prepare(fail_first=False, helper_failure=True)
        wait_for(lambda: self.count('wallpaper') >= 1, 'helper was not invoked')
        wait_for(lambda: self.active('wallpaper') == 'failed', 'cosmetic failure not visible')
        time.sleep(.5)
        self.assertEqual(self.active('dms'), 'active')
        self.assertEqual((self.count('dms'), self.count('wallpaper')), (1, 1))

    def test_queue_error_is_failure_isolated(self):
        self.prepare(fail_first=False, post_failure=True)
        wait_for(lambda: self.active('dms') == 'active', 'ignored post-hook failed DMS')
        self.assertEqual(self.count('dms'), 1)

    def test_missing_binary_condition_skips_helper(self):
        self.prepare(fail_first=False, condition=False)
        wait_for(lambda: self.active('dms') == 'active', 'mock DMS did not start')
        time.sleep(.5)
        self.assertEqual(self.count('wallpaper'), 0)
        self.assertEqual(self.active('dms'), 'active')

    def test_permanent_start_failure_is_bounded(self):
        self.prepare(permanent=True)
        wait_for(lambda: self.count('dms') >= 3, 'start-limit fixture did not run')
        wait_for(lambda: self.active('dms') == 'failed', 'permanent failure was not visible')
        self.assertEqual(self.count('wallpaper'), 0)
        self.assertEqual(self.count('dms'), 3)

    def test_logout_cancels_pending_start_without_a_helper(self):
        self.prepare(fail_first=False, delay=4)
        wait_for(lambda: self.count('dms') == 1, 'pending DMS did not start')
        run('systemctl', '--user', 'stop', self.names['graphical'])
        wait_for(lambda: self.active('dms') == 'inactive', 'DMS not stopped by session teardown')
        self.assertEqual(self.count('wallpaper'), 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args, rest = parser.parse_known_args()
    if os.geteuid() == 0 or os.environ.get('WILSOF_TARGET_VM') != '1':
        parser.error('requires an explicitly designated disposable VM and non-root session user')
    if run('systemd-detect-virt', check=False).stdout.strip() not in ('qemu', 'kvm'):
        parser.error('refusing outside QEMU/KVM')
    SOURCE, EVIDENCE = args.source.resolve(), args.evidence.resolve()
    unittest.main(argv=[__file__] + rest, verbosity=2)
