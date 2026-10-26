# Consolidated physical-only test checklist

Tracking: [status #16](https://github.com/tomli0/wilsof-os/issues/16),
[startup bug #28](https://github.com/tomli0/wilsof-os/issues/28),
[integration PR #27](https://github.com/tomli0/wilsof-os/pull/27).
Use the exact candidate/checksum identified in the current QA checkpoint. A build
or a successful VM test alone is not approval to install on physical hardware.

## One non-destructive live-USB boot

1. Verify downloaded SHA-256 and the expendable USB's actual byte capacity before
   writing it with a verified image writer. The agent does not write physical USBs.
2. Select **Try Wilsof OS** in the firmware's UEFI boot menu. Keep the USB attached;
   the default does not copy the rootfs to RAM and never starts installation.
3. Observe the actual WS splash/activity/stage. Esc switches to boot details;
   diagnostics is a separate no-splash menu entry. Record the exact failing text,
   not an approximate service name, if startup fails.
4. If the desktop fails, use Ctrl+Alt+F2. The local banner gives username `live`
   and a new password for this boot; input is hidden. Do not retry empty-root login.
   Run `sudo wilsof-live-recover` to view the relevant journals. A photo of the
   final error lines is sufficient; exclude the generated credential banner.
   `sudo wilsof-live-recover --restart` retries setup explicitly. Return to graphics
   with Ctrl+Alt+F1. If even this console is unavailable, photograph the last boot
   screen and stop; do not install or modify the internal disk as boot repair.
5. In a working desktop, check wallpaper/bar, launcher opening/navigation/Escape,
   Firefox, Files/Text Editor text and widgets, shortcut help and settings. Open
   Install Wilsof only far enough to see its explicit target prompt, then cancel.
   Do not select/erase an internal disk.
6. Check actual keyboard/modifiers, touchpad, scaling/GPU outputs, Wi-Fi/Ethernet,
   DNS and sound output/input. Record exact Mac model and device IDs where practical.
   VM audio enumeration or software rendering does not establish hardware support.
7. Shut down normally and record whether it completes. One concise report should
   include ISO/checksum, hardware model, the failed checklist step and sanitized
   error evidence. Do not send network passwords or personal identifiers.

The live evaluation session is deliberately unlocked. It is not an acceptable
substitute for testing installed-user password locking. No physical installation
is authorized by this checklist. Unsupported Secure Boot is not silently disabled.

## Installed-system checks — separate approval and expendable target required

Ordinary user login, actual password lock/unlock, idle lock, logout/reboot
persistence, networking/audio, suspend/resume, update behavior and per-file recovery
must be checked on an explicitly approved dedicated physical test disk. Full-disk
formatting is not reversible; configuration-file backup is not full-system rollback.

## Existing issue-specific owner evidence

- #3: original reference-VM graphical persistence after authenticated login/reboot.
- #4: real physical modifier/key routing; synthetic QMP input is not this test.
- #5: power-menu navigation and cancellation; no power action on an owner session.
- #6: idle-lock and actual password unlock; suspend is a separate observation.
- #7: research is already integrated, but universal search/indexing is not shipped
  or approved; do not treat this as a request to index private files.
- #10: standalone unlocked screensaver preview is excluded from this ISO. Its
  visual/pointer acceptance belongs to PR #20, not the live startup fix.
- #17: physical power-profile availability and real battery/thermal behavior.
- #18: physical lock-logo appearance on an installed ordinary account.

Keep implementation/review blockers on their issues. Only genuinely physical or
owner-session checks belong here. Do not mark a feature Done from this checklist
until its full acceptance and review/integration gates have independently passed.
