# Wilsof live boot experience

The internal image uses **UEFI systemd-boot only**. Its entries are generated
from the Archiso 91 releng templates, retaining `%INSTALL_DIR%`, `%ARCH%`,
`%ARCHISO_UUID%`, and `%KERNEL_PARAMS%` for mkarchiso to substitute.

- **Try Wilsof OS** is selected after 10 seconds. It starts the live desktop,
  not an installation, and explicitly uses `copytoram=n`. Keep the boot medium
  attached. Installing remains a separate, explicitly confirmed action.
- **Try Wilsof OS with speech** retains upstream `accessibility=on` and disables
  Plymouth. This is Archiso's Speakup console screen reader, **not a graphical
  desktop screen reader**. Audio hardware/output selection and console recovery
  must be checked on the target VM/hardware; it does not make Hyprland accessible.
- **Diagnostics** disables Plymouth and quiet mode, uses `loglevel=7`, and shows
  systemd status. It still avoids copying the rootfs into RAM.
- **Copy rootfs to RAM** is opt-in and leaves console output visible. The extra
  memory cost is the entire compressed rootfs image **in addition to** the RAM
  needed for the live system, its writable overlay and applications. This is not
  a recommendation for a 2 GiB VM. Insufficient RAM can cause startup failure.
- The upstream Memtest86+ EFI entry is retained for memory diagnostics.

## Splash and honest progress

The supported Plymouth `script` plugin shows the existing, unchanged Wilsof
WS-monogram/wordmark centered on black, scaled proportionally to the display.
A moving segment indicates activity, **not a percentage or a completion estimate**.
The stage changes from starting the OS to starting live services when Plymouth
receives the real root-mounted event. Boot messages/prompts can also be displayed.
No service-by-service progress or copy percentage is fabricated.

Press **Esc** to use Plymouth's native boot-details view; pressing it again toggles
back. The theme does not intercept keyboard input. If graphics/KMS is unavailable,
Plymouth may use its text/details fallback. The packaged mkinitcpio `plymouth`
hook's `run_emergencyhook` quits the splash for an initramfs emergency shell.
Live-service failures require the separately configured recovery/OnFailure path;
a theme alone cannot detect every systemd or desktop failure.

`pv` is included. In mkinitcpio-archiso 73, the upstream `archiso` install hook
includes it automatically and the runtime hook uses it for real file-copy progress
when `copytoram=y`. The RAM entry disables Plymouth so that output is visible.
This is **rootfs copy progress only**, not progress for the entire startup.
There is no custom RAM-copy hook, no transfer of `pv` percentages into Plymouth,
and no percentage at all on the normal no-copy path. Initramfs decompression and
firmware loading happen before/around splash startup and may remain blank.

## Integration and verification

After `prepare(...)`, import `scripts/boot-profile.py` with `importlib.util` and
call `configure_boot(output, source)`, where both arguments are profile/repository
paths. Call it before mkarchiso: it adds `plymouth`/`pv`, overlays the theme and
`/etc/plymouth/plymouthd.conf`, and inserts `keyboard plymouth` after `kms` while
preserving the remaining releng hooks and compression settings. Repeated calls
are deterministic; original loader templates are retained outside airootfs in
`.wilsof-boot-upstream/` for regeneration.

Run `python -m pytest tests/test_boot_experience.py -q` from the repository.
The tests use the actual Archiso 91 template format, not a custom bootloader.
They verify menu policy, substitution tokens, theme materialization, unmodified
logo bytes, hooks, dependencies, and repeatability. These are preparation tests,
not proof of a rendered splash or successful boot. A full ISO/VM smoke test must
still check Esc, audio, text fallback and recovery before release.

## Primary references inspected

- Archiso 91 installed releng: `efiboot/loader/entries/*.conf` and
  `airootfs/etc/mkinitcpio.conf.d/archiso.conf`.
- mkinitcpio-archiso 73 installed package sources: `hooks/archiso`,
  `install/archiso`, and upstream `docs/README.bootparams`:
  <https://gitlab.archlinux.org/archlinux/mkinitcpio/mkinitcpio-archiso>.
- mkinitcpio configuration and emergency hooks:
  <https://man.archlinux.org/man/mkinitcpio.conf.5.en> and
  <https://man.archlinux.org/man/mkinitcpio.8.en>.
- Plymouth scripting API and upstream parser declaration:
  <https://www.freedesktop.org/wiki/Software/Plymouth/Scripts/> and
  <https://gitlab.freedesktop.org/plymouth/plymouth/-/blob/main/src/plugins/splash/script/script-parse.h>.
- Current Arch Plymouth package's `usr/lib/initcpio/install/plymouth` and
  `usr/lib/initcpio/hooks/plymouth` (including native emergency quit), inspected
  from the package archive without installing it or touching host configuration.
