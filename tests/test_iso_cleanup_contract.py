"""The namespace owner, not mkarchiso, owns mounted work cleanup."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_retains_namespace_owned_work(tmp_path):
    source = tmp_path / 'source'
    scripts = source / 'scripts'
    scripts.mkdir(parents=True)
    shutil.copyfile(ROOT / 'scripts/build-iso.sh', scripts / 'build-iso.sh')
    (source / 'SOURCE_COMMIT').write_text('a' * 40 + '\n')
    (scripts / 'prepare-iso.py').write_text(
        'import pathlib, sys\n'
        'pathlib.Path(sys.argv[sys.argv.index("--output") + 1]).mkdir()\n'
    )
    (scripts / 'boot-profile.py').write_text(
        'def configure_boot(profile, source):\n    pass\n'
    )
    tools = tmp_path / 'tools'
    tools.mkdir()
    (tools / 'python3').symlink_to(sys.executable)
    for name, text in {
        'id': '#!/bin/sh\nprintf "0\\n"\n',
        'mkarchiso': '#!' + sys.executable + '\n'
        'import json, os, pathlib, sys\n'
        'pathlib.Path(os.environ["CAPTURE"]).write_text(json.dumps(sys.argv[1:]))\n',
    }.items():
        (tools / name).write_text(text)
        (tools / name).chmod(0o755)
    capture = tmp_path / 'arguments.json'
    work, out = tmp_path / 'work', tmp_path / 'out'
    env = os.environ | {
        'PATH': str(tools) + os.pathsep + os.environ['PATH'],
        'WILSOF_SOURCE_COMMIT': 'a' * 40,
        'WILSOF_ISO_WORKDIR': str(work),
        'WILSOF_ISO_OUTDIR': str(out),
        'WILSOF_HYPRIDLE_PACKAGE': str(tmp_path / 'verified-package'),
        'CAPTURE': str(capture),
    }
    result = subprocess.run(['sh', str(scripts / 'build-iso.sh'), '--build'],
                            env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    # -r recursively removes airootfs before xorriso and fails on a self-bind.
    # Retain work; the private namespace must exit before any later cleanup.
    assert json.loads(capture.read_text()) == [
        '-v', '-w', str(work), '-o', str(out), str(work) + '-profile'
    ]
    assert Path(str(work) + '-profile').is_dir()
