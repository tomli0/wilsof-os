#!/usr/bin/env python3
"""Apply Wilsof boot policy to the explicitly supported Archiso 91/92 contracts."""
from pathlib import Path
import json
import re
import shutil


def _entry(template, title, order, flags):
    """Retain upstream paths/substitution tokens; change only presentation/options."""
    text = re.sub(r'^title\s+.*$', 'title    ' + title, template, flags=re.M)
    text = re.sub(r'^sort-key\s+.*$', 'sort-key ' + order, text, flags=re.M)
    # Retain boot-device discovery and substitution tokens, but remove inherited
    # presentation/RAM policy so each entry has exactly one explicit choice.
    def policy_options(match):
        options = [arg for arg in match[1].split() if arg not in {'quiet', 'splash'}
                   and not arg.startswith(('cow_spacesize=', 'copytoram=', 'plymouth.enable=', 'rd.plymouth=', 'systemd.show_status=', 'loglevel='))]
        # tmpfs size is a ceiling, not an allocation. Scale to RAM rather
        # than reserving a fixed buffer; the installer checks actual headroom.
        return 'options  ' + ' '.join(options) + ' cow_spacesize=75% ' + flags
    return re.sub(r'^options\s+(.*)$', policy_options, text, flags=re.M)


def configure_boot(output, source):
    """Configure an already prepared profile; never writes outside output."""
    output, source = Path(output), Path(source)
    entries = output / 'efiboot/loader/entries'
    # Read the real releng templates before removing duplicates. A repeat run is
    # supported without appending duplicate kernel arguments.
    normal_path = entries / '01-archiso-linux.conf'
    speech_path = entries / '02-archiso-speech-linux.conf'
    cache = output / '.wilsof-boot-upstream'
    if normal_path.exists():
        normal = normal_path.read_text()
        speech = speech_path.read_text()
        memtest = (entries / '03-archiso-memtest86+x64.conf').read_text()
    else:
        normal, speech, memtest = [(cache / name).read_text() for name in ('normal.conf', 'speech.conf', 'memtest.conf')]
    # Validate before changing entries or creating provenance/cache files.
    config_path = output / 'airootfs/etc/mkinitcpio.conf.d/archiso.conf'
    config = config_path.read_text()
    matches = list(re.finditer(r'^HOOKS=\(([^)]*)\)', config, re.M))
    if len(matches) != 1:
        raise ValueError('Expected one Archiso releng HOOKS array')
    match = matches[0]
    hooks = match[1].split()
    if (not {'udev', 'modconf', 'archiso', 'keyboard'} <= set(hooks)
            or len(hooks) != len(set(hooks))
            or not hooks.index('udev') < hooks.index('modconf') < hooks.index('archiso')
            or ('kms' in hooks and not hooks.index('modconf') < hooks.index('kms') < hooks.index('archiso'))):
        raise ValueError('Unexpected Archiso releng hook layout')
    efi = re.findall(r'^efi\s+(\S+)\s*$', memtest, re.M)
    versions = {'/boot/memtest86+/memtest.efi': 91, '/boot/memtest86+/memtest86x64.efi': 92}
    if len(efi) != 1 or efi[0] not in versions:
        raise ValueError('Unsupported Archiso x64 memtest path')
    major = versions[efi[0]]
    # v92 dropped early KMS; Wilsof deliberately retains it for Plymouth.
    if 'kms' not in hooks:
        if major != 92:
            raise ValueError('Archiso 91 releng requires kms')
        hooks.insert(hooks.index('modconf') + 1, 'kms')
    hooks = [hook for hook in hooks if hook not in {'plymouth', 'keyboard'}]
    hooks[hooks.index('kms') + 1:hooks.index('kms') + 1] = ['keyboard', 'plymouth']
    contract = output / 'BOOT-CONTRACT.json'
    if contract.is_symlink():
        raise ValueError('Refusing boot contract symlink')
    if cache.is_symlink() or any(p.is_symlink() for p in cache.glob('*')):
        raise ValueError('Refusing boot cache symlink')
    cache.mkdir(exist_ok=True)
    for name, text in [('normal.conf', normal), ('speech.conf', speech), ('memtest.conf', memtest)]:
        (cache / name).write_text(text)
    contract.write_text(json.dumps({'archiso_major': major, 'early_kms': 'wilsof-explicit'}, sort_keys=True) + '\n')
    config_path.write_text(config[:match.start()] + 'HOOKS=(' + ' '.join(hooks) + ')' + config[match.end():])
    for path in entries.glob('*.conf'):
        path.unlink()
    modes = [
        ('01-wilsof-linux.conf', normal, 'Try Wilsof OS (%ARCH%, UEFI)', '01', 'copytoram=n quiet splash'),
        ('02-wilsof-speech.conf', speech, 'Try Wilsof OS with speech (%ARCH%, UEFI)', '02', 'copytoram=n plymouth.enable=0 rd.plymouth=0 systemd.show_status=1'),
        ('03-wilsof-diagnostics.conf', normal, 'Wilsof OS diagnostics - boot logs, no splash', '03', 'copytoram=n plymouth.enable=0 rd.plymouth=0 systemd.show_status=1 loglevel=7 wilsof.diagnostics=1'),
        ('04-wilsof-ram.conf', normal, 'Try Wilsof OS - copy rootfs to RAM (extra RAM = rootfs size)', '04', 'copytoram=y plymouth.enable=0 rd.plymouth=0 systemd.show_status=1'),
    ]
    for name, template, title, order, flags in modes:
        (entries / name).write_text(_entry(template, title, order, flags))
    (entries / '05-wilsof-memtest.conf').write_text(re.sub(r'^sort-key\s+.*$', 'sort-key 05', memtest, flags=re.M))
    (output / 'efiboot/loader/loader.conf').write_text('timeout 10\ndefault 01-wilsof-linux.conf\nbeep on\n')
    root = output / 'airootfs'
    theme = root / 'usr/share/plymouth/themes/wilsof'
    shutil.copytree(source / 'iso/boot/plymouth', theme, dirs_exist_ok=True)
    shutil.copy2(source / 'assets/Wilsof OS-logo med geometrisk WS-monogram.png', theme / 'logo.png')
    daemon = root / 'etc/plymouth/plymouthd.conf'
    daemon.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / 'iso/boot/plymouthd.conf', daemon)
    packages_path = output / 'packages.x86_64'
    packages = set(packages_path.read_text().splitlines())
    packages.update({'plymouth', 'pv'})
    packages_path.write_text('\n'.join(sorted(packages)) + '\n')
