# AS-02 Secure Lock Protocol — Phase 1, 2026-11-02

Status: **architecture/prototype complete; production protocol BLOCKED**.
Branch: `experiment/as02-protocol-phase1-20261102`, based on consolidated review `b75b8f8544e48578ac9c299307fe833c48f1ab19`.
Evidence began 10:56 UTC; publication identity/read-back is recorded separately.

## 1. Completed scope

Read actual current wrappers, session/compositor-scoped flock, Command Center F1/lazy access paths, startup/target chain, published AS-02 blocker and consolidated review; retrieved pinned upstream lock-notify, Hypridle, Hyprlock, Hyprland and Dux session/backend sources. Actual PR #47/#48/#49 source heads match the baseline listed in the ADR. Production branches and files are unchanged.

Deliverables: [concise ADR](../../spikes/as02-lock-protocol/ADR.md), [transition diagram](../../spikes/as02-lock-protocol/transition-diagram.md), [standalone runnable prototype](../../spikes/as02-lock-protocol/README.md), [executed results](../../spikes/as02-lock-protocol/results.json), [independent review summary](../../spikes/as02-lock-protocol/independent-review.json).

## 2. Independent adversarial findings

One fresh-context reviewer executed 19 tests and reported no internal logic error under the model's explicit assumptions, but production_ready=false. It identified missing origin-bound native generations, real UI-quiescence/activation enforcement, non-reused process incarnations and recovery during observer loss. Parent added three executable boundary probes; these reproduce limitations, not corrections. Core model bytes were not changed after review. Reviewer model identity was not independently reported.

## 3. Source quality and security

Conditional protocol uses session/incarnation/generation tokens, ordered authoritative events, fail-closed state and current UI ACK before modeled launch permission. Actual Dux contains sessionId/sessionPath but forwards no generation with the boolean lock signal. XML lock notifications are post-transition and untagged. Process exit never authorizes access. Existing mechanism alone does not establish the required strong protocol.

Deterministic RED: **2 failed / 1 passed**, for stale release and launch-before-ACK against a deliberately unsafe model alias. First GREEN: **3 passed**. Expanded/reviewer: **19 passed**. Final **22 passed in 0.07s**, including known-limit demonstrations and **6561** bounded length-four schedules. Related existing tests: **39 passed in 5.40s** (auth session, Command Center, session start and image payload contracts). Full project suite/native tests not rerun; production unchanged. Sanitized exact outputs and commands are in results.json. AST/JSON/whitespace/manifest and added-line security checks are required before publication.

## 4. Commits and CI

Only experimental files under `spikes/as02-lock-protocol/` and this report are committed on the new branch. No edit to PR #49, Integration2, existing review branches or deployment manifests. Commit/push and exact remote read-back are recorded in the publication receipt. Documentation/prototype publication is not CI success, merge or deployment authorization.

## 5. ISO/artifact identity

No ISO produced, mounted or modified. Historical Integration2 remains a different artifact from #49/prototype; its metadata is in the consolidated review. No fresh image-hash audit or new artifact acceptance is claimed. Existing QA and source artifacts are never mutable fixtures.

## 6. Installation results

Not run/not authorized: installation, storage operations, disk-only boot, live payload acceptance. All tests use in-memory or disposable fixture state only; the prototype has no native adapter.

## 7. Startup and real authentication

No real password, PAM, Hyprlock, compositor, DMS IPC, logout, session restart or suspend was performed. The runnable demo explicitly labels output MODEL TRACE. A compositor release is not itself proof of PAM success; actual installed package/policy remains a separate gate.

## 8. Blockers and assumptions

1. Current notifications lack native origin-bound lock generation; receiver labeling cannot manufacture it.
2. Truthful input/grab quiescence and enforcement through actual password activation are unproved. ACK -> returned start permission -> UI restart -> use retained permission is an exposed gap.
3. New process reconstruction can reuse tokens; real fresh incarnation identity is required.
4. Pending lock plus observer/IPC loss remains fail-closed with no same-session reconciliation, even after a genuine unlock.
5. Out-of-band locks can activate before notification/closure; all initiators require mediation or stronger compositor/UI coupling.
6. AS-03 native inherited-fd/session mapping, wrong/correct PAM, real focus/keyboard routing and hardware remain untested.

These prevent production adoption. A new permanent daemon was not shown necessary and would not itself solve the contracts. Prefer investigating integration into existing supported processes, with explicit native proof, not activating a background service.

## 9. Engineering and publication boundaries

Dedicated isolated experimental branch; only prototype/docs paths staged, no new dependency, no production imports/payload changes. The independent review is bounded and conditional, not approval to deploy. Existing branches/worktrees and artifacts are preserved. Publish exact-byte remote report/source read-back and keep issue #16 open. No PR, merge or release is required.

## 10. Model/API budget

Main session: gpt-6.1-sol/openai-codex. One explicitly requested independent review via inherited delegation route; no explicit OpenRouter/auxiliary CLI request, new worker, balance probe or paid fallback. Child receipt reports 3 model API calls; actual billing/token cost and child model identity are unavailable. Main work is bounded to at most twelve tool rounds including publication. No zero-cost claim or Phase 2 authorization.

## 11. Processes, locks and storage

Only synchronous source reads, fixture tests and publication; the one bounded reviewer completed. No native session/VM/builder/worker/scheduler lifecycle, dependency install, project execution-lock acquisition/release or physical operation. Existing automation controls were not changed/re-certified. Scratch storage at **2026-11-02T11:06:59.743753+00:00: 63994343424 available bytes**. Private evidence retains source identities, test receipts and publication read-back; no credentials/raw guest logs published.

## 12. Recommendation and stop

**NO-GO for production implementation/integration from this prototype.** Phase 1 supplies a tested conditional model and explicit counterexamples, not a verified native solution. First decide how origin identity, actual UI-to-password activation ordering, process incarnation and pending-lock reconciliation can be provided. That decision/native feasibility work requires separate authorization and review. Keep AS-02/#49 blocked. **Stop here; do not begin Phase 2.**
