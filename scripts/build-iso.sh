#!/bin/sh
# Build an internal live-test ISO only when explicitly requested.
set -eu

root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
overlay="$root/iso"
work=${WILSOF_ISO_WORKDIR:-"$root/.iso-work"}
out=${WILSOF_ISO_OUTDIR:-"$root/.iso-out"}
profile="$work/profile"

if [ "${1:-}" != "--build" ] || [ "$#" -ne 1 ]; then
    printf '%s\n' "Usage: $0 --build" >&2
    printf '%s\n' "Requires Arch Linux, archiso, root, network package access and free build space. No ISO is published or installed." >&2
    exit 64
fi
[ "$(id -u)" -eq 0 ] || { printf '%s\n' "build-iso: run as root on a disposable Arch build host." >&2; exit 77; }
command -v mkarchiso >/dev/null 2>&1 || { printf '%s\n' "build-iso: mkarchiso is unavailable; install archiso on a dedicated build host." >&2; exit 69; }
[ -d /usr/share/archiso/configs/releng ] || { printf '%s\n' "build-iso: the upstream archiso releng profile is unavailable." >&2; exit 69; }
[ -f "$overlay/profiledef.sh" ] || { printf '%s\n' "build-iso: tracked Wilsof overlay is incomplete." >&2; exit 65; }

rm -rf "$profile"
mkdir -p "$work" "$out"
cp -a /usr/share/archiso/configs/releng "$profile"
cp -a "$overlay/." "$profile/"
exec mkarchiso -v -r -w "$work" -o "$out" "$profile"
