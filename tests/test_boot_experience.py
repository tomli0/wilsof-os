"""Exercise the boot overlay against Archiso 91's loader contract."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NORMAL = '''title    Arch Linux install medium (%ARCH%, UEFI)
sort-key 01
linux    /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux
initrd   /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux.img
options  archisobasedir=%INSTALL_DIR% archisosearchuuid=%ARCHISO_UUID% %KERNEL_PARAMS%
'''
SPEECH = NORMAL.replace('sort-key 01', 'sort-key 02').replace('%KERNEL_PARAMS%', 'accessibility=on %KERNEL_PARAMS%')
HOOKS = 'base udev microcode modconf kms memdisk archiso archiso_loop_mnt archiso_pxe_common archiso_pxe_nbd archiso_pxe_http archiso_pxe_nfs block filesystems keyboard'


def configure(output):
    script = ROOT / 'scripts/boot-profile.py'
    assert script.is_file(), 'Boot profile configurator is missing'
    spec = importlib.util.spec_from_file_location('boot_profile', script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.configure_boot(output, ROOT)


def profile(tmp_path):
    output = tmp_path / 'profile'
    entries = output / 'efiboot/loader/entries'
    entries.mkdir(parents=True)
    (entries / '01-archiso-linux.conf').write_text(NORMAL)
    (entries / '02-archiso-speech-linux.conf').write_text(SPEECH)
    (entries / '03-archiso-memtest86+x64.conf').write_text('title Memtest86+\nefi /boot/memtest86+/memtest.efi\n')
    (output / 'efiboot/loader/loader.conf').write_text('timeout 15\ndefault 01-archiso-linux.conf\nbeep on\n')
    mkinit = output / 'airootfs/etc/mkinitcpio.conf.d/archiso.conf'
    mkinit.parent.mkdir(parents=True)
    mkinit.write_text(f'HOOKS=({HOOKS})\nCOMPRESSION="xz"\nCOMPRESSION_OPTIONS=(-9e)\n')
    (output / 'packages.x86_64').write_text('base\nmkinitcpio-archiso\n')
    return output


def options(entry):
    return next(line.split()[1:] for line in entry.splitlines() if line.startswith('options'))


def test_build_materializes_boot_experience_before_mkarchiso():
    build = (ROOT / 'scripts/build-iso.sh').read_text()
    assert 'scripts/boot-profile.py' in build
    assert build.index('configure_boot') < build.index('exec mkarchiso')


def test_menu_defaults_to_safe_live_boot_preserving_upstream_placeholders(tmp_path):
    output = profile(tmp_path)
    configure(output)
    entries = output / 'efiboot/loader/entries'
    default = (output / 'efiboot/loader/loader.conf').read_text()
    assert 'default 01-wilsof-linux.conf' in default
    assert 'timeout 10' in default
    assert not list(entries.glob('*archiso*')), 'Remove duplicate upstream installation entries'
    live = (entries / '01-wilsof-linux.conf').read_text()
    assert 'Try Wilsof OS' in live
    assert 'install medium' not in live
    assert 'copytoram=n' in options(live)
    assert 'quiet' in options(live) and 'splash' in options(live)
    for token in ('%INSTALL_DIR%', '%ARCH%', '%ARCHISO_UUID%', '%KERNEL_PARAMS%'):
        assert token in live
    assert 'linux    /%INSTALL_DIR%/boot/%ARCH%/vmlinuz-linux' in live
    assert 'initrd   /%INSTALL_DIR%/boot/%ARCH%/initramfs-linux.img' in live
    assert 'efi /boot/memtest86+/memtest.efi' in (entries / '05-wilsof-memtest.conf').read_text()
    speech = (entries / '02-wilsof-speech.conf').read_text()
    assert 'accessibility=on' in options(speech)
    assert 'copytoram=n' in options(speech)
    assert 'splash' not in options(speech) and 'quiet' not in options(speech)
    diagnostic = (entries / '03-wilsof-diagnostics.conf').read_text()
    for token in ('copytoram=n', 'plymouth.enable=0', 'systemd.show_status=1', 'loglevel=7'):
        assert token in options(diagnostic)
    assert not {'quiet', 'splash'} & set(options(diagnostic))
    ram = (entries / '04-wilsof-ram.conf').read_text()
    assert 'copytoram=y' in options(ram)
    assert 'extra RAM' in ram and 'rootfs' in ram
    assert 'splash' not in options(ram), 'Leave upstream pv copy progress visible'


def test_plymouth_theme_and_hook_are_materialized_without_custom_ram_copy(tmp_path):
    import hashlib
    import re
    output = profile(tmp_path)
    configure(output)
    root = output / 'airootfs'
    theme = root / 'usr/share/plymouth/themes/wilsof'
    assert (theme / 'wilsof.plymouth').is_file(), 'Supported Plymouth script theme is missing'
    descriptor = (theme / 'wilsof.plymouth').read_text()
    assert 'ModuleName=script' in descriptor
    assert 'ImageDir=/usr/share/plymouth/themes/wilsof' in descriptor
    assert 'ScriptFile=/usr/share/plymouth/themes/wilsof/wilsof.script' in descriptor
    assert 'Theme=wilsof' in (root / 'etc/plymouth/plymouthd.conf').read_text()
    original = ROOT / 'assets/Wilsof OS-logo med geometrisk WS-monogram.png'
    assert hashlib.sha256((theme / 'logo.png').read_bytes()).digest() == hashlib.sha256(original.read_bytes()).digest()
    script = (theme / 'wilsof.script').read_text()
    for symbol in ('Image("logo.png")', 'Window.GetWidth', 'Window.GetHeight', 'Plymouth.SetRefreshFunction', 'Plymouth.SetRootMountedFunction', 'Esc'):
        assert symbol in script
    assert 'SetBootProgressFunction' not in script, 'Do not invent whole-boot percentages'
    assert '%' not in script, 'Indeterminate activity, never fake percentage completion'
    assert 'Plymouth.SetKeyboardInputFunction' not in script, 'Leave native Escape-to-details handling intact'
    config = (root / 'etc/mkinitcpio.conf.d/archiso.conf').read_text()
    match = re.search(r'HOOKS=\(([^)]*)\)', config)
    assert match is not None
    hooks = match[1].split()
    assert set(HOOKS.split()) <= set(hooks)
    assert hooks.count('plymouth') == 1
    assert hooks.index('udev') < hooks.index('kms') < hooks.index('plymouth') < hooks.index('archiso')
    assert hooks.index('keyboard') < hooks.index('plymouth')
    assert 'COMPRESSION="xz"' in config
    assert 'COMPRESSION_OPTIONS=(-9e)' in config
    assert {'plymouth', 'pv'} <= set((output / 'packages.x86_64').read_text().splitlines())
    assert not (root / 'etc/initcpio/hooks').exists(), 'Use upstream emergency and pv copy hooks, not replacements'


def test_upstream_presentation_flags_cannot_override_safe_menu_policy(tmp_path):
    output = profile(tmp_path)
    entries = output / 'efiboot/loader/entries'
    for name in ('01-archiso-linux.conf', '02-archiso-speech-linux.conf'):
        path = entries / name
        path.write_text(path.read_text().replace('%KERNEL_PARAMS%', 'quiet splash copytoram=y %KERNEL_PARAMS%'))
    configure(output)
    live = options((entries / '01-wilsof-linux.conf').read_text())
    assert [arg for arg in live if arg.startswith('copytoram=')] == ['copytoram=n']
    for name in ('02-wilsof-speech.conf', '03-wilsof-diagnostics.conf', '04-wilsof-ram.conf'):
        assert not {'quiet', 'splash'} & set(options((entries / name).read_text()))
    before = {str(p.relative_to(output)): p.read_bytes() for p in output.rglob('*') if p.is_file()}
    configure(output)
    after = {str(p.relative_to(output)): p.read_bytes() for p in output.rglob('*') if p.is_file()}
    assert after == before, 'Overlay must be deterministic and idempotent'
