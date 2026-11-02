#!/bin/sh
# Build only inside a dedicated Arch environment; never attach or install the ISO.
set -eu
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
if [ "${1:-}" != "--build" ] || [ "$#" -ne 1 ]; then
    printf '%s\n' "Usage: $0 --build" >&2
    exit 64
fi
[ "$(id -u)" -eq 0 ] || { printf '%s\n' 'build-iso: root inside an isolated Arch build environment is required.' >&2; exit 77; }
command -v mkarchiso >/dev/null 2>&1 || { printf '%s\n' 'build-iso: archiso is unavailable.' >&2; exit 69; }
: "${WILSOF_SOURCE_COMMIT:?Exact reviewed source commit required}"
: "${WILSOF_ISO_WORKDIR:?Dedicated absolute work directory required}"
: "${WILSOF_ISO_OUTDIR:?Dedicated absolute output directory required}"
: "${WILSOF_HYPRIDLE_PACKAGE:?Exact verified internal Hypridle artifact required}"
if [ ! -f "$root/SOURCE_COMMIT" ] || [ "$(cat "$root/SOURCE_COMMIT")" != "$WILSOF_SOURCE_COMMIT" ]; then
    printf '%s\n' 'Build from a verified git archive with its exact SOURCE_COMMIT marker.' >&2
    exit 65
fi
python3 - "$WILSOF_SOURCE_COMMIT" "$WILSOF_ISO_WORKDIR" "$WILSOF_ISO_OUTDIR" <<'PY'
from pathlib import Path
import re, sys
commit, work, out = sys.argv[1:]
if not re.fullmatch(r'[0-9a-f]{40}', commit):
    raise SystemExit('Exact 40-character source commit required')
w, o = Path(work), Path(out)
if not w.is_absolute() or not o.is_absolute() or len(w.parts) < 3 or len(o.parts) < 3:
    raise SystemExit('Dedicated absolute build paths required')
w, o = w.resolve(), o.resolve()
# Use the same lexical profile name that prepare-iso receives, then resolve it;
# resolving work first would derive a different sibling through a symlink alias.
profile = Path(str(Path(work)) + '-profile').resolve()
paths = (w, profile, o)
if any(a == b or a in b.parents or b in a.parents
       for i, a in enumerate(paths) for b in paths[i + 1:]):
    raise SystemExit('Work/profile/output paths must be pairwise disjoint')
if w.exists() or profile.exists():
    raise SystemExit('Work and profile must be new')
if o.exists() and any(o.iterdir()):
    raise SystemExit('Output must be empty')
PY
mkdir -p "$WILSOF_ISO_OUTDIR"
python3 "$root/scripts/prepare-iso.py" --upstream /usr/share/archiso/configs/releng \
    --output "${WILSOF_ISO_WORKDIR}-profile" --source "$root" --commit "$WILSOF_SOURCE_COMMIT" \
    --hypridle-package "$WILSOF_HYPRIDLE_PACKAGE"
python3 - "$root" "${WILSOF_ISO_WORKDIR}-profile" <<'PY'
from pathlib import Path
from runpy import run_path
import sys
source, profile = map(Path, sys.argv[1:])
run_path(str(source / 'scripts/boot-profile.py'))['configure_boot'](profile, source)
PY
# Package-cache preflight: a corrupted mirror/download window leaves broken
# package files that only surface deep inside mkarchiso as mass
# "invalid or corrupted package (PGP signature)" failures (with noisy
# GPGME ioctl prompts on non-tty stdin). Download and signature-verify the
# full manifest up front and integrity-test every cached file, so a bad
# download fails fast before the expensive build. Signature checking stays
# fully enabled; nothing is force-installed.
python3 - "${WILSOF_ISO_WORKDIR}-profile" <<'PY'
import subprocess, sys
from pathlib import Path

profile = Path(sys.argv[1])
packages = [line.strip() for line in (profile / 'packages.x86_64').read_text().splitlines()
            if line.strip() and not line.strip().startswith('#')]
print(f'build-iso: cache preflight for {len(packages)} manifest packages', flush=True)
if subprocess.run(['pacman', '-Sw', '--needed', '--noconfirm', '--noprogressbar', *packages]).returncode != 0:
    raise SystemExit('build-iso: package download/preflight verification failed; inspect the mirror and retry')
cache = Path('/var/cache/pacman/pkg')
import gzip
bad = []
# Only test files still present; -Sw already PGP-verified them, zstd catches truncation.
for f in sorted(cache.glob('*.pkg.tar.zst')):
    if subprocess.run(['zstd', '-t', str(f)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        bad.append(f.name)
if bad:
    print('build-iso: corrupt cached packages: ' + ', '.join(bad[:20]), file=sys.stderr)
    raise SystemExit('build-iso: corrupt package cache; clear the cache and retry')
print('build-iso: cache preflight passed', flush=True)
PY
# Work may contain namespace-owned bind mounts for nested pacman CheckSpace.
# Do not let mkarchiso recursively delete it before the namespace exits.
# Retain work/profile as evidence; later cleanup needs a separate mount check.
exec mkarchiso -v -w "$WILSOF_ISO_WORKDIR" -o "$WILSOF_ISO_OUTDIR" "${WILSOF_ISO_WORKDIR}-profile"
