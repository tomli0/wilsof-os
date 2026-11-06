# Wilsof OS — live installation capacity and USB-transport QA

Status: partial delivery; source correction tested, new ISO build BLOCKED,
physical USB-test readiness NO-GO. Date: 6 November 2026 (UTC).

Source branch: `fix/live-install-capacity-20261106`.
Implementation commit: `62999ff475bc2f194a4a8adbec6f08bca4a79910`.
Runtime-tested predecessor source: `ddfe80a7385a8d9d50ba0781205cd458777093be`.
Status thread: [issue #16](https://github.com/tomli0/wilsof-os/issues/16).

The new source and the runtime-tested ISO are different inputs. No runtime
result below is attributed to an ISO containing the new source.

## 1. Completed milestones and executive summary

- Independently verified the existing `private1-cowspace2` ISO against its
  approved SHA256 before another test, and again after shutdown.
- Completed a fresh default installation from read-only emulated USB storage,
  not CD-ROM transport: UEFI/OVMF, KVM, 4 GiB RAM, a new blank 24 GiB QCOW2 with
  a unique serial, no backing image, and no host block devices exposed.
- Tested the installed desktop, applications, password authentication,
  logout/fresh login, real reboot and normal-user poweroff.
- Implemented and tested a permanent source-level overlay policy, early
  RAM/writable-capacity refusal and scoped installation umask.
- Reproduced the post-unlock Command Center failure. It remains unresolved;
  neither a shell restart nor a fabricated unlock message was used to pass it.

A successful installation does not establish full desktop acceptance or a
USB-ready final ISO. This mission's final acceptance criteria are not met.

## 2. QA findings and remediation

No Claude or additional paid-provider review was requested. One bounded,
independent Codex-context review of implementation commit
`62999ff475bc2f194a4a8adbec6f08bca4a79910` returned APPROVE-FOR-DRAFT with no
concrete source blockers. It reported 29 focused tests passing and a scoped
whitespace check passing. Reviewed file bytes remain identical to that commit.
This is independent AI-context review, not human security or release approval.

| Finding | Root cause / observed result | Remediation and acceptance |
| --- | --- | --- |
| Live preflight ENOSPC | Wilsof omitted `cow_spacesize`; the installed mkinitcpio-archiso 73 hook defaults to `256M`. The frozen signed closure needs about 1283 MiB. | Source uses `75%` in every Linux entry and refuses inadequate actual RAM/free writable space. Source tests PASS; new-image runtime NOT TESTED. |
| QA umask contamination | A supervisor's `077` produced root-owned, untraversable target parents; `000` can instead produce world-writable parents. | Installer scopes umask `022`, restores the caller on every tested exit, and preserves explicit private directory modes. RED/GREEN filesystem regression PASS. |
| Incomplete QA receipt | Optional console-open failure can terminate the retained driver before it writes a receipt. The earlier pre-format package failure's cause remains unknown. | Private driver hardening has three fixture tests: missing console, failing writes and timeout with unknown child exit. This is not a repaired historical package-preflight failure or a new full-install pass. |
| Command Center after unlock | Native password unlock restores ordinary input, but the owning shell still returns `WILSOF_COMMAND_CENTER_LOCKED`. | Reproduced on the new USB installation. FAIL; no authentication/lock-policy workaround added. |
| Build prerequisites | Approved builder requires authenticated sudo and at least 25 GiB free. Neither prerequisite is met. | BLOCKED before build; no authentication bypass, storage cleanup or inherited-artifact overwrite. |

## 3. Code quality and security status

The implementation changes only the boot configurator, installer resource/
umask handling, focused tests and explanatory boot documentation. Repository
snapshot policy, package closure/hash/signature verification, target identity,
full-disk blankness checks, confirmation, provisioning and bootloader policy
are unchanged. Private Hyprland/Hypridle pins and package provenance are retained.

`cow_spacesize=75%` is a tmpfs ceiling, not preallocated memory. Every Linux
entry retains upstream discovery/substitution tokens and its existing speech,
diagnostics or copy-to-RAM behavior. Memtest is unchanged. Installation checks
1792 MiB writable availability, 2304 MiB `MemAvailable`, and 3584 MiB usable
`MemTotal` before package preflight or disk prompts. Nominal minimum installation
RAM is 4 GiB; lower-memory live use is not blocked by an installer-only check,
but installation below that minimum is not supported/tested here. RAM-copy
boot additionally needs the compressed rootfs. See the updated
[boot documentation](../../iso/boot/README.md).

Authentication, sudoers, SSH, firewall and hypervisor settings were not changed.
No physical disk, USB device, preserved Fedora disk, NAS or protected VM was
attached or modified. Historical ISOs and the two prior accepted installed
QCOW2 images were independently hash-checked unchanged. No claim is made of a
new forensic audit of every protected resource.

## 4. Commits, tests and CI

Implementation: `62999ff475bc2f194a4a8adbec6f08bca4a79910`.

- Ubuntu source suite: `python3 -m pytest -q` — 660 PASS, 2 SKIPPED.
- Arch builder source archive suite: `python -m pytest -q` — 660 PASS, 2 SKIPPED.
- These are separate executions of the same suite, not 1320 unique tests.
- Boot-policy, capacity/wiring and umask defects have retained failing-before
  and passing-after evidence. The new capacity file contains 25 test
  cases; the complete suite also retains existing signature and disk-safety tests.
- ShellCheck in the documented sh/bash dialects: PASS.
- Profile Python AST and the three documented JSON files: PASS.
- Staged diff whitespace check: PASS after removing a trailing blank line in
  the new test file. No implementation change followed the passing full suites.
- Separate private QA driver fixtures: 3 PASS. These are not native installs.

The two opt-in native tests remain skipped, not implicitly passed. GitHub CI
and exact published draft metadata will be recorded separately after publication;
local/Arch source tests are not ISO, native lock-security or hardware acceptance.

## 5. ISO identity, build and storage

No new ISO was built. New ISO filename, size, SHA256, build timestamp, package
manifest and final embedded EFI image: NOT AVAILABLE / NOT TESTED.

Existing runtime-tested artifact:

- `wilsof-internal-2026.11.06-private1-cowspace2-x86_64.iso`
- Size: 2603745280 bytes.
- SHA256: `7eb5b3807d7f3c1de99ac98a84a57a8af903a10419b8b1e15e6bc14ab4c0df2d`.
- Original source provenance: `ddfe80a7385a8d9d50ba0781205cd458777093be`.
- This predecessor is a boot-configuration derivative, not a source rebuild.

Original ISO remains unchanged at SHA256
`fd6b0510bae464b8d72173b57ee71e8c098c9e006e3bf62bf32c912ea96058f0`.
Its default 256 MiB installation failure is historical evidence, not rerun here.
The corrected predecessor's USB installation used automatic 2 GiB cowspace,
without a remount. That does not validate the new source's 75% image policy.

Builder inspection at 18:44:00 UTC: Archiso `92-1`, free space 9828319232 bytes,
approved minimum 26843545600 bytes, shortfall 17015226368 bytes. Noninteractive
sudo explicitly requires a password. A clean source archive was staged and
independently verified, not built:
`6fce1c7204375326f226fd81d1736e19dab9802cb978476da5ac7796c1bc89c6`.
No old build directory or artifact was removed to evade the storage gate.

The new generated loader entries pass real Archiso 91/92 fixture tests; checking
both the ISO-tree entries and embedded EFI FAT on a newly built final ISO remains
mandatory and NOT TESTED. A predecessor's EFI/boot pass is not transferred.

## 6. Complete QEMU installation result

PASS on the exact existing corrected predecessor:

- New blank 24 GiB virtual target, unique serial, UEFI/OVMF and KVM verified.
- Only the disposable target and read-only emulated USB ISO were exposed.
- Actual USB transport and live read-only medium confirmed in the guest.
- Normal PTY installer, five of five prompts, password echo disabled.
- Signed/hash-verified package preflight completed with no manual cowspace fix.
- GPT, 1 GiB FAT ESP, ext4 root, user provisioning and boot assets verified.
- Installer exit 0, completion marker, elapsed 370.230530681 seconds.
- Root account locked; password-provisioned normal user; no autologin.
- Target unmounted cleanly before live guest poweroff.

Both QEMU lifetimes ended with exit 0. QEMU exit is recorded separately from
the installer's own exit. Final offline QCOW2 check: zero check errors.

## 7. Installed desktop, login and lifecycle

PASS unless otherwise stated:

- Booted the installed ext4 root without ISO or Archiso live mount.
- Actual greetd username/password login and PAM session-open evidence.
- Hyprland/Dux/Wilsof target, wallpaper and CLEAN top bar rendered.
- Super+Space opened Command Center; typed search produced owning results.
- Super+Enter launched Ghostty; typed `whoami` displayed the normal user.
- Super+B launched Firefox; a local QA page rendered and responded to keyboard
  activation. This is not a certificate/network-browser compatibility test.
- Super+E launched Nautilus; keyboard navigation reached the requested directory.
- Super+2 and Super+1 changed and restored workspaces.
- Super+L acquired a native lock; an independent second lock request was denied.
- Deliberately incorrect password rejected; correct private password restored
  the original session and ordinary terminal input without killing the locker.
- FAIL: Command Center stayed LOCKED after that real unlock, same Dux lifetime.
- The actual generated Super+Shift+E binding logged out; fresh password login
  restored a new working desktop/Command Center.
- Normal-user `systemctl reboot` caused a real guest reboot in the same QEMU
  process; boot ID changed, greeter returned, password login/desktop worked again.
- Normal-user `systemctl poweroff` ended the owned QEMU process cleanly.

PAM logs contain the wrong-password rejection. No separate exact locker
success message was present: a broad grep matched the diagnostic command text
and was explicitly discarded as success-log evidence. Correct-password input,
native unlock, locker exit and original-session input recovery were observed
independently; no fabricated PAM success log is claimed.

## 8. Remaining defects and limitations

The post-unlock shell-state defect is still a release/test-readiness blocker.
The frozen lock wrapper deliberately withholds an unverified asynchronous
unlock bridge. This PR does not change that security boundary.

Scoped pre-auth ordinary-client isolation passed a positive control, locked
activation attempt and harmless sentinel with zero new ordinary input before
credentials. Complete-interval certification is INCONCLUSIVE: a focus-enter
was recorded about 1.1 ms before the idle daemon's unlock callback log receipt.
That receipt timestamp is not an authoritative compositor-release boundary.
The raw evidence is retained; it is neither hidden nor called a reproduced
password leak. No all-client security certification is claimed.

No failed system/user units, Dux restarts or coredumps were found in the checked
installed boots. Retained warnings include missing RTKit/BlueZ service support,
a desktop-only UPower warning and a first-use recent-files database warning;
these are not a claim of warning-free startup or tested physical audio/Bluetooth.

Physical USB/firmware/GPU/Wi-Fi/audio/Bluetooth/suspend, a physical client,
low-memory hardware and automatic 180/300-second idle timing are NOT TESTED.
The old pre-format package failure remains causally unresolved; a better QA
receipt mechanism does not retrospectively identify its cause.

## 9. Standards and delivery boundary

This report belongs to the actual correction branch, not a report-only branch.
Any PR is to remain draft. No ready-for-review transition, automatic merge,
force push, history rewrite, release or public artifact publication is authorized
or performed. Issue #16 remains open. Private packages, raw journals, screenshots,
QCOW2/firmware and synthetic credentials are not public attachments.

## 10. Model usage

The session uses the configured Codex OAuth route; stored billing mode is
`subscription_included`. No provider switch or paid fallback was requested.
The one source-review child's stored session metadata independently confirms
`gpt-6.1-sol`, `openai-codex`, `subscription_included` and six API calls. Its
billed-actual field is null, not a measured zero invoice.

## 11. Processes, locks and private evidence

Owned live and installed QEMU processes are stopped. The QA lock was probed
available after exit; the main session lock remains held until reporting closes.
Existing project worker controls remain paused; no scheduler or autonomous
worker was started.

Private checkpoint logical name: `wilsof-usb-stabilization-20261106T1810Z`.
It retains the machine-readable matrix, source/RED/GREEN logs, complete native
trace/adjudication, install/session archives, screenshots, new disk/firmware
identities and preservation receipts. Absolute private paths are supplied only
to the owner, outside this public report. Exported archive members were scanned
for the private test password with no matches; this is not forensic erasure.

## 12. Decision and next safe action

NO-GO for a stable USB-test candidate or full mission completion. The strongest
verified artifact remains the unchanged corrected predecessor, with successful
USB-transport installation but a known post-unlock integration failure.

Next delivery gate: resolve the authenticated builder/storage prerequisites
without sacrificing preserved artifacts, complete a reviewed native unlock-to-
shell-state correction, then build a new uniquely versioned private ISO and run
all acceptance gates on those exact bytes. Neither the source suite nor this
predecessor's runtime results replace that final-image test.
