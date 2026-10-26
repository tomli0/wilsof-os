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
profile = Path(str(w) + '-profile')
if w == o or w in o.parents or o in w.parents or w.exists() or profile.exists():
    raise SystemExit('Work must be new; work/output paths must be disjoint')
if o.exists() and any(o.iterdir()):
    raise SystemExit('Output must be empty')
PY
mkdir -p "$WILSOF_ISO_OUTDIR"
python3 "$root/scripts/prepare-iso.py" --upstream /usr/share/archiso/configs/releng \
    --output "${WILSOF_ISO_WORKDIR}-profile" --source "$root" --commit "$WILSOF_SOURCE_COMMIT"
exec mkarchiso -v -r -w "$WILSOF_ISO_WORKDIR" -o "$WILSOF_ISO_OUTDIR" "${WILSOF_ISO_WORKDIR}-profile"
