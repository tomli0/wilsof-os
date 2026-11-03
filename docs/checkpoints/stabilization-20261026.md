# Stabilization checkpoint — released copy-to-RAM failure

## Confirmed reproduction

Released ISO source `21214fc4c0674775918cb5b36099616ef1bcedb5`:
`wilsof-internal-2026.10.26-x86_64.iso`, SHA-256
`82a26c119b51446123b44116689319bb5e1f5dfddedafe56a30b695a874b12d9`.
The cached squashfs was compared byte-for-byte by digest to its exact ISO extent
by an independent subscription reviewer, and the actual initramfs hook inspected.

Dedicated QEMU/OVMF USB-storage emulation, TCG, no physical/installed disk:

- 3072 and 4608 MiB: boot-media mount retained; live-setup and greetd start.
- 6144 MiB with restricted user networking: Archiso automatically copies rootfs
  to RAM, unmounts/removes `/run/archiso/bootmnt`; immutable squashfs remains
  mounted at `/run/archiso/airootfs`. `provision-target` raises its live-environment
  ValueError, `wilsof-live-setup.service` fails, greetd cannot start.
- Diagnostic one-line guard replacement in the running failed guest lets
  live-setup and greetd become active. This is not a final-ISO acceptance test.

This reproduces the reported symptom chain without a GPU failure. Exact physical
Mac logs/model remain unavailable, so the Mac's individual cause is not proven.
Original root has a locked password; rejection of empty-root console login is
intentional. The released live account also has no usable console password.

## Changes under review

- Both provisioning and installer now check the persistent live-root mount,
  retaining live-only restrictions in copy-to-RAM mode.
- Installer rechecks destination emptiness/symlink/mount state after the lengthy
  final disk scan, immediately before formatting; no existing disk guard removed.
- Independent live-console service generates a per-boot `live` password and
  displays it locally in `/etc/issue`; explicit tty2 login remains available if
  desktop preparation fails. Root stays locked; no network service or broad sudo.
- Narrow live-only helper exposes relevant journals and bounded desktop retry.
  Only exact helper arguments are authorized; no arbitrary shell commands.
- Recovery scripts/credentials/settings are not copied into the installed target.

## Tests and review

67 focused tests pass after observed RED/GREEN failures for RAM-mode guards,
console preparation/materialization and late destination mutation. Baseline
independent startup and installer/security reviews completed through verified
`openai-codex` / `gpt-6.1-sol` / `subscription_included`. New recovery and installer
changes are undergoing focused independent review; no final approval is implied.

No new ISO built at this checkpoint. Default GTK rendering, normal Hyprlock
password unlock, final-image boot/install/update checks and physical compatibility
remain outstanding. Boot branding/splash implementation is a parallel bounded
subtask. Scheduler and existing worker remain paused; approval/budget/retry rules
unchanged. No merge, release, issue closure or Done transition.
