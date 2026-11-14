# Wilsof OS — Private3 exact-image acceptance, 9 November 2026

Status: **REPLACEMENT NO-GO.** All 18 basic virtual functional gates passed on the
new Private3 ISO. Overall QEMU acceptance is **FAIL** because normal logout
reproducibly crashes xdg-desktop-portal-hyprland. Daily-driver readiness and
physical acceptance are not claimed.

Engineering/QA began at 19:43 UTC. Artifact/runtime work was completed before
20:30 UTC; preservation and publication continued afterwards. Starting delivery
HEAD was `bd43c9703d4727df7100c4c268471bece2f46fe2`; source correction is
`435e2cdca517ec8a6c33e1a83fb2098a07a031f3` on
`integration/private3-20261107`. Frozen image source remains
`7c3771b3c2c4b2ef05477f09bab8f0f3baa10261`.

## Evidence scope

This is new exact-image evidence, not transferred Private2/source-COW acceptance.
Private evidence group `private3-acceptance-20261109T1944Z` retains the immutable
audit, full read receipt, image members/EFI inspection, screenshots, 18-row JSON
matrix, installer transcript/result, native update/configuration tests, cores,
launch/exit identities, offline disk check and transfer manifest. The private
handoff gives actual hosts/absolute paths; they are deliberately not public here.

No physical owner files, disks, USBs, Omarchy, Proxmox configuration, package
signature policy or frozen repository date were modified. No additional ISO
build, main merge, public ISO release or worker/scheduler activation occurred.

## 1. Completed milestones and readiness classification

- Independently hashed the owner-readable export and local analysis/candidate
  copies; all match the independently supplied expected SHA256.
- Executed the existing read-only immutable audit: PASS, 64 independent Git payload
  files, 815 image package metadata records and its scoped private-path scan.
- Read/decompressed all 154,754 regular SquashFS members successfully: exit 0,
  5,382,665,751 logical bytes, without extracting/executing image code on the host.
- Inspected actual ISO/EFI boot structures, kernel/initramfs, wl ABI/dependencies,
  boot options, package policy, executable modes, identity and relevant notices.
- Completed a real interactive installation on a newly created no-backing 24 GiB
  QCOW2, then disk-only normal authentication, desktop, application, lock, update,
  persistence, reboot, second cold-boot and ordinary shutdown tests.
- Implemented and pushed a reviewed source-only installer review correction.
- Added the [gated backup/hardware/recovery procedure](../omarchy-transition.md).

| Classification | Result |
| --- | --- |
| SOURCE TESTED | PASS: 435e2cd, 786 tests passed / 3 explicit opt-in skips |
| ISO BUILT | PASS: owner-controlled completed artifact, frozen source 7c3771b |
| ISO VERIFIED | PARTIAL: provenance/rootfs/boot/module checks PASS; full required-notice inclusion unresolved |
| QEMU ACCEPTED | NO: 18 basic gates PASS, additional teardown stability FAIL |
| PHYSICAL TEST READY | Replacement NO-GO; future live-only investigation remains separately gated |
| PHYSICAL ACCEPTED | NOT RUN |
| DAILY DRIVER READY | NO |

## 2. QA findings and corrections

No Claude/paid-provider QA was commissioned. A separate bounded read-only AI
context reviewed the installer patch and relevant inventory/schema/review/guard
chain. It returned PASS with no security concerns or logic errors. Exact artifact
SHA256: `4c7e0c25696580a6de87ca4b44781e339b59abb20f9fb3852c8639603fd857f8`.
This is independent AI-context review, not human security approval.

| Finding | Evidence and classification | Disposition |
| --- | --- | --- |
| Target review hid device labels behind the identity hash | Frozen installer prints path/bytes/hash but not manufacturer/model/transport | Source fixed in 435e2cd; current ISO unchanged |
| Portal crashes on ordinary logout | SIGSEGV at 20:20:48 UTC, repeated at 20:24:37 after a fresh reboot with no new config mutation | Confirmed reliability FAIL; preserved cores/stack/journals; unresolved |
| Hypridle exits nonzero at compositor teardown | `Disconnected from pollfd id 1` / `Event loop disconnected`; no Hypridle core observed | Disclosed teardown behavior, not mislabeled as a Hyprland crash |
| Broadcom security warning | Actual boot logs report incompatible kernel security mitigations and an unpatched return thunk | Open safety limitation; no mitigation/signature bypass |
| Dux required-notice inclusion | Package declares MIT; its immutable package file list has no standalone license path | Full inclusion gate PENDING; embedded notices not independently verified |
| Initial app-readiness assertion was too early | Ghostty was not yet mapped at 3 seconds; later same launch mapped and rendered an actual echo command/output | Automation timing defect, preserved/adjudicated; no product renderer override |
| Software-page harness assumed search included root categories | Actual model searches commands; root navigation reached Software correctly | Automation defect, not a product failure; corrected input route tested |

The portal stack includes `wl_proxy_marshal_array_flags`,
`wl_proxy_marshal_flags` and libc exit handlers. It supports an exit/Wayland proxy
lifetime hypothesis, not a symbolized proof of the exact C++ object or a verified
patch. Similar upstream reports are [#330](https://github.com/hyprwm/xdg-desktop-portal-hyprland/issues/330)
and [#453](https://github.com/hyprwm/xdg-desktop-portal-hyprland/issues/453).
The latter explicitly describes an unbuilt/untested proposal for another package
version; no upstream issue prose or suggested diff was treated as acceptance.
Do not conceal this failure with restart suppression, success-exit overrides or
an unreviewed snapshot/package change.

## 3. Code quality and security status

`435e2cd` adds device-reported manufacturer, model, transport and removable state
to the existing escaped JSON destructive review. Exact byte capacity remains
visible; raw serial/WWN remain private behind the identity hash. Labels participate
in the plan digest and the immediate final probe equality. Missing metadata is
explicit, not inferred to mean an internal drive. Explicit selection, full-disk
zero verification, used/live-media refusal and exact destructive confirmation
remain unchanged. Nine new synthetic cases cover output, cancellation, changed
metadata and escaped control characters. RED/GREEN output was retained.

`python3 -m pytest -q`: 786 PASS / 3 opt-in SKIP, exit 0. Python AST, schema JSON,
ShellCheck in the prescribed sh/bash dialects and whitespace checks passed.
Tests are source/fixture evidence; this new installer has not been installed from
an ISO. Documentation-only close-out does not require another product test run.

The immutable image contains no home files/development users, all shadow entries
were locked, machine-id is `uninitialized`, and the scoped private-key scan
passed. Actual DKMS MOK key/public-key paths were absent. These are bounded checks,
not comprehensive secret, human security, legal or Secure Boot clearance.

## 4. Commits, PR and CI

| Commit | Role | Evidence |
| --- | --- | --- |
| 7c3771b3c2c4b2ef05477f09bab8f0f3baa10261 | Frozen image/runtime source | Independent Git payload byte comparison |
| bd43c9703d4727df7100c4c268471bece2f46fe2 | Starting delivery/QA head | Actual initial local/remote identity |
| 435e2cdca517ec8a6c33e1a83fb2098a07a031f3 | Installer target-review correction | Full source suite, bounded review, pushed and four remote file blobs read back |

The final documentation commit adds this report/checkpoint and the transition
procedure without changing the tested runtime. Draft [PR #61](https://github.com/tomli0/wilsof-os/pull/61)
remains the existing delivery PR, based on `integration/private2-20261107`.
`gh pr checks` reported no checks; missing exact-head CI is not green CI.
No merge, ready transition, reviewer request, auto-merge or public release is
part of this delivery. Exact final remote identities/read-back are retained in
the private publication receipt.

## 5. Exact ISO and immutable verification

| Field | Actual result |
| --- | --- |
| Filename | `wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso` |
| Bytes | 2,813,849,600 |
| SHA256 | `111c06b70cf6d909b3e815975f69bfa18f299af9dcfe9bbbfd5e197992c53a59` |
| Image source | `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261` |
| SquashFS bytes | 2,257,866,752 |
| SquashFS SHA256 | `d27911ce785a06e12bb271e3cb5e17b1e4814861daf3aff0fc0b1537080767ad` |
| Builder Archiso observed | 92-1, matching approved contract |
| Frozen official repositories | 2026-11-01, core/extra |
| Private location | Owner-readable builder export and separate private candidate bundle; exact paths in handoff |

The root-only original artifact path remains inaccessible to the unprivileged
agent. Independent reads verified the exported exact bytes and both local copies,
not the protected original inode. Export/build receipts identify the original;
no new privileged read/build or permission weakening was attempted.

Actual boot structure: protective MBR, GPT and UEFI El Torito image; appended FAT
EFI filesystem with x64 fallback loader and matching live entries. Default is
`cow_spacesize=75% copytoram=n`; diagnostic and explicit RAM-copy entries are
separate. Kernel is 17,244,672 bytes and initramfs is 254,469,836 bytes. Actual
installer/provisioning entrypoints are root-owned executable 0755. Desktop,
branding, unified menu, application and maintenance payloads are present.

Broadcom: `broadcom-wl-dkms 6.30.223.271-50`, matching linux/headers
`7.2.11.arch1-1`, wl vermagic `7.2.11-arch1-1 SMP preempt mod_unload`, dependencies
cfg80211/rfkill and actual modules.dep. wl/dependencies and effective policy are
in the initramfs; the /etc policy prefers wl before bcma without a vendor-wide
blacklist. wl loaded and persisted in the virtual installed boots. The class-wide
PCI alias is not evidence of BCM4360 probe success. Broadcom and private Hyprland
license files are present; broad notice/legal completeness remains open above.

## 6. Full installation and 18-gate functional matrix

One new 24 GiB no-backing QCOW2 was created. QMP/guest inventory established the
owned serial, exact size, no partitions/signatures/mounts, and no physical or
historical disk attachment. The real installer ran in a PTY with hidden synthetic
password input, normal child umask and explicit `ERASE /dev/vda` confirmation.
Installer exit 0, five prompts answered, completion marker true, elapsed
443.045 seconds. Scoped installer/backend-log raw/hex/base64 secret scan found
zero matches. Installation produced GPT, a 1 GiB FAT32 ESP and ext4 root with
systemd-boot fallback, ordinary administrator account and no autologin.

| Gate | Result | Exact-image evidence |
| --- | --- | --- |
| 01 UEFI boot from emulated USB | PASS | Read-only usb-storage, guest USB transport and UEFI/live identity |
| 02 Live Hyprland/Dux desktop | PASS | Owning processes and inspected branded desktop frame |
| 03 Correct cowspace | PASS | Unmodified 75% option; actual 3,067,904,000-byte cowspace |
| 04 Install on new blank QCOW2 | PASS | New-disk receipt, independent guard and real PTY transcript |
| 05 Installer success | PASS | Installer exit 0 and target postconditions, not QEMU exit |
| 06 Disk-only boot | PASS | Launch contains no ISO; /dev/vda2 ext4 and no live root |
| 07 Normal greetd/PAM login | PASS | Actual prompt input/session-open evidence; wrong-password control also rejected |
| 08 Installed branding/desktop | PASS | Actual installed WS wallpaper/bar and resident shell |
| 09 Menu before lock | PASS | Super+Space, real search/navigation and WS logo pointer click |
| 10 Native Hyprlock | PASS | Authoritative native locked state, owning PID and inspected password surface |
| 11 Wrong password rejected | PASS | Exact locker PAM rejection; same lock retained |
| 12 Correct password unlock | PASS | Private password entry, native release, locker exit and original-session input recovery |
| 13 Menu after unlock | PASS | Actual keyboard query in same shell, no shell restart |
| 14 Repeated lock/unlock | PASS | Two manual native cycles plus separately observed automatic idle cycle |
| 15 Terminal, Firefox, Files | PASS | Real launches and rendered content; terminal echo command/output |
| 16 Workspaces | PASS | Real shortcuts and owning IDs 1 through 9 |
| 17 Normal reboot | PASS | User-menu confirmation, changed boot ID, fresh ordinary password login |
| 18 Clean shutdown | PASS | Ordinary user poweroffs, actual QEMU exits 0, non-repairing offline QCOW2 check 0 |

The matrix is intentionally narrower than overall release acceptance. A portal
crash on logout still fails the additional reliability requirement. Two disk-only
cold-boot lifetimes passed, and all owned live/installed QEMU processes exited.
Offline QCOW2 check verifies the container; it is not a full filesystem fsck.

## 7. Desktop, authentication, maintenance and persistence

- Firefox, Ghostty, Nautilus, Text Editor, VLC, Papers, File Roller, Calculator and
  System Monitor actually opened and rendered. VLC displayed its initial privacy
  dialog; Papers/File Roller had intentional no-document/no-archive views. Full
  playback, document rendering, codecs and physical media/audio were not claimed.
- Super+Space, WS logo click, Super+Enter, Super+Tab window cycling and workspaces
  1–9 passed. Shortcut editor rendered; its backend applied/read-back a temporary
  binding, the real key opened another terminal, and the default was restored.
- Network/sound/Bluetooth control UIs and display/software pages rendered. Virtual
  Ethernet connected, audio listed Dummy Output, Bluetooth correctly reported no
  adapter. NetworkManager and PipeWire/WirePlumber were active. Bluetooth was
  enabled but condition-skipped without hardware, not falsely called active.
- Native idle lock was observed at 182.082 seconds under the unchanged 180-second
  policy without intervening keyboard/pointer input. Actual password unlock and
  same-shell keyboard menu recovery passed. The two manual lock cycles also
  retained the same Dux MainPID with NRestarts=0.
- `wilsof version --json`, `wilsof doctor`, and `wilsof update --check` returned 0
  on installed boots. Image identity stayed 7c3771b; version is honestly a
  development snapshot, not an invented release version.
- Two actual ordinary-user `wilsof update` calls authenticated through sudo/PAM
  and completed full `pacman -Syu` as no-ops on the unchanged snapshot. No package
  versions changed; private hypridle was reported newer than the archived package.
- Native controls: unknown argument exit 2; changed repository policy and existing
  package lock refusal 78, lock preserved; valid signed identical-version patch
  reinstall 0; damaged signature refused 1; restored preflight 0. Interruption at
  sudo returned 130 without package/config changes. This is not mid-write recovery.
- Signed `tree 2.3.2-1` was installed, executed and explicitly removed in the
  disposable guest; package inventory returned to its prior state. This was root
  QA instrumentation, not proof of every graphical package-management flow.
- Seven native configuration tests passed: current-schema reapplication with
  personal settings bytes preserved, idempotence, manual backup recovery, future
  schema refusal, partial failure without marker advancement, explicit repair and
  unchanged image identity. The synthetic unknown personal JSON field is a file
  preservation probe, not a separately verified functional Dux preference.
- Four actual file SHA256 values (synthetic document, settings, configuration
  identity, managed Hyprland file) matched after normal reboot and second cold
  boot. Installed inventory was 655 packages at the preserved checkpoint.

## 8. Remaining blockers and genuine limitations

1. Reproducible portal SIGSEGV during normal logout, including clean post-reboot
   reproduction. Preserve the native crash and test a narrowly pinned correction
   before another candidate is accepted. Exact upstream C++ root cause is pending.
2. The frozen installer cannot directly replace nonblank/Btrfs Omarchy storage.
   It has no Btrfs subvolumes, encryption or automatic rollback. The new readable
   target-review fix requires a separately approved build and exact-image testing.
3. Future coherent snapshot/security version progression, changed-kernel wl rebuild,
   changed-version upgrade, mid-write interruption and full-system recovery are
   not implemented/accepted by successful frozen no-ops and file backups.
4. Broadcom's actual mitigation warning and required-notice/legal/security gates
   remain unresolved. Do not disable mitigations/signature checks or publish the
   private proprietary image as a workaround.
5. Every physical MacBook gate is NOT RUN: UEFI/USB, i915 2560x1600/scale2, keyboard,
   trackpad, actual wl binding/scans/WPA/reconnect, btusb pairing, speakers/mic,
   suspend/resume, brightness, battery and physical shutdown/reboot.
6. Owner data backup/restore is NOT RUN by design. The executed synthetic selective
   backup test does not prove a real backup or complete rollback.
7. Human independent security review and exact-head CI remain pending/missing.

The [transition procedure](../omarchy-transition.md) provides the full physical
checklist, selective backup plan, restore/recovery gates and future USB-only
sequence. It explicitly retains Omarchy and does not instruct an internal wipe.

## 9. Engineering standards and documentation delivery

Existing approved integration branch and draft PR are retained. The implementation
was test-first, focused and independently reviewed; historical work and all failed
receipts were preserved. This substantial exact-image milestone gets a committed
report/checkpoint on that same branch under Engineering Standards §12.1. Public
README, other branches, issue closure, merge and release are untouched. Reporting
uses sanitized documents and existing #60/#16/PR61 updates with exact read-back.

## 10. Model use and cost evidence

The parent session reports `openai-codex / gpt-6.1-sol`; configured delegated and
auxiliary routes were inspected as Codex with empty fallback chains. One bounded
read-only reviewer completed six API calls in approximately 49 seconds according
to the delegation receipt. The child result did not establish an exact model or
billed cost. Token/cache totals and actual invoice costs are unknown. No alternate
paid provider, provider-budget probe or unbounded worker was requested. Unknown
billing is not represented as zero.

## 11. Processes, locks, evidence and resources

One live and two disk-only QEMU lifetimes ran sequentially under the established
exclusive QA lock and finite 7200-second supervision. Ordinary user shutdowns
ended both installed lifetimes with exit 0. No forced quit, duplicate install,
physical attachment or historical installation disk was used. All guest processes
were absent before offline checking/hashing; the QA lock was independently free.
159 transferred runtime evidence entries were independently hash/size-compared.
Raw diagnostics/cores remain private and separate from the candidate bundle.

The project lock is retained through synchronous publication, then released using
its owned marker and independently probed; the final private closure receipt
records that result. Worker control remained paused. No worker/scheduler is
started for reporting. At 20:37:29 UTC local available space was 13,715,066,880
bytes; the final offline builder measurement was 34,989,834,240 bytes. Root build
lock/protected original paths remain unverified rather than claimed absent.

## 12. Next recommended engineering action

Resolve the exact frozen portal teardown failure in a bounded native-package
workstream, retaining the existing cores and a fresh normal logout/relogin
regression. Do not blindly upgrade the snapshot, suppress the crash or start a
new privileged ISO build. When the correction, notices and installer safety
changes are reviewed and natively tested, prepare a separate owner-controlled
build authorization. No owner disk action is required or permitted now.

## Publication receipt

Exact final commit, remote document comparison, issue/PR comment IDs and final
lock/process state are recorded in the private handoff after actual publication.
This report is not a merge, public release, physical test approval or daily-driver
acceptance statement.
