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
