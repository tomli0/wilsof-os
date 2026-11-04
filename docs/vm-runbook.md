# VM runbook — Arch test target

This runbook applies only to authorized, disposable Wilsof infrastructure. Do not modify the historical Fedora VM or unrelated machines.

## Safe access

1. Confirm target operating system, VM identity and installed disk through read-only checks.
2. Compare the presented ED25519 host key with the recorded fingerprint before pinning it. Keep `StrictHostKeyChecking=yes` afterwards.
3. Take a VM snapshot if the platform offers one before desktop work. Do not reinstall, format, repartition or alter virtual hardware as part of configuration testing.

## Before the first graphical login

`install-arch-test-vm.sh` configures greetd with tuigreet and Hyprland without placing a password or hash in the repository. An authorized local operator must set the user password through normal interactive administration before graphical login. Never put passwords, hashes or private keys in the repository, shell environment or chat.

## Install or upgrade the Wilsof user profile

1. Run `scripts/preflight-arch.sh` as the target user to verify DMS, Hyprland, Hyprlock, Hypridle, the portal and the user systemd/D-Bus session.
2. If `~/.config/hypr/hyprland.lua` is absent, run DMS headless setup as that target user.
3. Copy the repository to the authorized VM location and run:

       WILSOF_TARGET_VM=1 /opt/wilsof-os/scripts/install-user-config.sh

4. The installer backs up replaced Wilsof-managed files under `~/.local/state/wilsof-os/backups/<UTC-time>/` before replacement. It preserves an existing personal DMS `settings.json` during normal upgrades.
5. The installer appends exactly one marked `require("wilsof")` to the DMS-generated entry point. Verify it occurs once and after `require("dms.binds-user")`.
6. It installs the Wilsof Hyprlock presentation file but does not change PAM configuration or account authentication.
7. Reload only bounded user components while working: `hyprctl reload`, `systemctl --user restart dms.service`, `systemctl --user restart hypridle.service`, and start `wilsof-session.target`. Do not log out or reboot mid-work.

## Power-profile backend

New images install `power-profiles-daemon`, the supported DMS backend. Before changing a profile, check that no competing manager is installed or active (`tlp`, `tuned`, or `auto-cpufreq`); do not enable competing managers together. Verify the system D-Bus name and service with:

    busctl --system status net.hadess.PowerProfiles
    busctl --system get-property net.hadess.PowerProfiles /net/hadess/PowerProfiles net.hadess.PowerProfiles Profiles
    systemctl status power-profiles-daemon.service

For a reversible selection test on supported hardware, record the `ActiveProfile` D-Bus property, select only an advertised profile, then restore the recorded profile. Do not test suspend, shutdown, reboot, firmware, or thermal-protection changes. A KVM VM without battery or platform-profile interfaces may only demonstrate backend availability or the clear unavailable state; it cannot validate power savings.

## VM fallback bindings

If the client intercepts Super before the guest, enable fallback bindings from a graphical Wilsof terminal:

    wilsof-vm-test-binds enable

Physically test `Ctrl+Alt+Space`, `Ctrl+Alt+L`, `Ctrl+Alt+I` and `Ctrl+Alt+F1` through the actual client-to-console path. Disable the layer after testing:

    wilsof-vm-test-binds disable

These commands only create or remove Wilsof's opt-in user file and reload Hyprland; they do not change client configuration.

## Recovery and reset

- Backups are under `~/.local/state/wilsof-os/backups/`.
- Use DMS Settings for personal DMS changes. Normal Wilsof reinstallation does not overwrite existing `settings.json` after first install.
- For an explicit Wilsof DMS reset, back up `settings.json`, remove `~/.local/state/wilsof-os/dms-defaults-v1` and the intended settings file, then reinstall deliberately.
- For a desktop failure, select a local fallback session in tuigreet, restore a backup, then inspect `journalctl --user -u dms -b` and the Hyprland log before retrying.

## Boot recovery without formatting

1. Boot an authorized recovery environment and mount the ESP at `/boot` plus the correct Btrfs `@` and `@home` subvolumes.
2. Verify `/boot/loader/entries/arch.conf`, kernel/initramfs, root UUID and `rootflags=subvol=@`.
3. Run `bootctl --esp-path=/boot install` and verify both the NVRAM entry and `EFI/BOOT/BOOTX64.EFI`.
4. Do not claim reboot success until one controlled reboot has actually been observed.

## Evidence discipline

Capture real screenshots of the desktop, launcher, settings, help and lock surface where permitted. Record whether each result was static validation, IPC, synthetic input, visual observation or physical keyboard input in `docs/testplan.md`.
