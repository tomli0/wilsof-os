"""Supplemental notices are payload bytes, not a legal-clearance assertion."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api():
    path=ROOT/'runtime/notices.py'
    assert path.is_file(), 'Missing supplemental-notice staging helper'
    spec=importlib.util.spec_from_file_location('notices',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_notices_are_pinned_staged_readably_and_idempotent(tmp_path):
    module=api();target=tmp_path/'target';target.mkdir()
    module.stage(ROOT,target);module.stage(ROOT,target)
    folder=target/'usr/share/licenses/wilsof-supplemental/dux-shell-2.0.0'
    assert (folder/'LICENSE').read_bytes()==(ROOT/'assets/notices/dux-shell-2.0.0/LICENSE').read_bytes()
    assert (folder/'LICENSE').stat().st_mode & 0o777 == 0o644
    assert json.loads((folder/'PROVENANCE.json').read_text())['upstream_commit']=='9b413296b16721f7679fb62e624cb1ed2433fa58'


def test_notice_target_symlink_is_refused_without_overwrite(tmp_path):
    module=api();target=tmp_path/'target';target.mkdir()
    outside=tmp_path/'outside';outside.mkdir();(target/'usr').symlink_to(outside,target_is_directory=True)
    with pytest.raises(ValueError):module.stage(ROOT,target)
    assert list(outside.iterdir())==[]


def test_notice_fifo_is_rejected_before_read_or_target_writes(tmp_path,monkeypatch):
    import os
    module=api();source=tmp_path/'source';target=tmp_path/'target';target.mkdir()
    folder=source/'assets/notices/dux-shell-2.0.0';folder.mkdir(parents=True)
    fifo=folder/'PROVENANCE.json';os.mkfifo(fifo)
    original=Path.read_bytes
    def read(path):
        if path==fifo:pytest.fail('Notice staging attempted an unbounded FIFO read')
        return original(path)
    monkeypatch.setattr(Path,'read_bytes',read)
    with pytest.raises(ValueError):module.stage(source,target)
    assert list(target.iterdir())==[]


def test_notice_payload_reaches_live_profile_and_target_provisioning(tmp_path):
    api()
    import runpy
    upstream=tmp_path/'releng';(upstream/'airootfs').mkdir(parents=True)
    (upstream/'packages.x86_64').write_text('base\n')
    output=tmp_path/'profile'
    runpy.run_path(str(ROOT/'scripts/prepare-iso.py'))['prepare'](upstream,output,ROOT,'a'*40)
    assert (output/'airootfs/usr/share/licenses/wilsof-supplemental/dux-shell-2.0.0/LICENSE').is_file()
    assert 'notices' in (ROOT/'runtime/provision-target').read_text()
