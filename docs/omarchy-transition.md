# Omarchy replacement: final readiness and minimal recovery plan

13 November 2026: **NO-GO for replacement; owner approved non-destructive physical Live testing only.**
The owner requires disk encryption. USB identity/write confirmation is still needed;
installation and internal-disk changes remain unauthorized. Keep Omarchy intact.

## Accepted image — preserve unchanged

- File: `wilsof-test-only-2026.11.11-rc2-r2-test-only-x86_64.iso`
- Bytes: `2816741376`
- SHA256: `43932a59dc4380f499f7b84a85fc81928e6a63bd02a6a84521ed5c8122e4e0ad`
- Frozen image source: `231483e3510206a03c12ff76dbb5f308892cc3cc`
- Acceptance: **59 PASS / 0 FAIL / 0 NOT RUN**, plus retained evidence review PASS.
- Trust remains **TEST ONLY; production approval pending**.

Original and content-addressed export were independently rehashed on 13 November;
both match acceptance and remain root-owned, mode 0640. The export is classified
PROTECTED in the existing artifact catalog. Both are on the builder, not an
independent off-host backup. Private exact locations, acceptance receipts and the
fresh verification receipt remain in the existing private checkpoint area.
Do not relabel, patch, rebuild or replace this accepted image for cosmetic issues.
The current dashboard is [issue #16](https://github.com/tomli0/wilsof-os/issues/16);
[issue #60](https://github.com/tomli0/wilsof-os/issues/60) retains release gates.

## Only remaining replacement gates

1. **Physical daily-use acceptance is missing.** Run the checklist below on the
   actual machine; virtual module loading is not Broadcom Wi-Fi connectivity.
2. **Recoverable Omarchy/data backup is unverified.** Complete destination readback
   and a real restore rehearsal before erasing anything. A home backup alone is
   not OS rollback; a snapshot on the target disk is not an independent backup.
3. **Security/maintenance decision is unresolved.** This image uses TEST ONLY trust,
   unencrypted ext4 plus a FAT32 ESP, and no automatic OS rollback. Its installer
   explicitly rejects encryption. Production signing/enrollment remains owner-gated;
   do not silently promote the test key. A coherent version-changing update and
   explicit recovery passed, but that bounded transition does not establish ongoing
   delivery of later compatible security updates. Resolve the production trust and
   maintenance path, and explicitly accept the disk layout before replacement.
   Encryption is now REQUIRED, so this image is unsuitable for installation; do not
   improvise a disk conversion. Required-by-default LUKS2-root support has passed
   bounded source review in the existing installer, but is NOT included or accepted
   in this ISO. It needs a
   genuine encrypted installation, cold-boot unlock/recovery and a newly accepted
   candidate before physical replacement. The unencrypted ESP is disclosed.

No critical code defect was established by this readiness review. Noninteractive
`wilsof` PATH limitations and retained QML/logout diagnostics do not justify a
new build. Public redistribution/legal clearance is separate from this private
migration decision; no professional security certification is claimed.

## Essential physical checks — all still NOT RUN

Live testing is authorized. Identify the expendable USB by model/serial/capacity,
write only that device, and verify the written image bytes against the accepted
ISO. Use the [owner USB procedure](internal-test-runbook.md#usb-preparation-performed-by-the-owner).
Boot Try Wilsof through UEFI. Do not install, mount personal volumes read-write,
or change firmware security settings to force a pass.

- UEFI/Live and recovery-media boot; internal storage detected without alteration.
- i915/internal display, scaling/brightness, keyboard/layout and trackpad.
- BCM4360 `14e4:43a0` actually bound to `wl`: scan, WPA, DNS/Internet and reconnect.
- Speakers/headphones, microphone and Bluetooth pairing/reconnect if used daily.
- Manual/lid suspend and resume on AC and battery: display, input and Wi-Fi recover;
  screen remains securely locked. Check charging, battery reporting and abnormal heat.
- Normal login/logout, manual/idle lock and unlock, reboot/shutdown; open the actual
  daily applications and essential peripherals, not just a local browser fixture.

Live results do not prove installed cold boot or persistence. After a separately
authorized installation, repeat only installed-specific boot/login, hardware,
lock/resume and data-persistence checks. Any daily-critical failure means stop.

## Minimal migration — future, separately authorized

1. Before destructive work, keep two independently stored verified backup copies,
   including one restorable full-disk Omarchy image with GPT/ESP and any encryption
   recovery material. Boot independent recovery media, read backups back, restore
   the system image onto a spare target and prove it boots. Test representative
   personal files, browser data, projects and private-key permissions from backup.
   No suitable spare/verified restore means NO-GO; do not substitute a checksum.
2. Prefer a separate Wilsof system disk, if available: preserve Omarchy offline,
   disconnected during installation. Otherwise require the verified full-image
   restore above. No repartitioning/dual-boot experiment is part of this plan.
3. Obtain explicit installation approval naming the physical target and accepted
   ISO. Recheck actual model/serial/size, partitions, mounts and USB identity.
   Stop on any ambiguity or installer refusal. Stable power; no hotplug or other
   disk writers. Only a future accepted encrypted candidate may use
   `wilsof-install --encrypt --replace-existing`,
   with the exact displayed plan-bound confirmation. It erases the entire target;
   default `wilsof-install` is strict blank-disk-only. Neither preserves Omarchy.
4. Verify the clean installed desktop and essential hardware after disk-only cold
   boot before restoring selected data. Do not copy Omarchy's Hyprland/DMS,
   autostart, systemd-user or package/repository configuration wholesale. Keep old
   backups/media until the restored daily workload has passed.

## Rollback — manual, not automatic

Stop installation/use if a critical gate fails. Preserve the error and any new
Wilsof user data to independent storage before restoring an older image.
With a preserved separate Omarchy disk, power off and return to that disk through
the firmware boot menu. With an overwritten disk, boot the independently tested
recovery media, revalidate the destination identity, and restore the rehearsed
full-disk image; then prove Omarchy boots and selected data opens. Do not invent
physical restore/format commands before the exact disks and backup tool are known.
EFI repair is documented separately in [recovery](recovery.md); it is not OS rollback.
For a failed update, stop retries, preserve transaction/package logs and use the
reviewed coherent full-set recovery; never blindly remove a package lock.

**Replacement requires physical PASS, verified restoration, resolved security/
maintenance choices and explicit owner approval. No more unchanged virtual tests
or infrastructure are needed for this readiness decision.**
