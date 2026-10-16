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

## Build requirements and limits

Build on a disposable Arch build host with:

- `archiso` installed (provides `mkarchiso` and the `releng` profile);
- root access for `mkarchiso` only;
- network access to the configured Arch package repositories;
- enough writable disk space for package cache, work tree and output ISO;
- no changes to Proxmox, VM 113, partitions, network services or the Hermes host configuration.

Run:

    sudo WILSOF_ISO_WORKDIR=/safe/work WILSOF_ISO_OUTDIR=/safe/out scripts/build-iso.sh --build

The script creates output locally and does not publish, install or attach it to a VM. A successful profile validation or script test is not an ISO build. Before accepting an ISO, boot it in an isolated disposable VM and manually inspect the login and live-session behaviour.
