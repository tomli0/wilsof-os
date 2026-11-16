#!/usr/bin/env python3
"""Link the real portal objects into a bounded native ownership regression."""
from pathlib import Path
import shlex
import subprocess
import sys

build = Path(sys.argv[1]).resolve(strict=True)
source = Path(sys.argv[2]).resolve(strict=True)
here = Path(__file__).resolve().parent
objects = sorted((build / 'CMakeFiles/xdg-desktop-portal-hyprland.dir').rglob('*.o'))
objects = [str(p) for p in objects if p.name != 'main.cpp.o']
if not objects:
    raise SystemExit('Build the complete native portal before the regression')
deps = ['sdbus-c++', 'wayland-client', 'libpipewire-0.3', 'libdrm', 'uuid', 'gbm', 'hyprlang', 'hyprutils']
def flags(option):
    return shlex.split(subprocess.check_output(['pkg-config', option, *deps], text=True))
executable = build / 'wilsof-teardown-regression'
subprocess.run(['c++', '-std=c++23', '-g', '-I'+str(source), '-I'+str(source/'protocols'), *flags('--cflags'), str(here/'teardown.cpp'), *objects, *flags('--libs'), '-o', str(executable)], check=True, timeout=90)
for _ in range(20):
    subprocess.run([str(executable)], check=True, timeout=10)
print('20 native Wayland ownership teardown iterations passed')
