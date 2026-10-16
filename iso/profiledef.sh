#!/usr/bin/env bash
# Internal Wilsof live-test profile. Build with scripts/build-iso.sh.
iso_name="wilsof-test"
iso_label="WILSOF_TEST_$(date +%Y%m)"
iso_publisher="Wilsof OS internal testing <https://github.com/tomli0/wilsof-os>"
iso_application="Wilsof OS internal live-test environment"
iso_version="dev"
install_dir="boot"
buildmodes=("iso")
bootmodes=("bios.syslinux.mbr" "bios.syslinux.eltorito" "uefi-x64.systemd-boot.esp" "uefi-x64.systemd-boot.eltorito")
arch="x86_64"
pacman_conf="pacman.conf"
file_permissions=(
  ["/etc/skel/.config/hypr/wilsof.conf"]="0:0:644"
  ["/etc/skel/.config/hypr/wilsof.lua"]="0:0:644"
  ["/etc/skel/.config/hypr/hypridle.conf"]="0:0:644"
  ["/etc/skel/.config/hypr/hyprlock.conf"]="0:0:644"
)
