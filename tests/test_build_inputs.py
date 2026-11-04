"""Controlled build inputs: deterministic metadata, explicit provenance, no ISO."""
import json
import os
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_profile_clock_comes_only_from_source_date_epoch(tmp_path):
    tools = tmp_path / 'tools'
    tools.mkdir()
    date = tools / 'date'
    date.write_text('#!/bin/sh\ncase "$*" in *--date=*|*\" -d \"*) exec /usr/bin/date "$@";; *) printf "%s\\n" "$TEST_MONTH";; esac\n')
    date.chmod(0o755)
    outputs = []
    for month in ('202601', '202602'):
        result = subprocess.run(['bash', '-c', 'declare -A file_permissions; source "$1"; printf "%s\\n%s\\n" "$iso_label" "$iso_version"', '-', str(ROOT / 'iso/profiledef.sh')], env={**os.environ, 'PATH': str(tools) + ':' + os.environ['PATH'], 'SOURCE_DATE_EPOCH': '1767225600', 'WILSOF_ISO_VERSION': 'fixed', 'TEST_MONTH': month}, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        outputs.append(result.stdout)
    assert outputs[0] == outputs[1] == 'WILSOF_202601\nfixed\n'


def test_repeated_materialization_records_equivalent_inputs_not_wall_clock(tmp_path):
    upstream = tmp_path / 'releng'
    (upstream / 'airootfs').mkdir(parents=True)
    manifest = upstream / 'packages.x86_64'
    manifest.write_text('base\n')
    prepare = runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare']
    records = []
    for name in ('one', 'two'):
        output = tmp_path / name
        prepare(upstream, output, ROOT, 'a' * 40)
        record = output / 'BUILD-SOURCE.json'
        assert record.is_file(), 'A source marker alone does not identify releng/source inputs'
        records.append(record.read_bytes())
        os.utime(manifest, (1, 1))
    assert records[0] == records[1]
    manifest.write_text('base\nextra-package\n')
    prepare(upstream, tmp_path / 'three', ROOT, 'a' * 40)
    changed = json.loads((tmp_path / 'three/BUILD-SOURCE.json').read_text())
    assert changed != json.loads(records[0]), 'Changed releng inputs must change build identity'


def test_profile_rejects_missing_epoch_instead_of_falling_back_to_now():
    env = dict(os.environ)
    env.pop('SOURCE_DATE_EPOCH', None)
    result = subprocess.run(['bash', '-c', 'declare -A file_permissions; source "$1"', '-', str(ROOT / 'iso/profiledef.sh')], env=env, capture_output=True, text=True)
    assert result.returncode != 0
