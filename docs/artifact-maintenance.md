# Wilsof artifact maintenance

## Ownership and lifecycle

Hermes owns the end-of-session storage lifecycle:

Develop → Test → Deliver → Preserve essential evidence → Clean up → Continue.

This is part of normal sprint completion, not an unattended service. No timer,
cron job, queue restart, automatic signing approval or privileged ISO build is
created by this procedure. Routine status goes on the existing project issue;
unchanged state does not need another report archive or report-only branch.

The authoritative current project dashboard is
[issue #16](https://github.com/tomli0/wilsof-os/issues/16).
[Issue #60](https://github.com/tomli0/wilsof-os/issues/60) tracks the remaining
Daily Driver acceptance gates, not a second general status history.

## Retention rules

| Class | Rule |
| --- | --- |
| ACTIVE | A process, mount, lock or ongoing workflow owns it; never remove. |
| PROTECTED | Accepted reference/current candidate ISO, necessary backing image, pinned baseline, source/WIP, signing material, credentials, user data, shared dependency store or protected backup; never remove. |
| ARCHIVE | Unique completed evidence suitable for an existing authorized archive; retain locally until verified transfer and an explicit retention decision. |
| DISPOSABLE | Explicit completed successful workflow manifest, no pending acceptance, known identity, retained reconstruction/duplicate proof, no owner or dependent backing chain. |
| UNKNOWN | Missing identity, permissions, ownership, provenance or dependency evidence; retain. |

Age is not a classification. A successful fixture may be disposable; a failed
fixture is not disposable while its unique failure evidence is needed. Keep
small sanitized receipts, exact inputs/hashes, exit codes and the minimal
reproducer for unresolved defects. Raw credentials, journals and cores stay
private. Source history belongs in Git; do not make another full source archive
unless a real custody/build input requires it. Preserve uncommitted work.

Keep the accepted reference ISO, current candidate and any older image still
referenced by unresolved bugs or a pinned acceptance baseline. Old *unreferenced
copies* may become candidates only after an explicit per-copy decision; ISO age
or a successful newer build is not permission to remove them. Do not rotate
images by a numeric count alone. Package signatures and production trust are
never disposable test output.

For important archives, verify an already authorized destination's identity and
capacity, use a new collision-safe private path, independently compare SHA256
manifests, and remove originals only when policy permits. A second directory on
the same filesystem is not off-host archival. No NAS access, new mount,
credential enrollment or backup pruning is implied.

## Host-only CLI

Run with the Python standard library; no application installation is needed:

    python3 scripts/artifact-maintenance.py --policy /private/run/retention.json
    python3 scripts/artifact-maintenance.py --policy /private/run/retention.json plan

Both commands are read-only. Inventory reports exact metadata and allocated
blocks; it does not infer disposability. Unlisted files stay UNKNOWN, and
protected prefixes/pins override a manifest label. Plans refuse ambiguous
candidates rather than silently weakening a guard.

The version-1 policy is a private JSON object with these fields:

- `roots`: exact, narrow, canonical absolute Wilsof-owned deletion roots.
- `protected`: canonical paths/prefixes that must survive.
- `pins`: objects containing a retained `path` and independently expected `sha256`.
- `image_roots`: complete existing image-catalog roots, including historical and
  stopped guests that may depend on any proposed target. These can extend beyond
  deletion roots; nothing there is implicitly disposable.
- `host_identity`: independently recorded trusted host `boot_id`,
  `pid_namespace_inode`, `user_namespace_inode` and `proc_device`. Destructive
  execution requires an exact match, authenticated UID 0, full initial UID mapping,
  CAP_SYS_PTRACE/CAP_SYS_ADMIN, matching caller/PID1 namespaces, initial-namespace
  parent checks and an unfiltered host procfs mount. Missing pins, nested or masked
  procfs and unsupported visibility contexts fail closed before lock-file writes.
  Do not manufacture this trust assertion from an unverified container's own view.
- `locks`: the existing project/QA locks and any owning workflow lock. All writers
  must cooperate with those same locks. Do not invent a new lock instead of the
  established one. Before administrative apply, verify/precreate required workflow
  locks under their correct workflow owner; do not leave a new root-owned lock in
  an ordinary user's QA workflow. Never replace or change the identity/permissions
  of a pre-existing lock as a shortcut.
- `artifacts`: objects containing unique `id`, exact `path`, `classification`,
  expected `sha256`, `workflow`, and a reconstruction `proof`.

A disposable workflow must have a nonempty `id`, `state: completed`,
`result: success`, and `pending_acceptance: false`. A caller must establish those
facts from retained workflow evidence; a JSON label is not self-authenticating.
A failure or historical baseline is not made disposable by changing a label.

A proof has a retained `path` and the candidate's expected content `sha256`.
Ordinary proofs are independently retained duplicate files. For immutable
archive members, add an absolute archive `member` and optionally
`format: squashfs`; the default format is ISO. Archive files must be independently
pinned. The tool streams the actual member through xorriso or unsquashfs and
compares its bytes, without extracting into the host tree. Only these two
explicit archive formats are supported. Actual QEMU backing inspection requires
`qemu-img`. Missing tools and unreadable catalogs are refusals, not clearance.

An approved plan includes the policy digest, target inode/device/mode/owner/link
count/timestamps/size/allocated blocks and content digest, retained proof, pins,
and backing catalog. Review the exact target set, not just the total size.

Execution needs all explicit approvals and a new private audit directory:

    python3 scripts/artifact-maintenance.py --policy /private/run/retention.json apply \
      --approve-policy POLICY_SHA256 --approve-plan PLAN_SHA256 \
      --targets-file /private/run/approved-target-ids.json --audit /private/run/new-audit

The targets file is a JSON array of the exact artifact IDs in the reviewed plan.
The command is an interface example, not approval to run an arbitrary policy.
Full procfs visibility is required for execution. When ordinary permissions hide
other users' descriptors/mappings/mount namespaces, stop for normal owner
administrative authentication; do not bypass it. Never run an ISO build merely
to obtain cleanup permission. Keep approval and source digests outside mutable
workflow output when preparing an authenticated owner handoff.

## Safety and interruption

Execution takes every configured lock nonblocking, rebuilds the plan, verifies
its digest and exact selected IDs, checks processes/mappings/mounts, reads QEMU
backing chains and pins, and rechecks each target and retained proof immediately
before unlink. Ancestors are opened with directory FDs and `O_NOFOLLOW`; deletion
is a file-only `unlink` relative to the verified parent FD. Hardlinked targets,
source repositories, directories, changed identities, pinned paths and missing
proofs are refused. No recursive tree deletion is implemented.

This is an administrative/cooperating-workflow tool, not a security boundary
against a malicious same-owner process or hostile root continuously renaming
ancestors. Keep roots stable under the owning locks. Ensure the image catalog is
complete: a manifest cannot prove that an undisclosed disk outside the configured
catalog has no backing dependency.

The private `events.jsonl` is exclusively created. Every intent is flushed and
fsynced before unlink, every successful unlink is followed by parent-directory
fsync and a durable receipt, and normal interruption records ABORTED. Terminating
signals stop further deletion and allow bounded audit/FD unwinding. SIGKILL or
power loss can leave a last INTENT without REMOVED: inspect that exact path and
inode against the log before creating a new plan. Never replay an old approval
or assume rollback. A changed/partially applied plan is refused. Existing audit
directories are never overwritten.

The final receipt distinguishes allocated bytes unlinked from the exact observed
filesystem available-space delta. Concurrent log/cache growth, delayed allocation,
shared extents or other writers can make those differ. Do not call a dry-run
estimate reclaimed storage. Independently compare original path inventories,
protected checksums, backing catalogs and source status after real execution.

Removing duplicate unpacked package payload from a completed build root leaves
that root NOT READY for chroot/build reuse, even when its package DB is preserved.
Rematerialize from its exact source/package manifest or retained immutable image;
never use the retained DB as evidence that pruned files still exist.

## Normal sprint contract

1. Before allocating space, inspect existing evidence, source/input digests,
   storage, processes and locks. Reuse a test result only when its actual inputs
   and required environment are unchanged; keep native/ISO/physical gates distinct.
2. Use one new exclusive build/test directory per real attempt. Write its private
   retention manifest at creation. Record bounded QEMU supervisor lifetime,
   shutdown interface, backing parents and owning QA lock; no detached orphan.
3. After delivery, preserve exact essential receipts and unresolved failure
   evidence first. Mark only successful disposable outputs as candidates.
4. Generate/review a read-only maintenance plan. Execute only that explicit
   approved policy/target set within current owner authorization, then verify
   actual storage and preservation. Do not auto-prune shared package stores.
5. Record storage used/reclaimed, protected artifacts, remaining candidates,
   active/parked branches and PRs, Daily Driver blockers and one next gate in the
   existing current status. Do not create duplicate issues or reports.
6. Stop owned tests/guests, verify locks available, and leave paused automation
   paused. Branch retirement is a proposed owner-reviewed list only; no force
   push, history rewrite, autonomous merge, tag/release deletion or branch deletion.

The owner-facing close-out must name actual storage/access blockers, not hide
unreclaimed data behind a cleanup estimate. A trust or privilege gate is a reason
to checkpoint and stop expensive work, not retry unchanged builds or tests.
