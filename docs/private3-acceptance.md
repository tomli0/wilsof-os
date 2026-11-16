# Private3 candidate acceptance and physical-test handoff

Status: **NOT ACCEPTED; no Private3 ISO at this checkpoint.** This is a gated
runbook, not permission to authenticate a build, write USB media, install on the
MacBook, replace Omarchy or publish proprietary binaries.

## 1. Frozen build identity and privilege boundary

The retained reviewed build uses source
`7c3771b3c2c4b2ef05477f09bab8f0f3baa10261`, Archiso **92-1**, the **2026-11-01**
repository snapshot and kernel **7.2.11-arch1-1** with matching headers. Its
proposed filename is `wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso`.
A proposed name is not an artifact: byte size and SHA256 remain unavailable.

Use the existing private, hash-locked owner command, delivered separately.
It performs one owner-authenticated bounded build through the reviewed
architecture; never start a second attempt because an SSH request timed out.
First reconcile that same service, one-shot marker, output and receipts. Rootful
staging, lock acquisition, trusted package-signature freeze and live resource /
namespace/device-denial checks remain mandatory inside the privileged phase.
A nonprivileged `--check` does not establish those root-only postconditions.

The newer audit/test/documentation files are outside `runtime/image-files.txt`.
They do not change the retained 7c3771b image payload or authorize regenerating
its source archive. Keep builder inputs and image-source identity pinned even
when the delivery branch later gains QA/report commits.

## 2. Read-only provenance tool: useful but deliberately partial

After an actual successful build, independently read the exact ISO and its
build receipt. On a trusted analysis host with `git`, `xorriso` and
`unsquashfs`, run the current audit tool against the image's build-source SHA,
not the delivery branch's later documentation HEAD:

```sh
python3 scripts/audit-iso.py \
  --iso /absolute/private/candidate.iso \
  --sha256 ACTUAL_INDEPENDENTLY_RECORDED_64_HEX_SHA256 \
  --source /absolute/path/to/independent/git-checkout \
  --commit 7c3771b3c2c4b2ef05477f09bab8f0f3baa10261 \
  --output /absolute/private/new-audit-directory
```

The checksum placeholder intentionally is not executable as a valid digest.
Do not replace it with a measurement and call that independent provenance:
reconcile the successful retained build receipt/export and actual bytes first.
The output parent must exist; the new output must be outside the source tree.

The tool never mounts, boots, installs, extracts a root filesystem or executes
image code. It checks the ISO hash before creating output, locates and hashes
the actual contiguous SquashFS extent, compares every allowlisted payload byte
against the exact independent Git commit, checks the embedded checksum map and
extra source members, reads package versions/license identifiers from the image
package database, performs a narrowly described private-path scan, and rechecks
the unchanged ISO. Existing output is never overwritten. External tools have
per-call timeouts and a finite aggregate tool budget; use a bounded foreground
invocation appropriate to the host for the entire audit, including hashing.

`audit.json` is private (directory 0700/file 0600). Preserve FAIL receipts.
A PASS is **only these static checks**, not package-signature, full secret,
UEFI, module, initramfs, installer, security or hardware acceptance. A package
license identifier is not legal clearance. Fixture/data-only ISO tests are not
product builds. Historical Private2 tool controls do not pass any Private3 gate.

## 3. Complete immutable audit still required

Before a guest boots, retain the successful build exit/service result and:

- Filename, bytes, independently read SHA256, exact source/archive identity,
  Archiso version, full official signed closure and separate private input pins.
- Actual El Torito/GPT/UEFI identity; inspect **both** ISO9660 entries and the
  embedded EFI filesystem. Confirm default loader, diagnostic path,
  `cow_spacesize=75%`, normal `copytoram=n`, kernel and initramfs paths/hashes.
- SquashFS hash, root-owned executable installer/provisioning entrypoints,
  application inventory, desktop settings, keybindings and installer scripts.
- Expected dated Pacman configuration, required/trusted official signatures,
  snapshot record and absence of builder-only cache paths in runtime mirrors.
- Empty/uninitialized machine identity, no seeded account/authorization or
  private keys; inspect content as appropriate, not just filenames. Do not
  publish account databases, network profiles or anything suspected to be secret.
- Exact `wl` file for 7.2.11-arch1-1, vermagic, dependencies, `modules.dep` /
  aliases, headers, effective modprobe override and initramfs contents. Verify
  default DKMS `mok.key`/`mok.pub` are absent **in the immutable image**.
- Applicable Broadcom/firmware license files, actual module firmware metadata,
  supplied runtime/firmware files and NetworkManager unit/enablement. Do not
  assume a firmware filename or a class-wide alias proves physical support.
- `wilsof`/doctor/update source inclusion and actual ordinary-user deployment.

Keep proprietary redistribution, Secure Boot and broad security review open.
See [Broadcom contract and license limits](broadcom-wl.md).

## 4. Exact-image QEMU matrix

Reuse the retained Private2 acceptance methodology, not its artifact identities
or PASS rows. Adapt only after the actual Private3 ISO identity is known.
Create a new unique private guest directory, fresh firmware and a new blank
QCOW2 **without a backing file**. No historical installation disk is attached.
Hold the existing QA lock for the full supervised guest lifetime. Bound that
lifetime, resource use and installer waits; preserve first failure and real exit
codes. Use real normal password input only after exact prompt/readiness checks,
never passwords in argv/logs or root access as a login/unlock substitute.

All current rows below are **NOT RUN**, blocked by absence of a new ISO.

| ID | Mandatory gate | Required new-image evidence | Current status |
| --- | --- | --- | --- |
| 01 | UEFI boot from emulated USB | Read-only USB attachment, UEFI and live source identity | NOT RUN |
| 02 | Live Hyprland/Dux desktop | Owning session/processes and rendered frame | NOT RUN |
| 03 | Correct cowspace | Unmodified boot options and actual overlay capacity | NOT RUN |
| 04 | Install onto new blank virtual disk | Exact path/serial/size/blankness guard and real PTY | NOT RUN |
| 05 | Installer exits successfully | Installer exit 0, completion marker and target postconditions | NOT RUN |
| 06 | Disk-only boot without ISO | QMP attachments, no ISO and installed root/source | NOT RUN |
| 07 | Normal greetd/PAM password login | Actual username/password prompt and owning PAM/session evidence | NOT RUN |
| 08 | Installed desktop and branding | Owning desktop, normal-user source/config and rendered WS | NOT RUN |
| 09 | Unified menu before lock | Real WS/keyboard routes and owning query/results | NOT RUN |
| 10 | Native Hyprlock | Compositor acquisition, owning locker and ready surface | NOT RUN |
| 11 | Incorrect password rejected | Exact locker/PAM failure, lock retained | NOT RUN |
| 12 | Correct password unlock | Native authentication/release and original-session input recovery | NOT RUN |
| 13 | Menu after unlock | Actual shortcut/search in same resident shell, no restart | NOT RUN |
| 14 | Repeated lock/unlock | Second genuine cycle with same security/recovery checks | NOT RUN |
| 15 | Terminal, Firefox and Files launch | Actual processes, rendered content and functional input | NOT RUN |
| 16 | Workspace switching | Real shortcuts, owning workspace IDs and client preservation | NOT RUN |
| 17 | Normal reboot | Ordinary user action, changed boot ID and fresh password login | NOT RUN |
| 18 | Clean shutdown | Ordinary user poweroff, actual QEMU exit and offline disk check | NOT RUN |

Keep temporary inhibitors and emulator workarounds explicit; restore them.
Preserve volatile installer/runtime evidence and sync/unmount before shutdown.
Reconcile a shutdown RPC timeout against the exact guest before another power
command. Verify process exit before offline checks/hashes and releasing locks.
Historical source-COW tests remain a separate evidence class.

## 5. Additional new-image update and wireless gates

As the installed desktop user, first collect `wilsof version --json`,
`wilsof doctor` and `wilsof update --check` with actual exit statuses. Version
must identify the built image, not the later QA checkout. The live-media update
refusal is expected and is not an installed-update pass.

In the new isolated installed guest, preserve pre/post inventories and policy.
Exercise the actual interactive `wilsof update` through normal sudo/PAM only
within the authorized test scope. Review replacements and advisories before
accepting; never change the snapshot or use partial upgrades. Report a no-op as
a no-op. Preserve lock/source/signature refusals, config migration/personal
preference/backup bytes, per-file manual recovery and fresh authenticated
login/boot. Do not claim changed-version updates, mid-write recovery, concurrency
safety or atomic rollback from the earlier no-op/fixture evidence.

Record module loading/reboot separately from actual adapter binding and Wi-Fi.
QEMU Ethernet and a loaded `wl` module cannot pass the MacBook wireless gates.

## 6. Owner USB/hardware handoff — not yet authorized to execute

Only after exact-image audit and all required QEMU gates pass, deliver the
private ISO, byte size, checksum, source and acceptance report together. Keep
QA secrets/disks and raw private logs separate. No public Broadcom ISO release.

The owner then follows [the existing USB preparation procedure](internal-test-runbook.md#usb-preparation-performed-by-the-owner),
checking the expendable USB's model/serial/capacity and the exact checksum.
This does not authorize writing or installing on the internal MacBook disk.
Back up personal data independently and preserve Omarchy unchanged. First
physical phase is live USB evaluation only; no automatic installer invocation.

Owner checks, all still pending: USB/UEFI boot; keyboard/mouse/display/scaling;
`14e4:43a0` recognized and bound to `wl`; wireless interface; nearby networks;
owner-private WPA login; Internet/DNS; reconnect and normal reboot. Then audio,
Bluetooth, suspend/wake, battery/power and recovery must be evaluated separately.
Do not silently alter firmware security settings, share SSIDs/passwords/MACs or
call the live unlocked session an installed secure desktop. Use the read-only
hardware collector privately, and record failures without mounting personal
volumes read-write. Daily-driver replacement remains a separate owner decision.
