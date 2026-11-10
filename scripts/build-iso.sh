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
: "${WILSOF_PORTAL_PACKAGE:?Exact portal backport archive and trusted detached signature required}"
: "${SOURCE_DATE_EPOCH:?Fixed source/build epoch required}"
: "${WILSOF_ISO_VERSION:?Explicit internal image version required}"
upstream=${WILSOF_ARCHISO_RELENG:-/usr/share/archiso/configs/releng}
export SOURCE_DATE_EPOCH WILSOF_ISO_VERSION
LC_ALL=C TZ=UTC
export LC_ALL TZ
if [ ! -f "$root/SOURCE_COMMIT" ] || [ "$(cat "$root/SOURCE_COMMIT")" != "$WILSOF_SOURCE_COMMIT" ]; then
    printf '%s\n' 'Build from a verified git archive with its exact SOURCE_COMMIT marker.' >&2
    exit 65
fi
python3 - "$WILSOF_SOURCE_COMMIT" "$WILSOF_ISO_WORKDIR" "$WILSOF_ISO_OUTDIR" "$root" "$upstream" "$WILSOF_HYPRIDLE_PACKAGE" "$WILSOF_PORTAL_PACKAGE" <<'PY'
from pathlib import Path
from runpy import run_path
import os, re, sys
commit, work, out = sys.argv[1:4]
if not re.fullmatch(r'[0-9a-f]{40}', commit):
    raise SystemExit('Exact 40-character source commit required')
w, o = Path(work), Path(out)
if not w.is_absolute() or not o.is_absolute():
    raise SystemExit('Dedicated absolute build paths required')
# Derive the same lexical sibling prepare-iso receives, then canonicalize.
profile = Path(str(w) + '-profile')
for path in (w, profile, o):
    if path.is_symlink() or any((p.is_symlink() and not p.exists()) or (p.exists() and not p.is_dir()) for p in path.parents):
        raise SystemExit('Refusing build path symlink/dangling ancestor')
w, profile, o = w.resolve(), profile.resolve(), o.resolve()
paths = (w, profile, o)
if any(len(p.parts) < 3 for p in paths):
    raise SystemExit('Dedicated canonical build paths required')
def overlaps(a, b):
    return a == b or a in b.parents or b in a.parents
if any(overlaps(a, b) for i, a in enumerate(paths) for b in paths[i + 1:]):
    raise SystemExit('Work/profile/output paths must be pairwise disjoint')
if w.exists() or profile.exists():
    raise SystemExit('Work and profile must be new')
if o.exists() and (not o.is_dir() or any(o.iterdir())):
    raise SystemExit('Output must be an empty directory')
# The wrapper always supplies inputs; the shorter form supports guard-only tests.
if len(sys.argv) > 4:
    source, upstream, package = map(Path, sys.argv[4:7])
    if not all(p.is_absolute() for p in (source, upstream, package)):
        raise SystemExit('Absolute source/releng/package paths required')
    for folder, names in ((source, ('SOURCE_COMMIT', 'runtime/pinned-package.py')),
                          (upstream, ('packages.x86_64', 'pacman.conf', 'profiledef.sh'))):
        if not folder.is_dir() or any(not (folder / n).is_file() or (folder / n).is_symlink() for n in names):
            raise SystemExit('Missing required source/releng input')
    if any((upstream / n).exists() or (upstream / n).is_symlink() for n in ('BUILD-SOURCE.json', 'BUILD-INPUTS.json', 'BOOT-CONTRACT.json', '.build-inputs', '.wilsof-boot-upstream')):
        raise SystemExit('Refusing inherited reserved provenance path')
    if any(p.is_symlink() and p.is_dir() for p in upstream.rglob('*')):
        raise SystemExit('Refusing releng directory symlink')
    if not package.is_file():
        raise SystemExit('Missing internal Hypridle package')
    if any(overlaps(p, i.resolve()) for p in paths for i in (source, upstream, package)):
        raise SystemExit('Build paths must be disjoint from source/releng/package inputs')
    if any(k in os.environ for k in ('WILSOF_PRIVATE_EXPERIMENTAL', 'WILSOF_PRIVATE_HYPRLAND_CONTRACT')):
        private = run_path(str(source / 'runtime/private-hyprland.py'))
        record = private['load']()
        private_inputs = (Path(os.environ['WILSOF_PRIVATE_HYPRLAND_CONTRACT']), Path(record['package']))
        if any(overlaps(p, i.resolve()) for p in paths for i in private_inputs):
            raise SystemExit('Private Hyprland inputs must be disjoint from build outputs')
        if any(overlaps(source.resolve(), i.resolve()) for i in private_inputs):
            raise SystemExit('Private Hyprland inputs must remain outside exported public source')
    pin = run_path(str(source / 'runtime/pinned-package.py'))
    if pin['verified_package'](package.parent) != package:
        raise SystemExit('Exact verified internal Hypridle package filename required')
    if len(sys.argv) > 7:
        portal_package = Path(sys.argv[7])
        portal = run_path(str(source / 'runtime/portal-package.py'))
        record = portal['artifact'](portal_package)
        portal_inputs = (portal_package, Path(str(portal_package) + '.sig'))
        if any(overlaps(p, i.resolve()) for p in paths for i in portal_inputs) or any(overlaps(source.resolve(), i.resolve()) for i in portal_inputs):
            raise SystemExit('Portal artifacts must remain outside source and output trees')
    if not re.fullmatch(r'[0-9]{1,12}', os.environ['SOURCE_DATE_EPOCH']) or int(os.environ['SOURCE_DATE_EPOCH']) > 253402300799:
        raise SystemExit('Invalid fixed source/build epoch')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}', os.environ['WILSOF_ISO_VERSION']):
        raise SystemExit('Invalid internal image version')
PY
: "${WILSOF_ARTIFACT_CATALOG:?Pre-existing private host-wide retention catalog required}"
: "${WILSOF_WORKFLOW_ID:?Unique owner workflow identifier required}"
python3 "$root/scripts/artifact-lifecycle.py" build-begin \
    --catalog "$WILSOF_ARTIFACT_CATALOG" --workflow "$WILSOF_WORKFLOW_ID" \
    --source "$WILSOF_SOURCE_COMMIT" --work "$WILSOF_ISO_WORKDIR" --out "$WILSOF_ISO_OUTDIR"
finish_storage() {
    result=$?
    trap - 0
    python3 "$root/scripts/artifact-lifecycle.py" complete \
        --catalog "$WILSOF_ARTIFACT_CATALOG" --workflow "$WILSOF_WORKFLOW_ID" --exit-code "$result" || result=1
    python3 "$root/scripts/artifact-lifecycle.py" check --catalog "$WILSOF_ARTIFACT_CATALOG" || result=1
    exit "$result"
}
trap finish_storage 0
mkdir -p "$WILSOF_ISO_OUTDIR"
python3 "$root/scripts/prepare-iso.py" --upstream "$upstream" \
    --output "${WILSOF_ISO_WORKDIR}-profile" --source "$root" --commit "$WILSOF_SOURCE_COMMIT" \
    --hypridle-package "$WILSOF_HYPRIDLE_PACKAGE" --portal-package "$WILSOF_PORTAL_PACKAGE"
python3 - "$root" "${WILSOF_ISO_WORKDIR}-profile" <<'PY'
from pathlib import Path
from runpy import run_path
import sys
source, profile = map(Path, sys.argv[1:])
run_path(str(source / 'scripts/boot-profile.py'))['configure_boot'](profile, source)
PY
# Resolve/download against a new local DB and explicit cache, verify every
# required package/signature, then replace mirrors with the frozen local inputs.
python3 "$root/scripts/build-inputs.py" "${WILSOF_ISO_WORKDIR}-profile" "$root"
cp "${WILSOF_ISO_WORKDIR}-profile/BUILD-INPUTS.json" "$WILSOF_ISO_OUTDIR/BUILD-INPUTS.json"
# Work may contain namespace-owned bind mounts for nested pacman CheckSpace.
# Retain work/profile as evidence; later cleanup needs a separate mount check.
mkarchiso -v -w "$WILSOF_ISO_WORKDIR" -o "$WILSOF_ISO_OUTDIR" "${WILSOF_ISO_WORKDIR}-profile"
