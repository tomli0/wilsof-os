# Internal test ISO design

## Decision

Wilsof uses an `archiso` profile based on Arch's maintained `releng` profile at build time. The repository stores only the small Wilsof overlay (`iso/profiledef.sh`, `iso/packages.x86_64` and any future `iso/airootfs` files). `scripts/build-iso.sh --build` materializes a disposable copy of `/usr/share/archiso/configs/releng`, overlays the tracked profile files and invokes `mkarchiso`.

This keeps BIOS/UEFI boot support from the current Arch profile instead of copying bootloader implementation files into Wilsof. Archiso is the official Arch ISO build tool; `releng` is the upstream profile used as the intended customization base.

## Live environment

The live image contains the base system, kernel and firmware, NetworkManager, Hyprland, DMS, Hypridle, Hyprlock, portals, Ghostty, Firefox, Nautilus, GNOME Text Editor and Polkit agent. It is a live evaluation environment only:

- no autologin;
- no fixed user password;
- no SSH daemon, authorized keys, known_hosts or remote administration setup;
- no VM address, hostname identity or machine-specific configuration;
- no automatic disk partitioning, formatting or installation.

The image deliberately does not claim to install Wilsof. A future installer must be separately designed, reviewed and tested against a disposable target.

## Installed system

The existing `scripts/install-arch-test-vm.sh` and `scripts/install-user-config.sh` remain the only prototype installation path. They configure a dedicated test VM after explicit guards and retain user-owned DMS settings. The ISO profile must not use a VM system disk as an installation target.

## Separate build environment and isolation boundary

The build host is not the Hermes host, Proxmox host, VM 113, a workstation with user data, or a prospective installation target. Use a newly provisioned, disposable x86_64 Arch Linux VM (or equivalent isolated build machine) that is authorized solely for this build. Do not mount any target-system disks into it and do not reuse its work or output directories for another project.

The build machine needs:

- `archiso` installed, which provides `mkarchiso` and `/usr/share/archiso/configs/releng`;
- root access only for the one `mkarchiso` invocation; do not run the repository checkout or routine inspection as root;
- outbound package-repository access; no inbound SSH service, production credentials, private keys, authorized keys, tokens, known-hosts files, or machine-specific configuration copied into the profile;
- at least 25 GiB free in the filesystem that will hold both the work and output directories, plus enough RAM and CPU for the host's normal Arch package build; record the actual free space before starting;
- dedicated absolute directories, for example `/srv/wilsof-iso-work` and `/srv/wilsof-iso-out`, owned and used only by this test.

The repository contains an overlay only. `scripts/build-iso.sh` copies the distribution-maintained `releng` profile into `WILSOF_ISO_WORKDIR/profile`, overlays the tracked Wilsof files, and writes the resulting ISO only to `WILSOF_ISO_OUTDIR`. It does not select, mount, format, partition, attach, boot, publish, upload, or install an ISO. Those boundaries remain mandatory: do not change Proxmox, VM 113, disks, firmware, network services, or the Hermes host configuration for this test.

## Safe, reversible build-only test

This is the next authorized test. It produces a local artifact on the separate build host; it is not permission to boot it.

1. In a non-root shell, confirm the host and paths before doing anything:

       uname -m
       command -v mkarchiso
       test -d /usr/share/archiso/configs/releng
       df -h /srv/wilsof-iso-work /srv/wilsof-iso-out
       git status --short

   Continue only when the architecture is `x86_64`, the `releng` directory and `mkarchiso` exist, both directories are dedicated, and the filesystem has at least 25 GiB available. The checkout must be the reviewed commit with no unexpected changes.

2. From that checkout, run only the bounded builder:

       sudo WILSOF_ISO_WORKDIR=/srv/wilsof-iso-work WILSOF_ISO_OUTDIR=/srv/wilsof-iso-out scripts/build-iso.sh --build

3. After a successful command, validate the local artifact without booting or attaching it:

       find /srv/wilsof-iso-out -maxdepth 1 -type f -name '*.iso' -printf '%f %s bytes\n'
       sha256sum /srv/wilsof-iso-out/*.iso
       ls -ld /srv/wilsof-iso-work /srv/wilsof-iso-out

   Record the command exit status, ISO filename, byte size, SHA-256, build-host OS version, and repository commit in the issue or pull request. Treat a successful profile test or CI run as different evidence; neither proves that an ISO was built.

4. To revert this test, delete only the two dedicated directories after recording the artifact metadata. Do not use a broad path or a target-system mount. The disposable build VM may then be destroyed.

Stop immediately, retain logs, and do not retry on a target host if any prerequisite fails, the free-space threshold is not met, the builder requests an unexpected path, the output appears outside the two dedicated directories, a credential or machine-specific file is found, or `mkarchiso` exits nonzero. The next action is to document the failure; it is not to alter the ISO profile, host, VM, disks, or network ad hoc.

## Explicit authorization gates

A build artifact remains internal and local. Publishing or uploading an ISO, attaching it to any VM, changing boot order, booting it, creating an installation target, partitioning or formatting storage, and installing Wilsof each require separate, explicit authorization and a new safety review. Before an authorized future boot test, use a newly created disposable VM with no important disks and manually inspect the login and live-session behavior. No physical-client, firmware, boot, or installation validation has been performed by this documentation change.
