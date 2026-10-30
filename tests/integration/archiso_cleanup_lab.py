"""Opt-in disposable mount/real-xorriso regression, never a full ISO build.

Usage: python3 .../archiso_cleanup_lab.py --mkarchiso /verified/root/usr/bin/mkarchiso
       --evidence /private/new-directory
Runs one private mount/PID namespace; no host block devices or recursive cleanup.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mkarchiso', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    root.mkdir(mode=0o700, exist_ok=False)
    source = args.mkarchiso.read_bytes()
    text = source.decode()
    start = text.index('_build_iso_image() {\n')
    end = text.index('\n# Read profile', start)
    function = text[start:end]
    # Assert the exact upstream cleanup seam, but never execute recursive rm on
    # a mount. Empty-directory rmdir proves the kernel EBUSY condition safely.
    assert '_unshare rm -rf -- "${work_dir:?}/${arch}/airootfs"' in function
    (root / 'upstream-function.sh').write_text(function)
    script = r'''
set -euo pipefail
root=$1
[[ $(readlink /proc/self/ns/mnt) != "$2" ]]
[[ $(findmnt -n -o PROPAGATION /) == private ]]
work_dir="$root/work"
arch=x86_64
isofs_dir="$work_dir/iso"
out_dir="$root/out"
image_name=fixture.iso
iso_label=WILSOF_LAB
iso_application=WilsofLab
iso_publisher=WilsofLab
quiet=n
bootmodes=()
rm_work_dir=0
mkdir -p "$work_dir/$arch/airootfs" "$isofs_dir" "$out_dir"
printf 'disposable\n' > "$isofs_dir/fixture.txt"
mount --bind "$work_dir/$arch/airootfs" "$work_dir/$arch/airootfs"
# No recursive removal: rmdir only attempts the known empty mountpoint.
if rmdir "$work_dir/$arch/airootfs" 2> "$root/rmdir-error.txt"; then
    exit 1
fi
/usr/bin/grep -q 'Device or resource busy' "$root/rmdir-error.txt"
printf 'preserve\n' > "$work_dir/$arch/airootfs/sentinel"
_msg_info() { printf '%s\n' "$*"; }
_unshare() { "$@"; }
app_name=mkarchiso
source "$root/upstream-function.sh"
_build_iso_image
[[ -s "$out_dir/fixture.iso" ]]
[[ $(< "$work_dir/$arch/airootfs/sentinel") == preserve ]]
mountpoint -q "$work_dir/$arch/airootfs"
# Namespace-owned mount is released by namespace exit, not recursive cleanup.
'''
    (root / 'probe.sh').write_text(script)
    host_namespace = os.readlink('/proc/self/ns/mnt')
    command = ['sudo', '-n', 'unshare', '--mount', '--pid', '--fork',
               '--kill-child', '--propagation', 'private', '/bin/bash',
               str(root / 'probe.sh'), str(root), host_namespace]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    (root / 'probe.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    mounts = Path('/proc/self/mountinfo').read_text()
    assert str(root) not in mounts
    assert (root / 'work/x86_64/airootfs/sentinel').read_text() == 'preserve\n'
    layout = subprocess.run(['xorriso', '-indev', str(root / 'out/fixture.iso'),
                             '-ls', '/fixture.txt'], capture_output=True, text=True)
    assert layout.returncode == 0, layout.stderr
    evidence = {
        'upstream_sha256': hashlib.sha256(source).hexdigest(),
        'function_sha256': hashlib.sha256(function.encode()).hexdigest(),
        'empty_mount_rmdir_ebusy': True,
        'real_xorriso_retained_work_exit': result.returncode,
        'sentinel_preserved': True,
        'host_mount_leak': False,
        'recursive_cleanup_executed': False,
        'fixture_iso_bytes': (root / 'out/fixture.iso').stat().st_size,
        'not_installation_or_boot_acceptance': True,
    }
    (root / 'result.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
