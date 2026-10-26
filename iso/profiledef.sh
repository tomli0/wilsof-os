#!/usr/bin/env bash
# shellcheck disable=SC2034
# Archiso 91 profile data: these variables are consumed by mkarchiso.
iso_name="wilsof-internal"
iso_label="WILSOF_$(date -u +%Y%m)"
iso_publisher="Wilsof OS internal testing <https://github.com/tomli0/wilsof-os>"
iso_application="Wilsof OS internal live and installation test"
iso_version="$(date -u +%Y.%m.%d)"
install_dir="arch"
buildmodes=("iso")
bootmodes=("uefi.systemd-boot")
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=("-comp" "zstd" "-Xcompression-level" "6" "-b" "1M" "-processors" "2")
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/sudoers.d/wilsof-live-installer"]="0:0:440"
  ["/usr/local/lib/wilsof/live-setup"]="0:0:755"
  ["/usr/local/lib/wilsof/provision-target"]="0:0:755"
  ["/usr/local/bin/wilsof-install"]="0:0:755"
  ["/usr/local/bin/wilsof-config-update"]="0:0:755"
)
