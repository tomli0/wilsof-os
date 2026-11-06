"""Unprivileged observer boundary tests; no actual desktop/session actions."""
from pathlib import Path
import runpy
import json
import os
import socket
import struct
import fcntl
import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    p = ROOT / 'bin/wilsof-lock-observer'
    assert p.is_file(), 'Missing native observer'
    return runpy.run_path(str(p))


@pytest.mark.parametrize('payload', ['{}','{"unlock":true}','{"prepare":"old"}','{"prepare":"'+'a'*32+'","unlocked":true}', '{'])
def test_only_bounded_prepare_requests_are_accepted(payload):
    with pytest.raises(ValueError):api()['parse_request'](payload)


def test_prepare_token_is_not_an_unlock_authorization():
    assert api()['parse_request'](json.dumps({'prepare':'a'*32})) == 'a'*32


def test_guard_probe_preserves_inode_and_detects_real_flock(tmp_path):
    f = tmp_path / 'guard';m=api()
    assert not m['guard_busy'](f)
    inode=f.stat().st_ino
    with f.open('r+') as held:
        fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert m['guard_busy'](f)
    assert not m['guard_busy'](f) and f.stat().st_ino==inode


@pytest.mark.parametrize('mutation',['symlink','hardlink','mode'])
def test_unsafe_guard_is_rejected(tmp_path,mutation):
    m=api();p=tmp_path/'guard';other=tmp_path/'other';other.write_text('untouched');other.chmod(0o600)
    if mutation=='symlink':p.symlink_to(other)
    elif mutation=='hardlink':os.link(other,p)
    else:p.write_text('');p.chmod(0o666)
    with pytest.raises((ValueError,OSError)):m['guard_busy'](p)
    assert other.read_text()=='untouched'
