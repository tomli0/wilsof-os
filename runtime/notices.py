"""Stage pinned supplemental notices in both live and freshly installed roots.

This repairs inclusion, not transitive-license/legal/redistribution clearance.
"""
import hashlib
import json
import os
from pathlib import Path
import re

FOLDER = 'assets/notices/dux-shell-2.0.0'
DESTINATION = 'usr/share/licenses/wilsof-supplemental/dux-shell-2.0.0'


def no_links(path):
    path=Path(path)
    if not path.is_absolute() or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Refusing supplemental-notice symlink or relative path')
    return path


def read_notice(path):
    path=no_links(path)
    if not path.is_file() or path.stat().st_size > 2*1024**2:
        raise ValueError('Supplemental notice must be a bounded regular file')
    return path.read_bytes()


def stage(source, target):
    source, target = no_links(source), no_links(target)
    folder = source/FOLDER
    data = read_notice(folder/'PROVENANCE.json')
    record = json.loads(data)
    if (record.get('component')!='dux-shell' or record.get('version')!='2.0.0-1' or
            record.get('upstream_commit')!='9b413296b16721f7679fb62e624cb1ed2433fa58' or
            not isinstance(record.get('files'),dict) or 'LICENSE' not in record['files']):
        raise ValueError('Supplemental-notice provenance rejected')
    payload={'PROVENANCE.json':data}
    for name,expected in record['files'].items():
        if (not re.fullmatch(r'[A-Za-z0-9_.-]+',name) or name in ('.','..','PROVENANCE.json') or
                not isinstance(expected,str) or not re.fullmatch(r'[0-9a-f]{64}',expected)):
            raise ValueError('Supplemental-notice manifest entry rejected')
        content=read_notice(folder/name)
        if hashlib.sha256(content).hexdigest()!=expected:
            raise ValueError('Supplemental-notice bytes do not match provenance')
        payload[name]=content
    destination=no_links(target/DESTINATION)
    # Check every existing destination before creating or replacing anything.
    for name,content in payload.items():
        path=no_links(destination/name)
        if path.exists() and (not path.is_file() or path.read_bytes()!=content):
            raise ValueError('Refusing to overwrite an existing different notice')
    current=target
    for part in Path(DESTINATION).parts:
        current=current/part
        if not current.exists():
            current.mkdir(mode=0o755)
            current.chmod(0o755)  # readable even under a private build supervisor umask
    for name,content in payload.items():
        path=destination/name
        if not path.exists():
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644)
            with os.fdopen(fd,'wb') as stream:stream.write(content)
            path.chmod(0o644)
