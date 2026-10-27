#!/usr/bin/env python3
"""Apply only Wilsof-owned user files, offline and without a running user bus.

Run as the desktop user. Personal DMS settings and its generated base are retained.
Backups are per-file recovery material, not a transactional rollback mechanism.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def install_user(source, home, *, live=False):
    source, home = Path(source).resolve(), Path(home).resolve()
    backup = home / '.local/state/wilsof-os/backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')

    def confined(relative, *, allow_leaf_link=False):
        current = home
        parts = Path(relative).parts
        if Path(relative).is_absolute() or '..' in parts:
            raise RuntimeError('Managed paths must remain within the user home')
        for index, part in enumerate(parts):
            current /= part
            if current.is_symlink() and not (allow_leaf_link and index == len(parts) - 1):
                raise RuntimeError(f'Refusing managed symlink: {relative}')
        return current

    live = live or confined('.local/state/wilsof-os/live-session').is_file()

    def write(relative, data, mode=0o644):
        path = confined(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            raise RuntimeError(f'Refusing managed symlink: {relative}')
        if path.exists() and path.read_bytes() == data:
            return
        if path.exists():
            saved = confined(str((backup / relative).relative_to(home)))
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, saved)
        fd, temporary = tempfile.mkstemp(prefix='.wilsof-', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(data)
            os.chmod(temporary, mode)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    for name in ('wilsof-search', 'wilsof-lock', 'wilsof-help', 'wilsof-help-view', 'wilsof-doctor', 'wilsof-vm-test-binds', 'wilsof-apply-wallpaper'):
        write(f'.local/bin/{name}', (source / 'bin' / name).read_bytes(), 0o755)
    for name in ('wilsof.lua', 'wilsof.conf', 'hypridle.conf', 'hyprlock.conf'):
        write(f'.config/hypr/{name}', (source / 'config/hypr' / name).read_bytes())
    for name in ('wilsof-session.target', 'wilsof-wallpaper.service'):
        write(f'.config/systemd/user/{name}', (source / 'config/systemd' / name).read_bytes())
    write('.config/systemd/user/dms.service.d/wilsof.conf', (source / 'config/systemd/dms-wilsof.conf').read_bytes())
    for name, origin in (
        ('wilsof-theme.json', 'config/dms/wilsof-theme.json'),
        ('wilsof-shortcuts.json', 'config/wilsof-shortcuts.json'),
        ('vm-test/wilsof-vm-test.lua', 'config/hypr/wilsof-vm-test.lua'),
    ):
        write(f'.local/share/wilsof-os/{name}', (source / origin).read_bytes())
    for name in ('Mørk geometrisk bakgrunn med isblått WS-monogram.png', 'Wilsof OS-logo med geometrisk WS-monogram.png', 'Wilsof lock background.png'):
        write(f'.local/share/wilsof-os/assets/{name}', (source / 'assets' / name).read_bytes())

    settings_relative = '.config/DankMaterialShell/settings.json'
    legacy_settings_dir = confined('.config/DankMaterialShell', allow_leaf_link=True)
    # Dux 2 migrates this directory to the literal sibling "dms". Select its
    # canonical path rather than following arbitrary links or relaxing confinement.
    if legacy_settings_dir.is_symlink() and os.readlink(legacy_settings_dir) == 'dms':
        settings_relative = '.config/dms/settings.json'
    settings = confined(settings_relative)
    if live or not settings.exists():
        data = json.loads(settings.read_text() if settings.exists() else (source / 'config/dms/settings-template.json').read_text())
        if data.get('customThemeFile') in (None, '', '__WILSOF_THEME_PATH__'):
            data['customThemeFile'] = str(home / '.local/share/wilsof-os/wilsof-theme.json')
        data['customPowerActionLock'] = str(home / '.local/bin/wilsof-lock')
        if live:
            data.update(loginctlLockIntegration=False, lockBeforeSuspend=False, lockAtStartup=False,
                        acLockTimeout=0, batteryLockTimeout=0)
        write(settings_relative, (json.dumps(data) + '\n').encode())
    entry = confined('.config/hypr/hyprland.lua')
    if not entry.exists():
        subprocess.run(['dms', 'setup', 'headless', '--compositor', 'hyprland', '--skip-existing'],
                       env=os.environ | {'HOME': str(home)}, check=True)
    if not entry.is_file() or entry.is_symlink():
        raise RuntimeError('DMS did not generate a regular hyprland.lua')
    content = entry.read_text()
    if 'require("wilsof")' not in content:
        content += '\n-- WILSOF_MANAGED\nrequire("wilsof")\n'
    write('.config/hypr/hyprland.lua', content.encode())

    # User unit links are created offline; never contact a different user's bus.
    units = [('dms.service', 'graphical-session.target'),
             ('wilsof-wallpaper.service', 'wilsof-session.target')]
    if not live:
        units.append(('hypridle.service', 'graphical-session.target'))
    else:
        write('.local/state/wilsof-os/live-session', b'Ephemeral unlocked evaluation session\n')
        idle = confined('.config/systemd/user/graphical-session.target.wants/hypridle.service', allow_leaf_link=True)
        if idle.is_symlink():
            idle.unlink()
    for unit, target in units:
        folder = confined(f'.config/systemd/user/{target}.wants')
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / unit
        origin = f'/usr/lib/systemd/user/{unit}' if unit != 'wilsof-wallpaper.service' else '../wilsof-wallpaper.service'
        if dest.is_symlink() and os.readlink(dest) != origin:
            raise RuntimeError(f'Unexpected managed unit link: {dest}')
        if not dest.exists() and not dest.is_symlink():
            dest.symlink_to(origin)
    if live:
        # A password-locked evaluation account cannot unlock PAM. Never claim it is locked.
        write('.local/bin/wilsof-lock', b'#!/bin/sh\nprintf "%s\\n" "Live evaluation is unlocked. Shut down when finished; do not enter private data."\n', 0o755)
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error('run as the desktop user, never root')
    install_user(args.source, Path.home(), live=args.live)
    print('Wilsof-managed files applied; personal DMS settings preserved. Log out/in to activate changes.')


if __name__ == '__main__':
    main()
