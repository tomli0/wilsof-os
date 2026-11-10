# Wilsof OS — maintenance and consolidation, 10 November 2026

## Current autonomous continuation — 12:34 UTC

**Verified source/maintenance delivery; Daily Driver RC remains BLOCKED. Keep Omarchy.**
This continuation starts from the exact previous delivery
`6eedb073c0e423cf8324d0a2766f39a0468e7249` on the unchanged authorized branch.
Implementation `e885c81585b62399d6d334c8b19cb68c5c58ab35` is pushed; all five
changed remote blobs were independently byte-read back. No main merge, branch
retirement, public ISO release, physical write or new privileged ISO build.

### Newly executed storage work

- Seven previously deferred generated intermediates were independently matched
  against members of three hash-pinned retained historical ISOs. Exact reviewed
  paths/inodes, single links, no-symlink ancestors, successful build provenance,
  backing catalogs, active-process/mount checks, trusted initial-host identity,
  existing locks and an exclusive write-ahead audit preceded file-only unlink.
- Actual historical allocation unlinked: **3,508,752,384 bytes / 7 files**.
  Actual available-space increase across that apply: **3,508,719,616 bytes**.
  No recursive deletion, backing/installed disk, credential, signing material,
  source/WIP, current candidate, ISO or unresolved failure evidence was removed.
- Independent root read-back finds START/7 INTENT/7 REMOVED/COMPLETE;
  **587,178 original non-target Wilsof paths have zero unexpected metadata/removal
  changes**. All **22 non-pytest local ISO paths** match their initial hashes.
  Pytest independently pruned six earlier tiny scratch fixture ISOs; this is not
  product-ISO cleanup or evidence that protected images were deleted.
- Full Hermes-home inventory: **1,042,619 paths**, 47 extension-candidate images
  (including intentionally invalid test disks and unrelated raw text) and 28 ISO
  paths including fixtures. Actual retained Wilsof backing catalog is 31 QCOW
  entries plus two standalone evidence raw files. All remain preserved.
- Fresh accessible builder inventory: **66,454 paths**, 20 disk/raw entries and
  15 hashed ISO exports. Root-only build storage remains UNKNOWN, not absent.
  All existing historical/backing/acceptance disks stay retained; none is made
  disposable merely because its test once passed.
- **VM112 bytes reclaimed: 0.** All 2,180 earlier duplicate-cache target identities
  still match; 4,447,215,616 allocated bytes remain candidates, NOT reclaimed space.
  A newly frozen owner helper passes actual read-only checks, embedded compilation
  and wrong-source-hash refusal. Normal owner sudo and complete authenticated
  catalog/process preflight remain unexecuted. It authorizes no build or resize.
- At **12:34:23 UTC**, Hermes has **22,060,797,952 available bytes**. At
  **12:22:40 UTC**, builder has **12,891,496,448 available bytes**: short by
  **13,952,049,152 bytes** of the unchanged 25-GiB floor and **19,320,758,272 bytes**
  of the preferred 30-GiB margin. Even optimistic cache recovery alone leaves
  9,504,833,536 / 14,873,542,656 bytes short. No capacity change is executed.

### Engineering, source tests and assessment

The new host-only `scripts/qa-retention.py` registers private explicit manifests
before allocation, retains failure/timeout/pending outputs, binds passed checks to
retained evidence and input pins, then produces bounded read-only maintenance plans.
Only declared disposable outputs of the exact run are eligible. The helper never
applies, manufactures approval or auto-retires installed reference disks. The
normal producer integration is in [artifact maintenance](../artifact-maintenance.md).

A real host-only lifecycle fixture used actual CLI registration/finalization and
normal authenticated exact-plan apply to remove one newly created **2,097,152-byte
raw file**, preserving its independent seed and evidence. Its root COMPLETE audit
was read back. This small newly generated fixture is separate from historical
storage recovery, not QEMU/installer/ISO acceptance. Its successful native path
predates the final cancellation-only correction; final source has actual CLI and
process-control regression evidence, not a newly claimed full native guest run.

Three concrete safety findings were reproduced before correction:

1. A cached proof could follow a substituted symlink ancestor despite matching inode
   and bytes. Cached proofs now traverse parents through no-follow directory FDs.
2. Normal TERM/HUP could bypass the separate planner group's cleanup. Real CLI RED
   demonstrated live descendants. An initial InterruptedError handler was swallowed
   by selectors; the same selector seam in the existing maintenance engine also
   reproduced unsafe continuation. SystemExit now unwinds cancellation/audit paths.
3. Planner pipe completion did not prove a redirected TERM-resistant proof reader
   exited. A real redirected-stdio RED reproduced the survivor. Cleanup now escalates
   and independently verifies the owned process group, including that case.

Receipts now fsync file and parent; JSON is size-checked before reading through the
same safely opened descriptor. Repeated cancellation signals cannot interrupt the
bounded stop, and original handlers are restored. SIGKILL/host loss remains an
explicit reconciliation boundary, not an unconditional cleanup guarantee.

Final local regression: **920 PASS / 3 explicit native opt-in SKIP**.
Focused lifecycle: **57 PASS**, included in that total, not additive. Exact
implementation [CI 42816600030](https://github.com/tomli0/wilsof-os/actions/runs/42816600030)
**SUCCESS / 920 PASS / 3 SKIP**, exact checkout and logs independently read back.
Python 3.12 grammar, both separately recorded ShellCheck groups, CI JSON,
whitespace/security scan and strict Git fsck pass. One intermediate full run
exposed an ESRCH race in a process-exit test oracle; its failure is retained and
its corrected exited-process handling passes. No product result was fabricated.

Three bounded separate-context AI assessments/two correction cycles were used.
The final targeted lifetime re-verification passes exact final diff SHA256
`6cf01fca69c291205d6ff2017a69cb04eb611d2db1479bfa0a0defb13dba7db4`.
Earlier reviewed boundaries remain scoped accordingly. This is not human independent
security certification. The normal-exit/redirected-survivor branch was source-inspected
but has no separately claimed direct positive test. No alternate paid route or
scheduler was activated; actual billed child model/cost is not independently known.

### Portal trust and release gates

The retained real portal archive and ELF match their independent expected hashes.
Offline inspection verifies 21 unique safe members, eight MTREE file hashes,
15 declared dependencies present in its retained BUILDINFO environment, four
provenance files and no install script. ELF NEEDED entries are recorded; this is
not a future-closure loader/runtime pass. Current portal trust regressions pass.
A canonical-filename unsigned signing input is privately staged and rehashed.

The inspected builder public keyring contains 183 primary identities and no Wilsof
UID; the inspected owner key stores have no public/secret objects. **No independently
approved production signer was established**; inaccessible owner workstations are
not assessed. No test identity signs the real portal, no production key is generated
or enrolled, and signature/approval remain absent. Exact custodian/fingerprint and
public enrollment scope are requested, never self-authorized.

Source export `e885c81585b62399d6d334c8b19cb68c5c58ab35` has 355 regular files,
14,612,480 bytes, SHA256
`224cd669d87f13596f732d6544557ec0e85548f0eddc6ea9c619b60a447f613c`;
independent Git archive bytes match. **This is source, not an ISO.** Shipped runtime,
installer, configuration and packaging remain unchanged from `fc0f60e`.

No new production signed-package consumer or five signed-package cycles pass;
no compatible coherent future OS progression is accepted. The frozen baseline and
existing incompatibility evidence remain, rather than a partial upgrade. No new ISO
exists and all 18 exact-new-image gates remain NOT RUN. The preserved historical
Private3 ISO remains 2,813,849,600 bytes / SHA256
`111c06b70cf6d909b3e815975f69bfa18f299af9dcfe9bbbfd5e197992c53a59`,
with the original portal crash; its 18 historical basic passes do not accept a new RC.

No additional PR/issue closures or branch deletions were performed. The seven open
PRs, 18 unresolved issues and 46 retained branches are preserved; #16 remains the
canonical status, #60 acceptance, #61 OPEN/DRAFT with retained Private2 base.
The existing [MacBook handoff](../omarchy-transition.md) remains non-destructive:
all physical hardware, independent backup/restore and physical replacement gates
are NOT RUN. Complete RC SOURCE READY is not declared; SIGNED PACKAGE ACCEPTED,
ISO BUILT/VERIFIED, VIRTUAL ACCEPTED, READY FOR PHYSICAL TEST and READY TO REPLACE
OMARCHY are **not achieved**.

Private checkpoint group: `wilsof-rc-completion-20261110T1142Z` contains classifications,
original inventories, exact policies/plans, root audits, verification, source/CI,
capacity and narrow signing requests, and one consolidated OWNER_ACTION. The normal
owner action covers one storage sudo phase and independent production signing
approval; capacity and a fresh exact build authorization remain subsequent gates.
No honest new ISO command is supplied while those inputs are missing. Never reuse
the consumed old-image helper. Root-only originals and lack of an authorized
archive destination are disclosed, not bypassed.

## Historical first maintenance milestone — unchanged scope below

Status: maintenance implementation delivered; verified local cleanup complete.
Daily Driver remains BLOCKED. No new ISO, production trust approval, physical
installation, infrastructure change, merge or release.

Work began 09:26 UTC. Final storage checkpoint: 2026-11-10T11:03:15.410209+00:00.
Implementation: `d8876dd70d66faf6d0c7c52af33b05e2458c6c3f`, existing branch
`integration/private3-20261107`, [draft PR #61](https://github.com/tomli0/wilsof-os/pull/61).
[Issue #16](https://github.com/tomli0/wilsof-os/issues/16) is the authoritative live
status; [#60](https://github.com/tomli0/wilsof-os/issues/60) owns current acceptance.

## Evidence and scope

The starting local/remote HEAD was independently verified as
`3af4564f836e79e3d87e3b8a7f8885a7c3aa394f`, rather than assuming the abbreviated
identifier in the request was a valid full commit. Inventory covered 588,541
Hermes paths and 66,421 builder paths, filesystem use, processes, mounts, locks,
31 known ISO paths including fixtures, and 53 virtual disk files/backing chains.
Guest filesystem figures are not Proxmox pool/backup capacity claims.

Private evidence is retained in the maintenance checkpoint: exact original file
metadata, classified inventories, explicit policies/targets, plans, root-owned
write-ahead audits, independent preservation comparisons and GitHub receipts.
Full paths, raw logs, credentials and private package material are not published.

## 1. Completed milestones

- Standalone standard-library host maintenance CLI; default inventory is read-only.
- Actual file-only cleanup: **1,390 files / 5,214,322,688 allocated bytes**. This
  comprises 632 regenerated package-payload staging files and 758 duplicate
  per-build package-cache copies. Actual bytes were independently matched against
  retained package copies or pinned SquashFS contents, whose bytes were separately
  verified inside retained historical ISOs.
- All 34 registered source worktrees preserved; only the authorized delivery
  branch advanced. Uncommitted work in other worktrees was not changed.
- Ten obsolete drafts closed as superseded, not merged. All branches retained.
- One active [Daily Driver milestone](https://github.com/tomli0/wilsof-os/milestone/1)
  with 15 existing acceptance issues; no new duplicate issue.
- Permanent close-out responsibility added to project instructions, engineering
  standards and contributing guide. README now describes the actual candidate;
  the old status document is a pointer, not another competing dashboard.

## 2. QA findings and corrections

No Claude review or professional independent security certification was obtained.
Two bounded separate-context AI assessments were used because this code unlinks
real files. The first found two concrete blockers; no deletion preceded correction.

| Finding | Severity | Correction and observed evidence |
| --- | --- | --- |
| F1: filtered procfs enumeration could falsely clear strict visibility | High | Externally pinned host boot/PID/user/proc identity, root/capability/initial-namespace/unfiltered-proc requirements, before writes. RED reproduced; fixed regression passes. |
| F2: maps path comparison missed alternate-mount aliases | Medium | Compare parsed device/inode, not pathname. RED reproduced; alias-path regression passes. |

Second bounded changed-boundary review: PASS, three targeted tests passed and
27 deselected. Full focused suite: **30 passed**. This is not full production or
human security approval. Trusted identity input, complete image catalogs and
cooperating workflow locks remain prerequisites; observational process checks
are not protection against hostile same-owner/root ancestor renames.

Reviewed source SHA256:
`997b20706a1b7f93099bdd089fac5c7f01d49d3f5d60fa351ebbe5ff64f37b60`.
Reviewed test SHA256:
`2051d327acbaf3734d3db5d28dc0f1557bdd1a1bdcd60bdcd2bfc7c329ffa0ac`.
Real privileged initial-host positive, wrong-host rejection and bounded nested
namespace rejection controls passed; the second assessor did not independently
rerun those native controls.

## 3. Code quality and cleanup safety

[Tool and policy procedure](../artifact-maintenance.md) documents explicit roots,
classifications, protected prefixes/pins, successful workflow state, retained
proofs, locks, complete image catalogs, host identity, exact policy/plan hashes
and exact target selection. Apply refuses changed/ambiguous identities, symlink
ancestors, hardlinks, source repositories, required backing parents, unavailable
process visibility and missing proof. Unlinks are relative to verified parent
FDs, never recursive tree removal. Archive verification streams actual ISO or
SquashFS members without extracting into the host tree.

Actual first apply reached its 360-second terminal limit after 362 completed
unlinks; durable INTENT/REMOVED counts matched exactly and ABORTED was recorded.
An ordinary-user audit-child existence check was initially misread as absence:
root-created audit directories are private. Authenticated root read-back corrected
that interpretation before any retry. All pins/chains and original non-target
metadata were independently verified, then a NEW plan approved only the remaining
1,028 targets. A finite 1,200-second supervised continuation exited 0 with a
COMPLETE receipt. Scoped image roots were accepted only after their full resulting
catalog exactly matched the retained broad discovery.

A newly created administrative QA lock was returned to the owning workflow user
under its exact inode and an exclusive lock; no pre-existing lock was replaced or
changed. Both local ordinary-user lock probes pass. Root-only audits remain
root-only; inspect through normal authorized authentication, not false absence.

An additional read-only preparation for seven generated intermediates timed out.
It produced no approved plan or deletion; those **3,508,752,384 allocated bytes
remain retained**, and no repeated attempt was made.

## 4. Commits, tests, CI and GitHub consolidation

- Baseline: 863 passed / 3 explicit native opt-in skips.
- Final local full suite: **893 passed / 3 skipped**.
- Exact implementation [CI 42799168482](https://github.com/tomli0/wilsof-os/actions/runs/42799168482):
  **SUCCESS, 893 passed / 3 skipped**. Logs and exact head were read back.
- Python 3.12 grammar, both prescribed ShellCheck groups, Git strict fsck,
  whitespace and scoped static checks pass. Documentation Markdownlint passes
  with the existing long-line rule MD013 explicitly excluded.
- All nine implementation/document blobs fetched from GitHub at the exact
  implementation SHA and byte-compared. This follow-up report changes documentation,
  not the reviewed maintenance source or shipped runtime.

Superseded drafts closed: **#32, #48, #49, #50, #51, #54, #56, #57, #58, #59**.
Seven source heads are exact ancestors of the retained successor. #48/#49
implementation preservation was independently checked with stable patch
comparison; unmatched documentation remains on unchanged original branches.
The README-only #32 is superseded by the delivered current candidate README.
Closures were individually read back as closed/unmerged with unchanged head/base.
All child base refs remain usable; no branch was deleted or force-pushed.

Open PR count: **17 → 7**. Current delivery #61 remains OPEN/DRAFT with its original
Private2 base. #33/#38/#39/#40 are explicitly parked historical workstreams with
unique requirements/history retained. #20/#26 retain independent unfinished work;
no worker/reviewer was activated. Open issues: **18 → 18**; none had all remaining
acceptance independently met, so no unresolved issue was closed.
Branches: **46 → 46**; tags/releases remain untouched.

## 5. ISO identities and protected artifacts

No new ISO was built or approved. All 31 inventoried ISO path hashes, including
small fixtures, are unchanged. Local independent verification also matched all
18 policy pins and all 33 virtual disk chains; builder verification matched
15 ISO paths and all 20 virtual disk chains. Non-target metadata comparisons found
zero unexpected removals or changes across the recorded inventories.

| Retained artifact | Actual identity and status |
| --- | --- |
| Accepted reference: `wilsof-internal-2026.11.07-private2-recovery1-x86_64.iso` | SHA256 `9a6fd11488546193e6e85584a22ad33ff3fbb648857e3ba62383d5da7a64ae8e`; preserved |
| Current retained candidate: `wilsof-internal-2026.11.09-private3-sprint2-wl1-x86_64.iso` | 2,813,849,600 bytes; SHA256 `111c06b70cf6d909b3e815975f69bfa18f299af9dcfe9bbbfd5e197992c53a59`; frozen image source `7c3771b3c2c4b2ef05477f09bab8f0f3baa10261`; original portal crash remains |

All necessary backing images/firmware, installed acceptance disks, unresolved
failure evidence, source/WIP, signing material, credentials, shared stores and
existing custody archives remain. NAS media, Proxmox backups, protected snapshots,
Fedora historical storage and VM113 were outside the deletion roots and untouched.
Inaccessible root-only builder originals were not independently rehashed; their
visible verified exports were. Inaccessibility is not absence or disposal authority.

New artifacts archived off-host: **0**. No accessible existing authorized NAS
archive destination was verified. Existing same-filesystem archives and earlier
owner-attested separate-PC custody remain preserved; neither is a newly verified
NAS transfer in this task.

## 6. Storage and installation results

| Guest filesystem | Used before | Used after | Available before | Available after |
| --- | ---: | ---: | ---: | ---: |
| Hermes | 186,441,322,496 | 181,263,712,256 | 13,442,420,736 | 18,620,030,976 |
| Builder | 146,844,639,232 | 146,851,205,120 | 12,906,987,520 | 12,900,421,632 |

All figures are bytes. Hermes checkpoint time: 2026-11-10T11:03:15.410209+00:00.
Builder checkpoint time: 2026-11-10T10:52:33.447125+00:00.

Actual allocated file bytes unlinked: **5,214,322,688**
(4.856 GiB), all link-count-one files.
Measured available-space increases across the two actual apply windows total
**5,205,020,672 bytes**; start-to-final available-space increase is
**5,177,610,240 bytes** (4.822 GiB). New audit/manifests/logs and unrelated
filesystem writers explain why net space is not the allocation sum. These are
real execution measurements, not a dry-run claim.

Builder reclaimed space: **0**. Its **2,180** duplicate-cache candidates total
**4,447,215,616 allocated bytes**, but remain unexecuted pending normal owner sudo
authentication and strict root preflight. Their verified retention classification
is UNKNOWN-for-execution until that gate; duplicate bytes alone do not prove idle.
The separate exact-policy owner helper passes its actual read-only check and
embedded-code syntax check. Its privileged execution is NOT RUN.

Both guests still have less than the documented 25-GiB build floor. Builder gap:
**13,943,123,968 bytes**. Even the prepared cache
cleanup would not alone establish build capacity. No deletion was expanded merely
to hit a target, and no storage resize or reserve adjustment occurred.

Full installation, new-image boot, normal login, native signed production package
acceptance and physical testing were **NOT RUN**. The two pruned legacy unpacked
build roots are **NOT READY for chroot/build reuse**, despite retained DB/configs;
rematerialize exact inputs into a new unique workspace rather than resuming them.

## 7. Boot, authentication and runtime boundaries

No QEMU guest, installer, package transaction, new rootful ISO build, physical
write, service power action or production trust enrollment was started. The
production runtime, installer, image payload, packaging and configuration bytes
are unchanged from the previously tested `fc0f60ee21c15fe8fca4f19cde9a4c42f666fa20`.
Existing native and image results keep their original identities; none is rerun
or transferred to a nonexistent new image for presentation.

## 8. Remaining Daily Driver and storage blockers

1. Owner-authenticated production signing identity/custody/public enrollment.
   Retained real portal archive SHA256
   `d3d2dba441324ed467574ea27f5d2432f7f10cf851e1cc46aaf73bed2d8e7fd0`
   is unchanged and its detached signature remains absent.
2. Native production signed-package consumers and five genuine portal cycles.
3. Coherent future private compositor/library/Dux/portal/kernel/header/driver
   update closure and recovery; prior incompatible SONAME result is retained.
4. New explicitly authorized source-pinned ISO after privilege, input and capacity
   gates; no old consumed build helper may be reused.
5. Complete exact-new-image virtual/security/notice/license acceptance.
6. Physical MacBook hardware, independent owner backup/restore and replacement.

Storage blockers: builder root-only build state is still UNKNOWN without normal
authentication; guest capacity remains below the build floor; no verified archive
access exists. The deferred seven local intermediates, unmanifested legacy trees,
protected historical disks/ISOs/custody archives, shared Docker/dependency stores
and owner/Hermes backups were not pruned by age or guessed ownership.

## 9. Permanent lifecycle and proposed branch retirement

The [artifact lifecycle](../artifact-maintenance.md), project instructions,
contributing guide and Engineering Standards now require unique workflow roots,
explicit retention manifests, bounded QEMU ownership, preservation of unresolved
failures, exact approved cleanup, reuse of unchanged evidence and storage/branch/
blocker reporting. No unattended cleanup service or scheduler was enabled.
Older producers without explicit manifests are not retrospectively declared safe;
this task demonstrates derived exact manifests and real cleanup, not blanket
conversion of every historical private harness.

**Proposed owner review only: 15 branch names. No deletion authorized or executed.**
Each has retained ancestry, but registered worktrees, active references, archival
coverage and the owner's exact per-branch approval must be resolved first.
Rejected security-experiment references are deliberately excluded.

| Proposed branch | Preserved ancestry | Registered worktree |
| --- | --- | --- |
| `docs/main-first-workflow-20261103` | main | No registered worktree observed; other gates still required |
| `feat/accept-completion-20261031` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `feat/archiso92-snapshot-20261104` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `feat/command-center-20261031` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `feat/integration-20261101` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `feat/modern-terminal-20261031` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `fix/as02-private-package-contract-20261103` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `fix/integration3-pi-remediation-20261102` | integration/private3-20261107 | No registered worktree observed; other gates still required |
| `fix/internal4-completion` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `fix/live-install-capacity-20261106` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `fix/native-command-center-lock-20261106` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `integration/integration3-20261102` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `integration/integration3-main-20261103` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `integration/internal3-20261030` | integration/private3-20261107 | Yes — retire/detach only with separate approval |
| `stabilization/internal4-20261030` | integration/private3-20261107 | Yes — retire/detach only with separate approval |

## 10. API/model resource accounting

Main session route is the supplied `gpt-6.1-sol` / `openai-codex` context. Two
bounded source reviews were justified for deletion safety. Exact child model,
tokens and billed cost are not independently established; no zero invoice is
claimed. No alternative paid provider/fallback was configured or quota workaround
started. GitHub mutations have durable per-operation receipts and exact read-back.
No scheduler/queue was restarted; no additional product milestone was started at
the unresolved trust/privilege gate.

## 11. Processes, locks and preservation

Both owned cleanup lifetimes are stopped; the continuation exited 0. The original
project holder was released through its verified marker and its PID is absent.
Project/local QA locks pass ordinary-user nonblocking probes; builder QA lock
passes its nonblocking probe. No owned build/test/QEMU process remains. Existing
unrelated host services and older forwarders were not killed by guessed ownership.
Worker remains paused and its queue disabled/paused. Root-only build-lock state
was not falsely certified without access. No mount or namespace was left by this
cleanup. All original recorded non-target paths remain intact.

## 12. Exact next owner actions

For storage only, run the prepared private owner helper with `--execute` from a
normal terminal. It checks exact frozen tool/policy/plan/2,180 target identities,
acquires the project lock and invokes one bounded builder sudo cleanup; enter
credentials only at sudo's own prompt. It cannot start an ISO, sign packages,
alter infrastructure, delete a branch or resume automation. The private checkpoint
contains the exact command; root audit/result read-back is required afterward.

For productive Daily Driver continuation, independently authenticate/approve the
exact production primary OpenPGP fingerprint, protected private-key custodian and
narrow isolated public enrollment scope for the retained portal, following
[package signing](../package-signing.md). Return only public certificate,
detached signature and explicit approval inputs—never a private key/passphrase.
Then verify native production consumers and coherent update/capacity gates before
a separately approved new build. **Keep Omarchy intact. Nothing resumes automatically.**
