#!/usr/bin/env bash
# Arch install for the explicitly verified, empty VM 113 system disk.
# This is intentionally single-use and refuses unexpected disk state.
set -euo pipefail

DISK=/dev/sda
[ -b "$DISK" ] || { echo "Refusing: $DISK is absent." >&2; exit 1; }
[ "$(blockdev --getsize64 "$DISK")" = 42949672960 ] || {
  echo "Refusing: $DISK is not the expected 40 GiB disk." >&2; exit 1;
}
if sfdisk --dump "$DISK" 2>/dev/null | grep -q .; then
  echo "Refusing: $DISK now has a partition table." >&2; exit 1
fi
if wipefs --noheadings "$DISK" | grep -q .; then
  echo "Refusing: $DISK now has filesystem signatures." >&2; exit 1
fi

sgdisk --zap-all "$DISK"
sgdisk --new=1:0:+1GiB --typecode=1:EF00 --change-name=1:EFI \
      --new=2:0:0 --typecode=2:8300 --change-name=2:ArchBtrfs "$DISK"
partprobe "$DISK"
mkfs.fat -F 32 -n EFI "${DISK}1"
mkfs.btrfs -f -L ARCHROOT "${DISK}2"

mount "${DISK}2" /mnt
btrfs subvolume create /mnt/@
btrfs subvolume create /mnt/@home
umount /mnt
mount -o noatime,compress=zstd:3,subvol=@ "${DISK}2" /mnt
mkdir -p /mnt/{boot,home}
mount -o noatime,compress=zstd:3,subvol=@home "${DISK}2" /mnt/home
mount "${DISK}1" /mnt/boot

pacstrap -K /mnt base linux linux-firmware btrfs-progs networkmanager sudo qemu-guest-agent \
  hyprland hyprlock hypridle xdg-desktop-portal-hyprland xdg-desktop-portal-gtk \
  dux-shell greetd greetd-tuigreet firefox ghostty nautilus gnome-text-editor papers loupe vlc \
  pipewire pipewire-pulse wireplumber polkit-gnome power-profiles-daemon

genfstab -U /mnt >> /mnt/etc/fstab
arch-chroot /mnt /bin/bash -s <<'CHROOT'
set -euo pipefail
ln -sf /usr/share/zoneinfo/Europe/Oslo /etc/localtime
hwclock --systohc
sed -i 's/^#\(nb_NO.UTF-8 UTF-8\)/\1/' /etc/locale.gen
locale-gen
printf 'LANG=nb_NO.UTF-8\n' > /etc/locale.conf
printf 'KEYMAP=no\n' > /etc/vconsole.conf
printf 'wilsof-arch-test\n' > /etc/hostname
cat > /etc/hosts <<'EOF'
127.0.0.1 localhost
::1 localhost
127.0.1.1 wilsof-arch-test.localdomain wilsof-arch-test
EOF
useradd -m -G wheel -s /bin/bash wilsofdev
install -d -m 0750 /etc/sudoers.d
printf '%%wheel ALL=(ALL:ALL) ALL\n' > /etc/sudoers.d/10-wheel
chmod 0440 /etc/sudoers.d/10-wheel
visudo -cf /etc/sudoers.d/10-wheel

# Do not rely on Arch's agreety default: this VM must present tuigreet and
# start Hyprland only after normal PAM authentication.
install -d -m 0755 /etc/greetd
cat > /etc/greetd/config.toml <<'EOF'
[terminal]
vt = 1

[default_session]
command = "tuigreet --time --cmd Hyprland"
user = "greeter"
EOF
systemctl enable NetworkManager.service greetd.service
systemctl enable greetd.service
[ -s /etc/greetd/config.toml ] || { echo "greetd configuration missing" >&2; exit 1; }
systemctl set-default graphical.target
systemctl add-wants multi-user.target qemu-guest-agent.service
for unit in NetworkManager.service greetd.service qemu-guest-agent.service; do
  systemctl is-enabled "$unit" | grep -qx enabled || { echo "required unit not enabled: $unit" >&2; exit 1; }
done
root_uuid=$(blkid -s UUID -o value /dev/sda2)
install -d -m 0755 /boot/loader/entries
cat > /boot/loader/loader.conf <<'EOF'
default arch.conf
timeout 3
console-mode max
editor no
EOF
cat > /boot/loader/entries/arch.conf <<EOF
title Arch Linux (Wilsof test)
linux /vmlinuz-linux
initrd /initramfs-linux.img
options root=UUID=${root_uuid} rootflags=subvol=@ rw
EOF
# Install to the ESP. `bootctl install` creates both the NVRAM entry and the
# removable-media fallback EFI/BOOT/BOOTX64.EFI; /boot is an ESP, not XBOOTLDR.
bootctl --esp-path=/boot install
for asset in /boot/EFI/systemd/systemd-bootx64.efi /boot/EFI/BOOT/BOOTX64.EFI /boot/vmlinuz-linux /boot/initramfs-linux.img /boot/loader/entries/arch.conf; do
  [ -s "$asset" ] || { echo "required boot asset missing: $asset" >&2; exit 1; }
done
bootctl --path=/boot status
CHROOT

printf '\nInstallation complete. Remote administration is not installed or enabled.\n'
