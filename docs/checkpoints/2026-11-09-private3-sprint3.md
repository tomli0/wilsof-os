# Private3 Sprint 3 checkpoint — 9 November 2026

Status: **NOT ACCEPTED; privileged candidate build blocked; all 18 new-image
acceptance gates NOT RUN; physical USB testing NO-GO pending those gates.**

## Exact source and artifact boundaries

- Initial local/remote reporting HEAD:
  `0b025cb6924fb61ab7e7d0ef3ddafcf6d8a0513c`.
- Unchanged retained image/runtime source:
  `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261`.
- New reviewed QA source:
  `e6c8d940c812afcc65ef5628d8ce68834c4a1cd9`.
- Branch: `integration/private3-20261107`.
- [Draft PR #61](https://github.com/tomli0/wilsof-os/pull/61), based on retained
  Private2 source `063b7f034dce7387e88f649f2c67ba95f370fcdc`. OPEN/DRAFT,
  no reviewers/teams or auto-merge requested; not merged.
- [Full 12-part report](../development-reports/2026-11-09-private3-sprint3-readiness.md).
  Exact final reporting SHA and read-back URLs are recorded in #60/#16 and the
  private handoff rather than predicted in this containing commit.

No Private3 ISO was produced or verified. The retained proposed filename
`wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso` has no actual size /
SHA256. Root-only attempt/work/output/lock state is NOT VERIFIED; accessible
owner export is absent and no active Private3 service/build/VM was observed.
The authenticated helper must reconcile root state before any single attempt.

## Newly verified

- Actual retained owner wrapper read-only check: exit0. Wrapper/helper/archive /
  approved 814-package metadata closure and Broadcom archive hashes match their
  independent prior pins; Git re-export matches the retained source archive.
  Exact package license bytes match retained copy. No signature/legal inference.
- Archiso92-1, frozen repository2026-11-01, kernel7.2.11-arch1-1 and matching
  linux/headers7.2.11.arch1-1 remain the candidate contract. Rootful receipt /
  isolation/signature freeze/resource enforcement still NOT RUN this sprint.
- New read-only [`audit-iso.py`](../../scripts/audit-iso.py), regressions and
  [acceptance/physical runbook](../private3-acceptance.md). Host-side QA only,
  outside the image payload; retained source pins were not changed.
- Full suite **777 PASS / 3 opt-in SKIP**, exit0, 32.24s. Includes21 focused audit
  checks, not additive. ShellCheck/AST/prescribed JSON/whitespace checks passed.
- Independent AI source review PASS, no required corrections, exact patch
  `fd0a9371e9004397dbe169cce3817987a595d7477f9c5f0aeead4da3025c67c2`.
  Human security/runtime/ISO acceptance remains separate.
- Actual historical Private2 positive audit:62 payload files /787 packages;
  same ISO with Private3 source expected:exit1 / source FAIL. Both preserve ISO
  bytes. These are tool controls, not Private3 immutable or runtime passes.
- Exact QA-head GitHub CI at16:31:18 UTC:0 checks /0 contexts /0 workflows:
  **MISSING**, not green. Existing workflow filters unchanged; no manual dispatch.

## Current acceptance and preservation

All18 rows are individually listed **NOT RUN** in the full report and runbook;
private matrix has empty actual evidence. New-image immutable/Broadcom/update,
physical adapter binding/scans/WPA/reconnect, Secure Boot, audio/BT/suspend,
recovery and daily-driver gates remain unaccepted. Historical Sprint2 native
source-COW results remain historical. No new guest boot or transaction occurred.

Historical Private2 ISO bytes remain hash-matched locally and on builder. No
historical disk, firmware, evidence, worktree or branch was overwritten/deleted.
No sudo probe, package/host/Proxmox/physical operation, merge or release.

Resource snapshot16:32:56 UTC: local available20,372,975,616 bytes; builder
available60,965,679,104 bytes versus26,843,545,600-byte floor (excess34,122,133,504).
Builder available RAM7,479,037,952 bytes /4 CPUs. QA lock independently available;
no QEMU/build/package process; historical VNC endpoints refused. Root build lock
is inaccessible/nonprivileged-unverified, not asserted free.

The session-owned finite project holder remains held through publication/read-back;
normal release/probe and final exact resources are recorded in the closure
comments/private receipt. Worker stayed paused and queue disabled/paused;
nothing automatically resumes. Main route is configured Codex; one read-only
review requested inherited route. Exact child model/token/invoice cost unknown;
no alternate paid provider or configuration change requested.

## One next safe action

Owner review and explicit interactive authentication of the unchanged, reviewed,
hash-locked single private-build command delivered privately. One bounded attempt
only after its actual root prerequisites pass. Preserve/reconcile any failure /
timeout; never duplicate. Then exact-byte complete immutable audit and all18+
separate gates on the genuine new image/new blank disposable disk. No physical
USB writing or MacBook installation follows automatically from this checkpoint.

Private durable evidence label: `wilsof-sprint3-20261109T1612Z`; private handoff,
owner action,18-row ledger, source logs, retained-input checks, historical controls,
review, resource/process/lock and exact publication receipts are retained there.
