#!/usr/bin/env python3
"""Apply the Wilsof boot experience to a materialized Archiso 91 releng profile."""
from pathlib import Path
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
                   and not arg.startswith(('copytoram=', 'plymouth.enable=', 'rd.plymouth=', 'systemd.show_status=', 'loglevel='))]
        return 'options  ' + ' '.join(options) + ' ' + flags
    return re.sub(r'^options\s+(.*)$', policy_options, text, flags=re.M)


def configure_boot(output, source):
    """Configure an already prepared profile; never writes outside output."""
    output, source = Path(output), Path(source)
    entries = output / 'efiboot/loader/entries'
    # Read the real releng templates before removing duplicates. A repeat run is
    # supported without appending duplicate kernel arguments.
    normal_path = entries / '01-archiso-linux.conf'
    speech_path = entries / '02-archiso-speech-linux.conf'
    if normal_path.exists():
        normal = normal_path.read_text()
        speech = speech_path.read_text()
        memtest = (entries / '03-archiso-memtest86+x64.conf').read_text()
        cache = output / '.wilsof-boot-upstream'
        cache.mkdir(exist_ok=True)
        for name, text in [('normal.conf', normal), ('speech.conf', speech), ('memtest.conf', memtest)]:
            (cache / name).write_text(text)
    else:
        cache = output / '.wilsof-boot-upstream'
        normal, speech, memtest = [(cache / name).read_text() for name in ('normal.conf', 'speech.conf', 'memtest.conf')]
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
    config_path = root / 'etc/mkinitcpio.conf.d/archiso.conf'
    config = config_path.read_text()
    match = re.search(r'^HOOKS=\(([^)]*)\)', config, re.M)
    if match is None:
        raise ValueError('Expected Archiso releng HOOKS array')
    hooks = match[1].split()
    if not {'udev', 'kms', 'archiso', 'keyboard'} <= set(hooks):
        raise ValueError('Expected Archiso releng udev/kms/archiso/keyboard hooks')
    hooks = [hook for hook in hooks if hook not in {'plymouth', 'keyboard'}]
    hooks[hooks.index('kms') + 1:hooks.index('kms') + 1] = ['keyboard', 'plymouth']
    config_path.write_text(config[:match.start()] + 'HOOKS=(' + ' '.join(hooks) + ')' + config[match.end():])
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
