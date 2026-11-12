# Wilsof Pyramid development loop

This is a synchronous Hermes workflow, not a new agent platform or unattended
service. GitHub issue #16 remains the human-readable project dashboard; issue #60
remains the release acceptance specification. `automation/.pyramid/state.json`
is a private execution projection of those authorities and retained evidence,
not another backlog, dashboard or replacement for the host artifact catalog.

## Session and task contract

1. Read the checkpoint (`python3 automation/pyramid.py status`), current #16,
   current #60 and only the exact handoff/evidence paths they reference. Reconcile
   newer native receipts before trusting old prose. A missing/inaccessible path
   is not automatically ENOENT. Do not repeat broad inventory or completed cleanup.
2. Keep the permanent product goal separate from the current release gate.
   Inspect source HEAD/WIP, inputs, permissions and relevant existing workloads.
   Refresh observations with evidence; never manufacture approval or test results.
3. `python3 automation/pyramid.py next` selects from the finite current milestone
   execution slice. Dependencies must be completed, known blockers absent and
   explicitly required approvals satisfied. Estimates score
   `(5*impact + 3*unblocks) / ((minutes+5)*(1+risk+cost))`, descending, then task ID.
   Scores are estimates, not measured efficiency. Impact/dependency/risk/cost are
   0..5. Missing approval fails closed. Three workstreams: Product, QA,
   Infrastructure. Permission eligibility is checked before ranking.
4. Before dispatch, use `begin TASK --expected SHA256` from the latest status.
   This writes RUNNING durably. Inspect → Plan → Implement → Test → Review, then
   use `finish RECEIPT.json --expected SHA256`. Execute with existing tools; the
   state CLI intentionally never starts shell commands, models, sudo or services.
   Record exact commands/statuses outside Git in the existing private evidence
   area. A PASS requires actual exit0, evidence hashes and explicit accepted
   review of the intended result/milestone contribution; it does not certify the
   review's truth or grant native/image acceptance. Repair relevant regressions.
5. Continue to `next` in the same authorized session. Completed input identities
   are never selected again. FAIL/BLOCKED/INTERRUPTED retain receipt and original
   exit; they are not automatically retried. To repair, inspect the failure, make
   the focused change, then `repair REPAIR.json --expected SHA256` with a new
   input identity, documented reason and hashed evidence. Old attempts/completions
   remain unchanged. Run acceptance again for the actual changed input.
6. Publish a concise verified delta on #16, read that exact comment back, and
   checkpoint its reference. Do not duplicate #60's matrix or create new tracking
   issues. Read back remote source/CI before claiming publication or CI success.

The command paths above follow `python3 automation/pyramid.py`; use `--state PATH`
before the subcommand only for isolated tests. `init --input JSON` is first-use
only and refuses existing state. `observe --input JSON --expected SHA256` updates
only blockers, approvals, source-check identity and evidence references, never
history, tasks or image acceptance. State is private/ignored, not embedded in ISO.
Tasks are a deliberately small execution slice; a genuinely new milestone needs
an explicitly reviewed schema-compatible transition, not an unattended planner.

A terminal receipt contains:

    {"attempt":"<running UUID>","task":"<task ID>","result":"PASS|FAIL|BLOCKED|INTERRUPTED",
     "exit_code":0,"review_accepted":true,"milestone_advance":"what was verified",
     "evidence":[{"path":"<absolute retained file>","sha256":"<exact digest>"}]}

A repair document contains `task`, a different `input_identity`, nonempty `reason`,
and one `evidence` path/SHA256 object. These are cooperating-owner records, not a
security boundary against hostile users with write access. Do not store secrets.

## Interruption and recovery

`status`/`next` are read-only. RUNNING yields RECONCILE, never another execution.
Reconcile actual process/lock/service/receipt state before calling finish: a dead
CLI, shell exit0, inactive main PID or missing terminal alone proves neither build
completion nor safe resource release. Keep existing project/QA lock custody until
the native supervisor proves every owned service/cgroup/guest has exited.

Mutations use a nonblocking persistent metadata flock and expected-state SHA256.
Each writes a same-directory private temporary, fsyncs data, atomically replaces
`.prev` with the old valid snapshot, then the main state, and fsyncs the directory
after each replacement. Concurrent/stale writers refuse. Failed writes retain
private temporary evidence. A post-rename fsync failure means durability is
uncertain: reread, do not blindly repeat the operation.
Serialized state is bounded to1MiB before either snapshot changes. Duplicate or
malformed approval IDs/statuses are refused; record order cannot grant permission.

Invalid/current-future schema data is not silently overwritten or defaulted.
For corrupted bytes only, `recover --expected SHA256` explicitly preserves the
current bytes under a unique `.corrupt-*` name and restores the validated `.prev`.
It refuses rollback of valid state. Recovery can lose the newest state transition:
the restored snapshot therefore has a mandatory RECONCILE_RECOVERY barrier, even
if .prev appears idle. No begin can execute through it. After inspecting actual
native services/locks/receipts and retained temporaries, use
`reconcile-recovery RECONCILIATION.json --expected SHA256`. Its document requires
nonempty `reason`, one hashed `evidence` object and `dispositions` covering every
restored unfinished task: NOT_STARTED only with explicit evidence that no work
started, otherwise RETAIN. RETAIN quarantines a lost attempt as checkpoint-only
INTERRUPTED with native exit unknown; existing attempts/results are never erased.
Known RUNNING still yields RECONCILE, not EXECUTE, after barrier reconciliation.
Do not infer NOT_STARTED from a missing terminal or stopped native process.
Unknown future schema is refused rather than restored as an older schema.
SIGKILL/host loss cannot guarantee native cleanup. Tests kill a real disposable
writer before rename and verify old complete snapshots, lock release and preserved
temporaries; they do not simulate storage hardware/power-loss durability.

## Existing production and QA integration

Reuse the already reviewed bounded production owner entry and its pinned input
manifest, not a duplicate producer or consumed older helper. Its native pool
admission/reuse tests, build receipt, artifact export and QA reservation remain
separate gates. Before execution reconcile current catalog, capacity, original
pins, existing lock/workload state and normal VM112 administrative authorization.
Do not run the new-only owner entry over an existing pool, reset a failed marker,
repeat historical32-file retirement, create another permanent root or parallel build.

After actual BUILD-PASS: retrieve native receipts, verify service/cgroup exit,
independently hash the real ISO against the receipt, then use existing exact-image
QA tooling and the full59 formal criteria from #60. Prior source tests, stubbed
supervisors, original RC2's58/1 and RAM-only materialization do not transfer PASS.
Preserve each failed attempt and the known A02 failure. TEST ONLY trust never
becomes production trust through a state edit. `last_accepted_iso: null` explicitly
means no artifact is recorded as having passed this complete59-gate milestone;
older preliminary acceptance remains in its original evidence.

The proposed permanent least-privilege administrative runner is separately gated:
reviewed root-controlled entrypoint, fixed operation allowlist/targets, no arbitrary
commands or user-controlled imports, existing locks, budgets, durable audit and
owner-approved installation/authorization. This workflow does not install it,
modify sudoers/polkit, create credentials or treat an earlier proposal as approval.
Use the retained consolidated normal-authentication owner command until then.

## Acceptance and stop conditions

Accept an engineering task only when intended change/result, relevant tests,
preserved evidence, review and absence of critical regression are established.
The CLI cannot independently adjudicate those facts; Hermes is accountable.
Accept corrected RC2 only after59 mandatory exact-artifact PASS, never task-count
completion. Empty executable work yields REVIEW_MILESTONE or BLOCKED, not release.

Stop/checkpoint for owner stop, privilege/authentication boundary, protected data,
physical device/disk work, production signing, material scope/security/cost change,
unsafe capacity/lock/input drift or provider quota/auth failure. Consolidate owner
needs. Do unrelated safe critical-path work only when it has a specific deliverable;
never fill a blocker with more administration. Do not self-grant privilege, weaken
signature/security gates, expand storage or use paid inference fallback.

Orchestration work is capped at approximately60–90minutes, followed by direct
product work or a truthful owner-only blocker. Existing schedulers stay paused.
No claim of multi-hour unattended execution or measured gains follows from this
helper. The default-profile Wilsof skill locates this workflow even from outside
the checkout; project rules provide the in-repository entrypoint.

## Verification

`python3 -m pytest tests/test_pyramid.py -q` exercises ranking, permission/dependency
refusal, durable previous snapshots, stale/concurrent writers, process interruption,
corrupt-state recovery, evidence drift, failure retention, explicit repair and
actual CLI resumption. These are host-only orchestration tests, not image tests.
