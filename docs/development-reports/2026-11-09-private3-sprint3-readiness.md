# Wilsof OS — Sprint 3 candidate readiness, 9 November 2026

Status: **QA/readiness milestone delivered; privileged build blocked;
Private3 NOT ACCEPTED; physical USB handoff remains NO-GO.**

Engineering period: 16:12–16:30 UTC; publication/closure checks begin 16:31 UTC.
Branch: `integration/private3-20261107`.
QA source commit: `e6c8d940c812afcc65ef5628d8ce68834c4a1cd9`.
Retained runtime/build source: `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261`.
Draft: [PR #61](https://github.com/tomli0/wilsof-os/pull/61).
Acceptance: [#60](https://github.com/tomli0/wilsof-os/issues/60);
status: [#16](https://github.com/tomli0/wilsof-os/issues/16).

## Evidence basis and scope

- Historical: [Sprint 2 report](2026-11-09-daily-driver-sprint2.md), runtime
  source 7c3771b, 756 source passes / 3 opt-in skips, native driver/update/session
  source-COW evidence. Those native results were not rerun or inherited by a
  new image. Sprint 2's reporting HEAD 0b025cb was independently matched locally
  and remotely at this session's start.
- Newly checked: retained archive/helper/closure/package identities, actual
  builder read-only check, resources/processes/accessible destinations, new
  audit tool, real historical-artifact controls, full source suite and publication.
- No privileged phase, sudo probe, new product ISO, guest boot/install, physical
  disk/USB operation, host package change, Proxmox change, merge or release.
- Private evidence label: `wilsof-sprint3-20261109T1612Z`. Raw inventories, method
  locators, owner command and machine-readable 18-row ledger remain private.
  Historical artifacts and the untracked private handoff remain preserved.

## 1. Completed milestones

**A — Refreshed conditional build preflight.** Reconfirmed exact source/archive
and reviewed helper identities; actual hash-locked owner wrapper `--check`
returned **0**, including native Archiso/private input/generated entry and
storage checks. No build was invoked. Root-only staging/receipt/marker/build
lock checks remain **NOT VERIFIED** without owner authentication, not PASS.

**B — Executable read-only provenance audit and tests.** Added
[`scripts/audit-iso.py`](../../scripts/audit-iso.py),
[`tests/test_iso_audit.py`](../../tests/test_iso_audit.py) and
[the staged acceptance/USB runbook](../private3-acceptance.md).
The tool compares every allowlisted image payload byte with the exact independent
Git commit, not just an image-supplied checksum map. It hashes ISO/SquashFS,
checks payload membership, inventories immutable package/license metadata,
performs a scoped private-path scan and rechecks unchanged image bytes.

**C — Acceptance and owner handoff prepared without counterfeit results.**
Private ledger contains exactly **18 NOT RUN** rows with empty actual evidence;
historical evidence names are explicitly templates only. Six retained method
inputs compile, but were not adapted/executed for Private3. The original reviewed
one-command owner build handoff remains executable and unchanged. No parallel
construction pipeline or duplicate privileged attempt was created.

## 2. Claude QA findings and remediation

No Claude/alternate paid reviewer was requested. One bounded independent
read-only AI source review returned **PASS**, no required security/logic fixes,
for exact staged patch
`fd0a9371e9004397dbe169cce3817987a595d7477f9c5f0aeead4da3025c67c2`.
The committed three-file patch matches that reviewed identity.

Optional suggestions: additional source/output/ancestor-symlink regression cases
and explicitly disabling Git replacement objects in the trusted analysis host.
They are recorded, not silently claimed implemented. This is not independent
human security, rootful, image, runtime or physical acceptance.

## 3. Code quality and security status

- `python3 -m pytest -q`: **777 passed / 3 explicit opt-in skips**, exit 0,
  **32.24 seconds**. This includes the **21** focused new audit tests; do not add
  focused totals to the full suite. Exact staged bytes became e6c8d94 unchanged.
- Both prescribed ShellCheck dialect sets, including the workflow's session
  wrapper, passed. Changed Python AST, three prescribed JSON files and whitespace
  checks passed. No new dependency or workflow/configuration change.
- RED/GREEN covers missing audit/reader/CLI/inventory behavior and duplicate JSON
  checksum keys. Characterization controls cover traversal, rewritten embedded
  hashes, wrong identity, changed fixture bytes, tool budget, private paths and
  refusal to overwrite evidence. Real data-only ISO/SquashFS fixtures exercise
  actual host tools; they are not bootable Wilsof candidates or product builds.
- The actual historical Private2 ISO passed the audit against source **063b7f0**:
  **62 payload files**, **787 package records**, **142,254 non-directory entries**
  in the limited filename scan. Same ISO with requested Private3 source **7c3771b**
  returned **1 / FAIL** at source identity; remaining collected static controls
  stayed separate. Both full command entrypoints executed, not just helper mocks.
- Historical ISO remains SHA256
  `9a6fd11488546193e6e85584a22ad33ff3fbb648857e3ba62383d5da7a64ae8e`;
  local tool rechecks and independent builder export hash match. No historical
  artifact was modified. Its SquashFS hash was measured as
  `329707f237546f633ac454461c7ef9497c4e0bf8679b728e61c7931b80610516`;
  this is historical-tool evidence, not a Private3 image hash.
- Audit output remains private. Filename scanning is deliberately not a full
  secret-content/security audit; package DB/license identifiers do not establish
  trusted package signatures or redistribution clearance. No image code executes.
- No signature weakening, authentication bypass, partial upgrade, stale-lock
  removal, source-pin replacement or shared signing-key distribution occurred.
  The new host-side QA files are outside the image payload allowlist.

## 4. Commits and CI status

| Commit | Role | Verified status |
| --- | --- | --- |
| `0b025cb6924fb61ab7e7d0ef3ddafcf6d8a0513c` | Actual initial reporting HEAD | Local/remote matched; only private handoff untracked. |
| `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261` | Unchanged retained runtime/build source | Git re-export matches retained approved archive; no repin. |
| `e6c8d940c812afcc65ef5628d8ce68834c4a1cd9` | Reviewed audit/tests/runbook | Pushed; exact remote HEAD and all three file bytes matched. |
| Commit containing this report/checkpoint | Reporting only | Exact final SHA/file read-back is recorded in issue/private receipts. |

At **16:31:18 UTC**, exact QA-head GitHub state: **0 check runs, 0 status
contexts, 0 workflow runs**. Combined pending with zero contexts means
**MISSING / NOT REPORTED**, not a running or successful CI test. `gh pr checks`
also reports no checks. Existing branch filters were not changed, and no manual
CI was dispatched. Final-head CI is recorded during publication read-back.

PR #61 was created and read back **OPEN/DRAFT**, head e6c8d94, base
`integration/private2-20261107` at **063b7f0**, no requested reviewers/teams,
no auto-merge, not merged. This is the scoped existing integration exception;
other PRs/branches were not retargeted or closed. Issues #16/#60 remain open.

## 5. ISO filename, size, SHA256 and location

**No Private3 ISO was produced or verified in this session.**

| Field | Actual status |
| --- | --- |
| Proposed retained filename | `wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso` — proposal only |
| Image build source | `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261` |
| Source archive SHA256 | `5e40387c8c3d7b750b418701adb5007bf61bbcb5ca00b357cae17d1dbac68e41` — newly matched, including Git re-export |
| Archiso / repository epoch | 92-1 / 2026-11-01 — unchanged native check passed |
| Target kernel / headers | 7.2.11-arch1-1 / linux and linux-headers 7.2.11.arch1-1 |
| Actual ISO bytes / SHA256 / download | Unavailable; no verified new artifact |
| Build log / exit / boot/EFI/SFS identity | NOT RUN for Private3; no invented success receipt |

Retained candidate closure hash matched the approved **814-package metadata-only**
record; full trusted-signature freeze remains mandatory before mkarchiso.
The expected kernel, headers, Broadcom, DKMS, firmware and NetworkManager rows
remain present. Retained official Broadcom archive hash matched; its license
bytes match the package and retained copy. That is input integrity, not a new
signature freeze or legal clearance.

The owner-readable completion/export directory was independently absent through
an accessible parent; no Private3 service or QEMU/build/package process was
observed. Root-only work/output/one-shot paths were **inaccessible**, not falsely
reported absent. Any unseen pre-existing root state must be reconciled by the
existing authenticated helper before it can claim its sole attempt.

Helper/wrapper identities are unchanged from the Sprint 2 review. Privileged
build requires the owner's explicit interactive decision/authentication. The
prompt was not treated as sudo approval; no sudo probe or retry was attempted.
The existing helper retains actual device/isolation checks, strict signature
freeze, unique leaves, persistent one-shot marker, QA/build locks, 2400-second
service ceiling, TasksMax4096, memory6G/swap1G and CPU quota300%.

## 6. Full installation and immutable-image results

New Private3 immutable audit, UEFI/EFI/kernel/initramfs checks, actual Broadcom
inclusion and fresh-target installation are **NOT RUN**: no new artifact exists
in the verified accessible handoff. The static utility is only a subset of the
full audit; the runbook explicitly preserves the remaining gates.

| ID | Mandatory new-image acceptance | Status |
| --- | --- | --- |
| 01 | UEFI boot from emulated USB | NOT RUN |
| 02 | Live Hyprland/Dux desktop | NOT RUN |
| 03 | Correct cowspace configuration | NOT RUN |
| 04 | Installation onto new blank virtual disk | NOT RUN |
| 05 | Successful installer exit | NOT RUN |
| 06 | Disk-only boot, no ISO | NOT RUN |
| 07 | Normal greetd/PAM password login | NOT RUN |
| 08 | Installed desktop and Wilsof branding | NOT RUN |
| 09 | Unified menu before lock | NOT RUN |
| 10 | Native Hyprlock | NOT RUN |
| 11 | Wrong password rejected | NOT RUN |
| 12 | Correct password unlock | NOT RUN |
| 13 | Menu after unlock | NOT RUN |
| 14 | Repeated lock/unlock | NOT RUN |
| 15 | Terminal, Firefox and file manager | NOT RUN |
| 16 | Workspace switching | NOT RUN |
| 17 | Normal reboot | NOT RUN |
| 18 | Clean shutdown | NOT RUN |

Resource check **16:32:56 UTC**: builder available **60,965,679,104 bytes**;
required preflight floor **26,843,545,600 bytes**; measured excess
**34,122,133,504 bytes**. Available RAM **7,479,037,952 bytes**, 4 allowed CPUs.
Local available **20,372,975,616 bytes**. These are observations, not peak-size
proof; actual privileged scope limits must still be verified in-service.
No cleanup, resize, artifact export or capacity allocation occurred.

## 7. Boot, authentication, Broadcom and update status

No new normal login, lock/unlock, update transaction or guest lifecycle was run.
Historical Sprint 2 source-COW evidence remains distinct: native wl build/load /
initramfs/reboot; real normal sudo/PAM frozen-snapshot no-op; signature/source /
lock refusals; seven configuration cases; idle lock and normal login/reboot.
Those results do not establish the new image's behavior or a changed-version
upgrade. The image-only final helper/sealing gate remains unaccepted natively.

New-image `wilsof version`, `wilsof doctor`, `wilsof update --check/update`,
configuration persistence/failure recovery and normal post-update login remain
**NOT RUN**. The runbook names actual commands and separates live-media refusal
from installed-system acceptance. No automatic or transactional rollback claim.

Physical `14e4:43a0` binding to wl, interface discovery, scans, owner-private WPA,
Internet/DNS, reconnect and reboot remain **NOT RUN**. QEMU module loading and
class-wide modalias matching cannot pass these gates. NetworkManager/firmware
new-image configuration, Secure Boot and applicable license inclusion still
require actual immutable-image inspection. Public Broadcom redistribution is
**NOT CLEARED**.

## 8. Remaining defects, blockers and daily-driver limits

1. Owner-authenticated retained build phase and real rootful/signature/resource
   gates; no duplicate build or unapproved sudo execution.
2. Exact new ISO identity and full immutable audit, then all 18 mandatory QEMU
   gates on a new blank no-backing QCOW2 disk, plus new-image driver/update gates.
3. Owner live-USB/hardware phase only after virtual acceptance; no MacBook install
   or Omarchy replacement. Preserve independent personal backups and internal
   disks. Physical display/input/audio/BT/suspend/power/recovery remain open.
4. Coherent future snapshot progression, changed-version updates, mid-write /
   power-loss recovery and configuration concurrency remain unaccepted. Existing
   file backups are manual recovery, not automatic system rollback.
5. Missing CI, independent human security and qualified proprietary redistribution
   review. Source review and a draft PR do not close any of these boundaries.

The optional audit-hardening suggestions are not ISO-build blockers and did not
justify another development loop. No new runtime product defect was confirmed.

## 9. Engineering Standards and documentation delivery

Followed CONTRIBUTING, Engineering Standards, current authorization, existing
integration/lock ownership and the reporting template. A substantive executable
QA milestone is published on the existing delivery branch with this full report;
no report-only branch/PR. Private paths, raw logs, inputs and owner authentication
remain outside public payloads. Changed-document links, sensitive content and
whitespace are checked before final reporting commit. Exact published files and
PR/issue states are read back; main/protection/release controls remain untouched.

## 10. API/model usage where documented

Main session identifies `gpt-6.1-sol` / `openai-codex`; selected stored route lines
agree. One independent reviewer inherited the requested configured route and
self-reports **6 API calls**. Exact child runtime-model/token/cache telemetry and
invoice cost are **unknown**. No alternate provider/fallback or routing change
was requested, no paid-provider budget endpoint contacted, and no zero-cost
invoice assertion is made. No review was started solely to write this report.

## 11. Processes and project locks

At **16:32:56 UTC**: no builder QEMU/build/package process, QA lock independently
available, historical localhost VNC endpoints both refused. No new guest or
rootful service was started; no forced shutdown, private mount or offline write
needed cleanup. Root build-lock availability remains unverified without root.

The finite session-owned project-lock holder remains held through Git publication
and exact read-back; final normal release/independent probe is recorded in the
issue/private closure receipt, not presumed here. Existing worker control stayed
paused and queue job disabled/paused. No scheduler/worker was started. Historical
PIDs, disks, ISOs and other agents' worktrees were not signaled or changed.

## 12. Next recommended action

The owner reviews and explicitly authorizes/authenticates the single unchanged
private build command delivered in the terminal/private handoff. It verifies
retained bytes, rechecks root-only prerequisites and makes one bounded attempt.
On failure or transport timeout, preserve/reconcile that same attempt; never
rerun blindly. After actual success, inspect exact bytes and run all 18+separate
gates. Nothing in this report starts another operation or permits physical
installation, public proprietary ISO publication, merge or release.

## Publication receipt

The exact containing report/checkpoint commit, final remote/file read-back,
PR #61 head/state, issue URLs and final process/lock/resource snapshot are stored
in the private handoff and posted to #60/#16. This avoids a self-referential
report commit loop. The report's owner action remains deliberately private.
