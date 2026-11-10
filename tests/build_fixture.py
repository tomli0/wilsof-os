"""Scratch-only wrapper harness: materializer/package tools/mkarchiso substituted."""
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def layout(tmp_path):
    source, upstream, tools = [tmp_path / name for name in ('source', 'releng', 'tools')]
    (source / 'scripts').mkdir(parents=True)
    (source / 'runtime').mkdir()
    upstream.mkdir()
    tools.mkdir()
    (source / 'SOURCE_COMMIT').write_text('a' * 40 + '\n')
    shutil.copy2(ROOT / 'scripts/build-iso.sh', source / 'scripts/build-iso.sh')
    (source / 'runtime/pinned-package.py').write_text('def verified_package(directory):\n    return directory / "internal.pkg.tar.zst"\n')
    (source / 'scripts/prepare-iso.py').write_text('import pathlib,sys\np=pathlib.Path(sys.argv[sys.argv.index("--output")+1]); p.mkdir()\n(p/"packages.x86_64").write_text("base\\n")\n')
    (source / 'scripts/boot-profile.py').write_text('def configure_boot(profile,source):\n    pass\n')
    (source / 'scripts/build-inputs.py').write_text('import pathlib,sys\n(pathlib.Path(sys.argv[1])/"BUILD-INPUTS.json").write_text("{}\\n")\n')
    for name in ('packages.x86_64', 'pacman.conf', 'profiledef.sh'):
        (upstream / name).write_text('fixture\n')
    package = tmp_path / 'internal.pkg.tar.zst'
    package.write_bytes(b'fixture; not an actual verified Hypridle artifact')
    portal = tmp_path / 'portal.pkg.tar.zst'
    portal.write_bytes(b'synthetic portal archive; not signature acceptance')
    Path(str(portal)+'.sig').write_bytes(b'synthetic detached signature')
    (source / 'runtime/portal-package.py').write_text('def artifact(path):\n    if not path.is_file() or not path.with_name(path.name+".sig").is_file(): raise ValueError("missing portal input")\n    return {"package":str(path)}\n')
    for name, text in {
        'id': '#!/bin/sh\nprintf "0\\n"\n',
        'pacman': '#!/bin/sh\nexit 0\n',
        'zstd': '#!/bin/sh\nexit 0\n',
        'sudo': '#!/bin/sh\nexec env "$@"\n',
        'mkarchiso': '#!' + sys.executable + '\nimport json,os,pathlib,sys\npathlib.Path(os.environ["CAPTURE"]).write_text(json.dumps(sys.argv[1:]))\n',
    }.items():
        path = tools / name
        path.write_text(text)
        path.chmod(0o755)
    env = {
        'PATH': str(tools) + ':' + os.environ['PATH'], 'HOME': str(tmp_path),
        'WILSOF_SOURCE_COMMIT': 'a' * 40, 'SOURCE_DATE_EPOCH': '1767225600',
        'WILSOF_ISO_VERSION': 'fixture', 'WILSOF_ARCHISO_RELENG': str(upstream),
        'WILSOF_ISO_WORKDIR': str(tmp_path / 'work'), 'WILSOF_ISO_OUTDIR': str(tmp_path / 'out'),
        'WILSOF_HYPRIDLE_PACKAGE': str(package), 'WILSOF_PORTAL_PACKAGE': str(portal), 'CAPTURE': str(tmp_path / 'mkarchiso.json'),
    }
    return source, upstream, package, env
