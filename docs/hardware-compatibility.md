# Hardware compatibility and physical acceptance matrix

This is an evidence ledger, not a universal hardware-support claim. The generic
installer accepts x86-64 UEFI, not a MacBook vendor/model. Both Intel and AMD
microcode are in the existing base selection. Standard kernel, firmware,
NetworkManager, PipeWire/WirePlumber, BlueZ and generic USB paths remain in scope.
No new driver, repository, blacklist, firmware override or proprietary GPU package
is introduced by this ledger.

## Tested environment versus intended hardware

| Combination | Evidence available | Classification / required next test |
| --- | --- | --- |
| QEMU q35 x86-64 UEFI, virtio block/network, bochs display, USB keyboard/tablet | Historical identified-image boot/install/PAM/desktop/input/network and source-overlay replacement/recovery evidence | Tested only in those identified virtual environments; not physical PC acceptance |
| Intel x86-64 + integrated graphics | Owner target is i915, 2560x1600; generic source is not vendor-restricted | Physical NOT RUN: acceleration, scaling, internal/external display, lock and resume |
| AMD x86-64 + AMD graphics | Generic source and AMD microcode retained; no AMD-specific native/physical gate executed | NOT RUN: actual GPU driver/firmware binding, rendering, lock, resume and display outputs |
| NVIDIA open-kernel/proprietary configurations | No verified NVIDIA configuration or licensing/integration change in this candidate | NOT RUN / not claimed supported; review exact GPU, matching kernel/driver, license and Wayland behavior before inclusion |
| Physical wired Ethernet | NetworkManager integration; virtual Ethernet is a regression control only | NOT RUN: actual Intel/Realtek/USB adapter binding, DHCP, DNS, Internet and reconnect |
| Common Intel/AMD-platform wireless adapters | Generic firmware and wireless diagnostic/authentication tools retained | NOT RUN by chipset: identify numeric ID, driver/firmware, scan, WPA, reconnect and resume |
| Owner Broadcom BCM4360 14e4:43a0 | Earlier native wl build/load/kernel-header/initramfs evidence; no physical device in QEMU | Physical NOT RUN: actual wl binding, scan, WPA, Internet, reconnect, reboot and resume |
| Generic USB input | Emulated USB keyboard/tablet exercised in QEMU | Physical NOT RUN: actual keyboard layouts/modifiers, mouse and hotplug; laptop trackpad/gestures separate |
| Audio and Bluetooth | PipeWire/WirePlumber/BlueZ components retained; VM audio was dummy and Bluetooth lacked adapter | NOT RUN: physical speakers/headphones/microphone and actual pairing/reconnect |
| Laptop power management | Existing power-profile, brightness and suspend integration, no hardware acceptance | NOT RUN: AC/battery, lid, brightness, thermal behavior, repeated suspend/resume and wake networking |
| Multiple displays / docks | No physical multi-output gate | NOT RUN: connection/hotplug, scale/refresh/orientation, workspace placement, lock on every display and resume |
| Secure Boot | No accepted firmware/kernel/module signing chain | Unsupported/not accepted; do not disable firmware policy or enroll keys automatically |

Broadcom wl is an additional owner-hardware integration, not proof that all PCs
need Broadcom. Generic installer target/boot logic must remain model-independent.
The known wl mitigation warning and proprietary redistribution assessment remain
open; do not suppress mitigations or infer legal clearance from package availability.

## Owner evidence contract

Use the [MacBook live-first checklist](omarchy-transition.md#4-live-usb-first-checklist-all-physical-rows-not-run)
only after exact new-image virtual acceptance. Record ISO filename/SHA256, machine
model, numeric device IDs, actual driver binding, kernel, display modes/scales,
boot ID and per-test PASS/FAIL/NOT RUN with sanitized observations. Keep SSIDs,
credentials, serials and personal network details private. A service being enabled
or a module file being present does not pass a physical functionality row.

Do not run the installer, erase Omarchy or mount personal volumes writable for
these tests. Replacement still requires independent backups, tested restoration,
working recovery media, physical acceptance, target verification and a separate
explicit owner approval.
