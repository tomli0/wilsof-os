"""Substituted wrapper builds must not depend on the host's free capacity."""
from pathlib import Path
import subprocess

from build_fixture import layout


def test_wrapper_fixture_substitutes_only_its_storage_query(tmp_path):
    source, _, _, env = layout(tmp_path)
    hooks = tmp_path / 'startup-hooks'
    hooks.mkdir()
    (hooks / 'sitecustomize.py').write_text(
        'import os\n'
        'def forbidden(path):\n'
        '    raise AssertionError("HOST-STORAGE-QUERY escaped fixture")\n'
        'os.statvfs = forbidden\n'
    )
    env['PYTHONPATH'] = str(hooks)
    result = subprocess.run(
        ['sh', str(source / 'scripts/build-iso.sh'), '--build'],
        env=env, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert Path(env['CAPTURE']).is_file()
