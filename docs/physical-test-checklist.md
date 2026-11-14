# RC4 physical Live test checklist

Status: **owner testing in progress; individual results not yet reported**.
This records the owner's current test activity, not a physical PASS. RC4 already
passed 66/66 virtual checks on November 13, 2026. Do not rerun those checks merely
to fill this checklist, and do not modify the ISO during evaluation.

Use only `2026.11.13-rc4-recovery-test-only`; verify the full image identity and
SHA-256 in [Getting started](getting-started.md). Results from other candidates
are not transferable. Wilsof remains **TEST ONLY**, not production-approved.
Current decisions belong on [status #16](https://github.com/tomli0/wilsof-os/issues/16).

## Before booting

- Verify the ISO checksum and the identity of the expendable test USB privately.
  Writing or rewriting a physical USB requires explicit confirmation of that
  exact target; this checklist does not authorize an agent to write it.
- Use the UEFI Live entry. Do not change firmware security settings to force a
  pass, launch the installer, format storage or mount personal volumes writable.
- Keep the media attached for the normal Live entry. RAM boot is a separate
  selection; do not assume the normal entry copied everything into RAM.
- Do not modify an existing operating system. This is Wilsof hardware evaluation,
  not migration or replacement work.

## Checks and stop conditions

Record each item as PASS, FAIL, NOT TESTABLE IN LIVE or NOT RUN.

1. **Boot and display.** Reach the real desktop; verify the internal display,
   resolution/scaling, brightness and any essential external display. Stop on
   boot failure, persistent corruption or an unusable input/display surface.
2. **Keyboard and pointing device.** Check layout, modifier keys, trackpad,
   scrolling, window focus and the essential shortcuts from Getting started.
   Real physical key routing is not established by synthetic QMP input.
3. **Desktop and applications.** Open Wilsof Menu, search, navigate and cancel;
   check Ghostty, Firefox, Files, shortcut help and appearance settings. Do not
   install packages, enable private-file indexing or select an installation disk.
4. **Connectivity.** Check the actual Wi-Fi/wired connection, name resolution,
   reconnect and required peripherals. Keep SSIDs, passwords, MAC addresses,
   serial numbers and personal identifiers out of public reports. Virtual module
   loading is not physical device binding or connectivity.
5. **Audio and Bluetooth.** Check speaker/headphone output, microphone input and
   any required Bluetooth pairing/reconnect. Report unavailable devices honestly;
   a virtual dummy output is not physical acceptance.
6. **Power and resume.** Check battery/charging, normal shutdown and, when safe,
   manual/lid suspend and resume on AC and battery. Verify that display, input and
   connectivity recover; stop for abnormal heat or repeated failure. Record the
   actual lock behavior, not an assumed authenticated lock from an unlocked Live
   session. Installed-user password/idle locking remains a separate test where
   Live mode cannot exercise it.

## If the desktop fails

Use the separate diagnostics entry or Ctrl+Alt+F2. The local console banner
provides the current Live login; never publish its generated password or type
credentials into chat. After normal local login, the shipped read-only diagnostic
entrypoint is:

```sh
sudo /usr/local/bin/wilsof-live-recover
```

Preserve the exact error and relevant lines first. The helper's `--restart` option
is an explicit desktop-setup retry, not a disk repair or proof the first boot
passed. Do not use installation, formatting, firmware resets or unrelated-disk
changes to repair a Live boot failure.

## Minimal result report

- Exact RC4 version and verified ISO checksum.
- Hardware model and relevant non-identifying device/driver information.
- Checklist item, result, reproducible steps and whether the issue repeats.
- A sanitized photo/error excerpt if useful; exclude credentials and private data.

Leave unreported checks unmarked. Report failures before trying workarounds that
would change the test environment. The agent prioritizes those findings without
changing this accepted image or accessing the owner's physical system.

## Separate installed-system boundary

Live results do not establish installed cold boot, disk unlock, ordinary-user
password locking, persistence or installed recovery on physical hardware.
Those checks need an explicitly authorized disposable target and a separate
installation decision. No physical installation is authorized by this checklist.
