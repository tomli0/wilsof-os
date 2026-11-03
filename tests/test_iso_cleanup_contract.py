"""The namespace owner, not mkarchiso, owns mounted work cleanup."""
import json
from pathlib import Path
import subprocess
from build_fixture import layout


def test_build_retains_namespace_owned_work(tmp_path):
    source, _, _, env = layout(tmp_path)
    result = subprocess.run(['sh', str(source / 'scripts/build-iso.sh'), '--build'],
                            env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    # -r recursively removes airootfs before xorriso and fails on a self-bind.
    # Retain work; the private namespace must exit before any later cleanup.
    work, out = env['WILSOF_ISO_WORKDIR'], env['WILSOF_ISO_OUTDIR']
    assert json.loads(Path(env['CAPTURE']).read_text()) == [
        '-v', '-w', work, '-o', out, work + '-profile'
    ]
    assert Path(work + '-profile').is_dir()
