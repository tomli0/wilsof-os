# Internal ISO and physical-PC test runbook

Status is evidence-based: building an ISO is not live-boot verification; a live
boot is not an installation test; a VM installation is not physical-PC validation.
The session checkpoint records which of these actually passed.

## Scope and prerequisites

This integration branch is for one internal x86-64 UEFI test image. It combines
selected open PR changes without merging `main` or `arch-install`.
`docs/checkpoints/internal-iso-integration.json` records included/excluded PRs and
exact source revisions. Worker/scheduler changes and the Terra QA stage are not
part of this image or deployed by this workflow.

Build only a clean `git archive` export. Record `git rev-parse HEAD` outside the
build environment, write that exact value to the export's `SOURCE_COMMIT`, and
check it against the reviewed revision. Set `WILSOF_SOURCE_COMMIT` to that value.
Use Archiso 91 in an isolated Arch environment, a new absolute work directory
and a separate empty output directory. No host disks, credentials, `.ssh`, Git
credential helpers or private home directories may be mounted into the build.
The source payload is limited by `runtime/image-files.txt`; symlinks are rejected.

    WILSOF_SOURCE_COMMIT=<exact-reviewed-40-character-commit> \
    WILSOF_ISO_WORKDIR=/export/new-work \
    WILSOF_ISO_OUTDIR=/export/new-output \
    WILSOF_HYPRIDLE_PACKAGE=/verified-artifacts/hypridle-0.1.8-2.1-x86_64.pkg.tar.zst \
    /src/scripts/build-iso.sh --build

The internal Hypridle artifact is supplied separately, never committed as a
binary. Its package and installed-executable SHA256 are pinned in
`runtime/pinned-package.py`; mismatches fail closed. The same verified package
is installed into the live root during the pinned Archiso 91 customization step
and copied/installed into the target during provisioning. This step does not
rebuild Hypridle. The Archiso 91 customization hook is deprecated upstream and
must be reviewed before changing the supported Archiso version.

The prepared profile is a sibling of the work directory. A new successful
`mkarchiso -r` build removes its work directory. A resumed existing work directory
is retained by upstream Archiso; preserve logs and clean up only that dedicated
session directory after evidence has been recorded. The builder does not publish
or attach images. The evidence records the actual environment and command.

## Live environment

The `live` account is an ephemeral evaluation account, not a development account
or installed administrator. A fresh password is generated at boot, displayed only
on the local console banner, and never embedded in the image. Use Ctrl+Alt+F2,
log in as `live` with that boot's displayed password (input is hidden), then run
`sudo wilsof-live-recover` for relevant logs or add `--restart` to retry desktop
setup. Ctrl+Alt+F1 returns to graphics. Root remains locked; do not try empty-root
login. No network login is enabled. Recovery starts independently before graphical
setup; failures reveal the console and useful journals rather than hide them.

The ISO intentionally opens an unlocked graphical session. Lock requests route
to an explicit warning; idle locking is disabled for the evaluation account.
Do not use it for private work. Its only root commands are the root-owned
installer and exact diagnostics/retry helper; there is no blanket passwordless
sudo policy. This account, credential banner and recovery policy are live-only.

See [boot menu/splash limitations](../iso/boot/README.md): Try Wilsof OS is the
safe no-install default, with optional RAM copying, speech and diagnostic entries.
Esc reveals Plymouth boot details. The RAM-copy entry leaves real upstream `pv`
progress visible; the normal splash is indeterminate, not a fake percentage.

The intended session is Hyprland/DMS with the approved WS assets, Spotlight
(`Super+Space`), help (`Super+F1`), Ghostty, Firefox, Nautilus, Text Editor, Papers,
Loupe and VLC. This is not a claim of universal file/window/action search.
The live setup disables GNOME automatic volume mounting/opening; do not manually
mount existing internal disks while evaluating the image.

## Disposable VM installation

Use a new VM with UEFI, at least 4 GiB RAM, and only a newly created virtual disk
of at least 16 GiB plus the test ISO. Give the virtual disk a stable serial; never
attach a physical disk, NAS volume, existing VM disk or reference VM 113's disk.
The adapter deliberately requires every target byte to be zero and refuses used,
mounted, partitioned, aliased/in-use or unidentified targets. Merely deleting a
partition table is insufficient. The first runtime supports only unencrypted
ext4 root plus a 1 GiB FAT32 ESP; no dual boot, resizing or encryption is provided.

Launch `Install Wilsof` from Spotlight, or run `sudo /usr/local/bin/wilsof-install`
from a live terminal. Enter an explicit target path and a new administrator name,
then a hidden password twice. Read the package/layout/target summary and data-loss
warning. Only the exact requested `ERASE /dev/...` confirmation proceeds.
No password is stored in the plan, argv or build inputs. The disk is revalidated
immediately before the existing archinstall backend formats it.

The installer does not reboot automatically and does not promise rollback.
After success, inspect the boot assets and logs, unmount the target cleanly,
shut down the disposable VM, detach the ISO, and boot from its virtual disk.
Verify normal password login, networking/DNS, services, applications, theme/help
and persistence. Synthetic terminal/key input and screenshots must be labelled
as such; they are not physical-keyboard or hardware evidence.

## Updates and recovery limits

Arch package updates use the real supported full-system upgrade command:

    sudo pacman -Syu

Read Arch news before a significant update. Never use `pacman -Sy` followed by
selective installs (partial upgrades). Record package versions and the command's
actual result. Reboot the test VM when the kernel/system components require it,
then check login/networking and the desktop again. Arch updates can change
Hyprland/DMS APIs; compatibility is not guaranteed by a successful download.
The installer is pinned to archinstall 4.5; a different version is refused until
the adapter is reviewed/tested against it.

Wilsof configuration updates are local, explicit and separate from Arch packages:
obtain and inspect the intended source commit, extract its reviewed archive to an
absolute local directory, then run as the desktop user, without sudo:

    wilsof-config-update /absolute/path/to/reviewed-source

This implemented command applies only Wilsof-owned user files, preserves existing
personal DMS settings and generated base configuration, and creates per-file
backups for changed managed files under `~/.local/state/wilsof-os/backups/`.
It does not fetch or trust remote code automatically. Review the source first.
Log out/in to activate a configuration change. The installed source commit is
recorded in `/usr/share/wilsof/source/SOURCE_COMMIT`; a user-only config update
does not replace that root-owned system bundle or falsely update its provenance.
Record the applied user-config source revision separately.

There is no transactional update rollback, disk-format rollback, boot snapshot
or automatic recovery mechanism. A per-file backup is not such a mechanism.
For a bad user-config update, use a console to inspect/restore only the affected
managed files from its recorded backup, then re-test. Keep the known test ISO
available for diagnostics. Do not repartition or rerun installation as boot repair.

## Consolidated spare-PC checklist (owner-operated, not VM evidence)

1. Save the final ISO filename, byte size, SHA-256, source commit and VM evidence.
   Use exactly the same bytes that passed the final VM test, not a later rebuild.
2. Back up the spare PC. Inventory its CPU/UEFI, GPU, network, audio and storage;
   disconnect unrelated/internal data disks where practical. Do not select a used
   disk for this first-alpha installer. Physical installation requires separate
   owner confirmation and an eligible dedicated empty disk.
3. Prepare a dedicated expendable USB drive using the instructions below. Verify
   its identity/capacity; all data on that USB will be lost. No agent writes it.
4. Boot from the USB in UEFI mode using the PC's boot menu. Secure Boot signing is
   not provided; do not enroll keys or silently change firmware security settings.
   Record firmware/Secure Boot state and any boot failure.
5. Check the visible desktop, WS theme, scaling, launcher, help, terminal/browser,
   keyboard layout and physical shortcuts. Do not infer these from VM input.
6. Check actual Ethernet/Wi-Fi, DNS, GPU/display outputs, audio/microphone and
   input devices. Do not include network passwords or personal identifiers in
   shared logs. Do not mount existing Windows/data volumes read-write.
7. Check physical lock/unlock only on an installed account with its real password;
   the live evaluation session is intentionally unlocked. Suspend/resume, power
   behavior, USB boot and battery/thermal results require their own observations.
8. Only if separately confirmed, install to the dedicated eligible physical test
   disk, then remove the USB and verify installed boot/login/network/desktop and
   the update procedure. Record device IDs and limitations; unknown stays unknown.

## USB preparation (performed by the owner)

First verify the downloaded ISO with `sha256sum <ISO-file>` against the recorded
final checksum. Use an image-writing tool, for example GNOME Disks → select the
expendable USB by model/serial/capacity → Restore Disk Image → select the exact
verified ISO → review the destructive destination confirmation → write. Do not
copy the `.iso` as an ordinary file or format a partition and assume it is bootable.
Use the writer's verification option when available and safely eject afterwards.
Do not select an internal disk or NAS. This procedure is documentation only;
no physical USB device has been attached or written by the agent.
