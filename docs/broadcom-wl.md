# BCM4360 / Broadcom STA integration — internal Private3 candidate

Status: source integration and isolated native kernel build/load demonstrated;
**physical Wi-Fi acceptance PENDING; public image redistribution NOT CLEARED**.
No Omarchy files, binaries, modules or configuration were copied.

## Hardware and exact baseline

The owner's read-only Omarchy diagnostic identifies PCI `14e4:43a0`, BCM4360,
and a working `wl` interface. This is owner-provided physical evidence for
Omarchy, not a Wilsof physical pass. Subsystem IDs have not been recorded.

Wilsof's approved repository epoch remains **2026-11-01**, not the builder's
running kernel or Omarchy's kernel. Fresh official database inspection and a
source-COW boot both identified:

| Input | Exact version |
| --- | --- |
| `linux`, `linux-headers` | `7.2.11.arch1-1` |
| Kernel release / module vermagic prefix | `7.2.11-arch1-1` |
| `broadcom-wl-dkms` | `6.30.223.271-50` |
| `dkms` | `3.4.4-1` |
| GCC | `16.2.1+r23+gd564253eb6c8-1` |

The original retained installed image lacked `wl` (`modinfo`: module not found).
This supports the missing-driver hypothesis; it does not establish the cause of
all physical Private2 wireless failures. The frozen official package, its
headers and dependencies installed with normal Pacman trusted signatures in a
new isolated COW guest; no host package transaction occurred.

## Native evidence and limits

- Official Pacman full-upgrade-plus-dependency transaction exited 0; DKMS built
  and installed `broadcom-wl/6.30.223.271` for the exact kernel above.
- A second explicit native DKMS build/install also exited 0. This demonstrates
  a repeatable recipe, **not bit-for-bit reproducibility**; generated signing
  identity/timestamps are not reproducible inputs.
- Installed file: `/usr/lib/modules/7.2.11-arch1-1/updates/dkms/wl.ko.zst`.
  `modinfo` reports dependency `cfg80211`, correct vermagic and
  `MIXED/Proprietary`. `modprobe wl` succeeded; `lsmod` confirmed residency.
- Its actual PCI alias is class-wide `pci:v*d*sv*sd*bc02sc80i*`, not a
  chipset-specific supported-ID table. It matches a representative class-0280
  alias for `14e4:43a0`; **this alone does not prove successful BCM4360 probe**.
  Owner Omarchy evidence establishes practical chipset/driver compatibility;
  Wilsof physical initialization remains untested.
- Native `dkms build` with an unsupported kernel/missing headers exited 21.
  Source negative controls also cover missing headers, another kernel pkgbase,
  ABI mismatch, alias mismatch, absent module and failed build metadata.
- The native guest has only virtual Ethernet. NetworkManager continued to see
  the connected virtual interface; no emulated BCM4360, Wi-Fi scans, WPA,
  reconnect or wireless reboot result is claimed.

## Image and installed-target contract

`runtime/desktop-packages.txt` supplies **both** the live profile and installer
package closure, including `linux-headers` and `broadcom-wl-dkms`. DKMS supplies
GCC/make/patch dependencies. The existing frozen closure/signature verifier must
verify all these inputs in the eventual build, not silently change snapshots.

`runtime/broadcom-wl.py` checks actual installed package versions, the single
Arch `linux` kernel tree, header release, module file, vermagic, alias and
module dependencies. It uses the existing `arch-chroot -r` target boundary;
it never uses the builder's `uname` as the target ABI. Image customization and
fresh-target installation refuse missing/failed DKMS output even if Pacman's
post-transaction hook did not propagate a failing status.

The upstream package ships a vendor-wide blacklist. Wilsof supersedes that
file by the **same basename** in `/etc/modprobe.d`, using only
`softdep bcma pre: wl`: the native `bcma` module shares this PCI alias. It does
not blacklist b43/b43legacy/ssb/brcmfmac/brcmsmac or unrelated devices.
`/etc/mkinitcpio.conf.d/wilsof-wl.conf` adds `MODULES+=(wl)` so wl claims supported
hardware before root switch; cfg80211 follows through module dependencies.
The actual native `mkinitcpio -P` succeeded and `lsinitcpio` showed wl,
cfg80211 and the effective override in the resulting installed initramfs.
The fresh installer stages policy **before its final mkinitcpio**. Live
materialization stages it before package hooks. This still needs inspection
and boot tests on the eventual exact ISO.

DKMS's `AUTOINSTALL=yes` and packaged ALPM path triggers handle future kernel /
headers changes before mkinitcpio. Every new kernel epoch needs a native build
and post-update module/boot check. A passed build for 7.2.11 does not promise
support for a future Linux API. Kernel-update postcondition acceptance remains
separate from a frozen-snapshot maintenance no-op.

DKMS generated a build-local MOK private key in the native lab. Image-only
customization removes default `var/lib/dkms/mok.key` and `mok.pub` after module
verification; it refuses symlink/shared/unowned files. **Never call this on an
installed system**: the installer and update controller do not call it.
Fresh target DKMS generates its own key. The later immutable image audit must
independently prove no private signing material or other secret is shipped.

## Signing / lockdown

The native guest reports lockdown `[none]` and module signature enforcement `N`.
The DKMS-signed module loaded with an untrusted-key verification warning and
normal out-of-tree/proprietary kernel taints. No enforcement or package signature
setting was disabled. A generated DKMS certificate is **not** an enrolled
Secure Boot key. Secure Boot/lockdown-enabled boot and owner firmware policy are
unverified; do not turn either off silently or claim that this module is trusted.

## License and redistribution boundary

The exact official package contains
`/usr/share/licenses/broadcom-wl-dkms/LICENSE`. It was inspected directly,
including clauses 2.1–2.6 and 7.5. It is a Broadcom proprietary binary license,
not an ordinary GPL-only driver. In summary, its binary distribution grant is
conditional on completeness/unmodified software, Broadcom-product-only use,
accompanying license and notices, distribution obligations including indemnity,
restrictions on modification/reverse engineering and applicable export laws.
The official Arch recipe patches the source compatibility wrapper and installs
the shipped proprietary object separately; Wilsof reuses that official package,
not a new redistribution license or an Omarchy module.

**No legal clearance is asserted** for redistributing the resulting combined
kernel module or public ISO. Availability in Arch is not sufficient clearance
for Wilsof's public distribution. Internal owner-use development can establish
technical compatibility without authorizing a public image. Before public
packaging, obtain qualified license review of the exact object, wrapper
licenses, modifications and compiled-module distribution; preserve the package
license/notices. If that cannot be cleared, keep the public image free of STA
and provide an explicitly approved owner-side installation path using verified
Arch packages and matching headers. That public/private split is **not yet
implemented**, so this candidate must not be published as a public ISO.

## Primary provenance

- [Official frozen core repository database](https://archive.archlinux.org/repos/2026/11/01/core/os/x86_64/core.db)
- [Official frozen extra repository database](https://archive.archlinux.org/repos/2026/11/01/extra/os/x86_64/extra.db)
- [Exact Arch packaging tag / PKGBUILD](https://gitlab.archlinux.org/archlinux/packaging/packages/broadcom-wl-dkms/-/blob/6.30.223.271-50/PKGBUILD)
- [Upstream DKMS 3.4.4 manual](https://github.com/dkms-project/dkms/blob/v3.4.4/dkms.8.in)
- [kmod modprobe.d precedence](https://man.archlinux.org/man/modprobe.d.5.en)

The original Broadcom tarball URL in the exact recipe returned HTTP 403 during
this sprint. Its contents were not independently downloaded or declared
verified; license inspection uses the real official package instead. Retained
package SHA256: `e3f2532c3519c6267c93724046e27cf7ec70b4028db537bd22dc2813447b4ed9`.

## Physical acceptance checklist — all PENDING

1. Exact new Wilsof image boots on the owner MacBook.
2. `lspci -nnk` identifies `14e4:43a0`, with wl bound; no firmware/probe error.
3. `nmcli device` discovers a wireless interface; do not require a guessed name.
4. Radio/rfkill state permits scanning; nearby networks are visible.
5. Owner enters WPA credentials privately and establishes connectivity.
6. Disconnect/reconnect and a normal reboot preserve connectivity.
7. Review kernel logs, battery/suspend/wake and regulatory behavior on hardware.
