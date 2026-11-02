"""Run actual build path validator before any directory creation."""
from pathlib import Path
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[1]


def validate(work, out):
    script = (ROOT / 'scripts/build-iso.sh').read_text().split("<<'PY'\n", 1)[1].split('\nPY', 1)[0]
    return subprocess.run(['python3', '-', 'a' * 40, str(work), str(out)], input=script, text=True, capture_output=True)


@pytest.mark.parametrize('case', ['equal-profile', 'inside-profile', 'profile-inside-output', 'symlink-profile', 'alias-work'])
def test_canonical_work_profile_output_are_pairwise_disjoint(tmp_path, case):
    work = tmp_path / 'work'
    if case == 'equal-profile': out = tmp_path / 'work-profile'
    elif case == 'inside-profile': out = tmp_path / 'work-profile/out'
    elif case == 'profile-inside-output':
        work = tmp_path / 'out/work'; out = tmp_path / 'out'
    elif case == 'symlink-profile':
        (tmp_path / 'alias').symlink_to(tmp_path, target_is_directory=True)
        out = tmp_path / 'alias/work-profile'
    else:
        (tmp_path / 'alias').symlink_to(tmp_path, target_is_directory=True)
        out = tmp_path / 'alias/work/child'
    assert validate(work, out).returncode != 0
    assert not work.exists()


def test_disjoint_new_paths_are_allowed(tmp_path):
    assert validate(tmp_path / 'work', tmp_path / 'out').returncode == 0


@pytest.mark.parametrize('case', ['nested-input', 'alias-input', 'dangling-output'])
def test_direct_materializer_rejects_unsafe_output_before_copy(tmp_path, monkeypatch, case):
    import runpy
    import shutil
    upstream = tmp_path / 'releng'; upstream.mkdir()
    (upstream / 'packages.x86_64').write_text('base\n')
    output = upstream / 'nested'
    if case == 'alias-input':
        alias = tmp_path / 'alias'; alias.symlink_to(upstream, target_is_directory=True)
        output = alias / 'nested'
    elif case == 'dangling-output':
        output = tmp_path / 'dangling'; output.symlink_to(tmp_path / 'missing')
    def forbidden_copy(*args, **kwargs):
        raise AssertionError('copy attempted before path validation')
    monkeypatch.setattr(shutil, 'copytree', forbidden_copy)
    with pytest.raises(ValueError):
        runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare'](upstream, output, ROOT, 'a' * 40)


@pytest.mark.parametrize('reserved', ['BUILD-SOURCE.json', 'BUILD-INPUTS.json'])
@pytest.mark.parametrize('kind', ['file', 'symlink', 'dangling'])
def test_releng_cannot_supply_reserved_provenance_paths(tmp_path, reserved, kind):
    import runpy
    upstream = tmp_path / 'releng'
    (upstream / 'airootfs').mkdir(parents=True)
    (upstream / 'packages.x86_64').write_text('base\n')
    target = tmp_path / 'external-sentinel'
    if kind != 'dangling':
        target.write_bytes(b'preserve external bytes')
    if kind == 'file':
        (upstream / reserved).write_bytes(b'inherited metadata')
    else:
        (upstream / reserved).symlink_to(target)
    output = tmp_path / 'output'
    with pytest.raises(ValueError, match='reserved provenance'):
        runpy.run_path(str(ROOT / 'scripts/prepare-iso.py'))['prepare'](upstream, output, ROOT, 'a' * 40)
    assert not output.exists()
    if kind == 'dangling':
        assert not target.exists()
    else:
        assert target.read_bytes() == b'preserve external bytes'
