# Authentication & Session Remediation 2/5 — 2026-11-02

Status: **PARTIAL / BLOCKED — AS-02 REMAINS PENDING. DO NOT DEPLOY OR MERGE.**
Source commit: `e8d7d10e91b34c831275c4c1d1ee323ab60d3849` on `fix/auth-session-security-20261102`. Base: review commit `2a6b1251896fc7e279bdcb51bdf46c419f080242`, including PR #48 source `26cf38457efb170d587bd6e1f0b6f353c92fab5c`. No source branch was merged or rewritten. Scope: AS-01, AS-02 and AS-03 only; no Review 3.

## 1. Delivered scope and finding status

| Finding | Source result | Acceptance |
| --- | --- | --- |
| AS-01 | Added `wilsof-idle` and shared helper to actual image manifest and executable desktop deployment | Fixed and fixture-verified for fresh installed payload; real installation not run |
| AS-02 | Removed ALL unlock notifications from locker exit/error/signal paths; unsafe asynchronous event bridge withdrawn | **Incomplete**: genuine-release/logind/shell resynchronization remains pending; not full remediation |
| AS-03 | Replaced UID-wide process-name check with an atomic, session/compositor-scoped flock | Fixture-verified; native Hyprlock descriptor retention and real session mapping unverified |

Both shell wrappers delegate to `bin/wilsof-lock-session`. No PAM policy, credential handling, privilege grants, F1 QML, Hyprlock presentation, or timeout policy was weakened or changed. The installed 180-second idle and 300-second normal-lock contracts remain configured; the dedicated idle presentation is required rather than silently substituted.

## 2. Independent review and corrective decision

First independent read-only review **FAILED**: asynchronous Hypridle `secured`/`released` handlers were not bound to a lifecycle generation; a delayed release from A could clear a newer B. That proposal was **not committed or published**. Both actions and their hooks were removed, not merely protected by another mutex. Regression tests reject these actions before any session command. There is no `unlock-session` or `SetLockedHint` operation in the final helper.

A second bounded independent static review **PASSED for the revised source only**, with no remaining security concerns or logic errors reported. It explicitly did NOT certify AS-02 completion, deployment, native descriptor behavior, real session mapping, F1 runtime, or PAM acceptance. Reviewers ran no tests or system actions. Main agent: gpt-6.1-sol/openai-codex; child provider/model was not independently reported. Review evidence is retained privately as `independent-review-1.json`, `independent-review-2.json` and staged diff snapshots.

## 3. Exact modifications and verification

- `runtime/image-files.txt:1–5` and `runtime/desktop.py:60–61`: distribute and install `wilsof-idle` and `wilsof-lock-session` executable, alongside both Hyprlock configurations. `tests/test_auth_session.py:20–42` constructs a source bundle from ONLY manifest entries, invokes real desktop provisioning into a fresh installed-home fixture, and checks every Wilsof executable referenced by deployed Hypridle config, both presentations, timer contracts, and installed Hypridle unit link. Live behavior is not used as proof.
- `bin/wilsof-lock:1–8`, `bin/wilsof-idle:1–8`: argument validation followed by exec into the shared lifecycle. No independent deduplication or unlock cleanup remains.
- `bin/wilsof-lock-session`, `context()`: validate private canonical runtime directory, owned Wayland socket, exactly matching compositor instance/PID ownership; resolve the compositor PID through logind `GetSessionByPID`; verify owned active/online Wayland user session and reject stale supplied session identity. Missing `XDG_SESSION_ID` can be resolved from PID. No arbitrary command output/environment/exception is logged. This strict mapping is an unverified deployment assumption, not proof supported targets satisfy it.
- `bin/wilsof-lock-session`, `main()`: open a mode-0600, non-symlink, singly linked regular guard file inside private runtime storage; acquire nonblocking exclusive flock before the lock request or child launch. Key includes validated session and compositor identity, not UID alone. Busy returns 75 and expressly does NOT claim a secure surface. Never unlink the guard inode: stale unlocked files are reusable and surviving owners retain the same lock. Pass its descriptor into the child so the fixture locker keeps exclusion after supervisor SIGTERM/SIGKILL. No guarantee is made that native Hyprlock retains arbitrary inherited descriptors.
- The helper preserves a normal child's exit code and converts signal termination to 128+signal. It does not equate zero with successful PAM authentication or actual compositor unlock. A lock request remains distinct from confirmed lock state. No failure, signal, zero exit, or duplicate invocation clears shell/logind state.
- `tests/test_auth_session.py` covers normal/nonzero/SIGTERM/SIGKILL child exits through both wrappers, repeated calls, deterministic overlap, supervisor death with surviving child, stale inode reuse, separate mocked sessions, identity/bus failures, unsafe runtime/guard files, and absent environment session ID. `tests/test_scripts.py` replaces obsolete tests that demanded unsafe unconditional unlock and UID-wide pgrep behavior with the new boundary contracts.

### RED→GREEN evidence

1. AS-01: **1 failed** on missing installed `wilsof-idle` → **1 passed** after manifest/deployment correction.
2. AS-02: corrected regression run against restored pre-change wrappers: **15 failed / 1 passed**, including all eight exit/signal cases exposing unconditional unlock. Interim implementation: **16 passed**. The initial attempt had a UNIX socket fixture path-length error, which was corrected and is NOT counted as RED. Final removal of the unsafe bridge is verified by explicit rejection tests. This does not establish complete correct-release behavior.
3. AS-03: before adding atomic ownership, **2 failed / 18 deselected**: duplicate starts and parent-death exclusion. After flock/descriptor handoff: **20 passed**. Additional hardening tests were subsequently added. A temporary guard-key mismatch in the test fixture was corrected; final tests use the same nonsecret session/compositor key.

Baseline full suite on the review commit: **422 passed / 2 skipped**. Final tested source bytes match `e8d7d10e91b34c831275c4c1d1ee323ab60d3849` (documentation publication may add a later commit):

    PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider --basetemp=FRESH_SCRATCH       tests/test_auth_session.py tests/test_scripts.py tests/test_hypr_config.py       tests/test_command_center.py tests/test_session_start.py tests/test_desktop_runtime.py       tests/test_image_payload_contract.py tests/test_installer_safety.py

Final focused result: **147 passed in 5.84s**, exit 0. Full `python -m pytest -q -p no:cacheprovider --basetemp=FRESH_SCRATCH`: **448 passed / 2 existing native opt-in skips in 23.78s**, exit 0. The full-count increase includes new parameterized cases and replacement of one obsolete legacy test, not a claimed increase in native coverage.

ShellCheck: both prescribed sh and bash groups passed, including `wilsof-idle`, `wilsof-session` and ReGreet wrapper in sh coverage. Changed Python ASTs and all config JSON parsed; staged/unstaged diff whitespace checks and scoped added-line secret/injection scan passed. Prior installer source/policy/provisioning and its dedicated regression file are byte-unchanged relative to #48; its regressions ran in focused and full suites. All authentication/session commands in new tests were substitutes; no real lock, credential or service operation ran.

## 4. Commits, draft PR and CI

Code commit: `e8d7d10e91b34c831275c4c1d1ee323ab60d3849`. Draft PR is stacked on `review/auth-session-security-20261102` and must remain blocked. The documentation publication commit and exact PR URL are recorded in the publication receipt and status issue #16, avoiding a self-referential report commit. Remote branch, exact report bytes, changed source blobs, PR draft/base/head/open state and status comment must be read back before claiming publication. No GitHub CI-green claim is made; workflow branch filters do not automatically cover this new stack.

## 5. ISO and historical QA preservation

No ISO build, QEMU, image mount, physical installation/storage operation, image cleanup, Proxmox change or release. Historical ISOs and QA artifacts were not opened as test fixtures or modified. Size/mtime/inode metadata for **8 discovered image paths** under the inspected artifact roots remained unchanged from this session's metadata snapshot; this is not a complete historical artifact inventory or a fresh content-hash audit. All existing remote branches are retained; compare their heads against the pre-change snapshot at publication.

## 6. Installation results

Actual installation, disk-only boot, real timer execution and physical hardware: **NOT RUN / NOT AUTHORIZED**. The fresh-home fixture proves payload/provisioning content only, not installer execution or installed-system runtime. Earlier Integration2 acceptance is historical and is not transferred to this source.

## 7. Startup, PAM and normal unlock

No new normal login, wrong-password test, genuine PAM unlock, logout/re-login or suspend/resume acceptance. PAM configuration remains system/package-owned and unchanged. The first bridge's removal is a fail-closed withholding decision, not a complete replacement authentication lifecycle.

## 8. Blocking limitations and required dynamic tests

**AS-02 remains a blocker.** Normal authenticated-release/logind/shell-state resynchronization is not implemented in this candidate. Shell lock state may remain locked after real PAM unlock, leaving Command Center/F1-related surfaces unavailable until session recovery/logout/login. This limitation is not a safe-to-deploy success. The candidate must not deploy, merge or release.

Completion requires a compositor-confirmed, lifecycle-generation-bound observer with ordered state transitions that rejects delayed release A after lock B and rejects reordered secured/released events. A plain mutex, process exit 0, signal cleanup, and independent asynchronous shell hooks are insufficient. Add deterministic regressions for these interleavings before enabling any unlock bridge. Real observer integration cannot be safely certified within this source-only session; no workaround falsely clearing lock state was installed.

Separately verify native Hyprlock retains the inherited guard through its entire lifetime; supervisor/locker signals and rejected competing lock; real logind Type/Class/PID mapping through greetd/start-hyprland and user services; two same-user graphical sessions; F1 modal/password routing during pending/secured/crashed/restarted states; genuine wrong/correct PAM submissions; actual 180/300-second and sleep ordering; suspend/resume, inhibitors, hotplug and multiple outputs. Session discovery or D-Bus failure deliberately refuses to pretend the desktop is locked; that failure itself needs visible runtime/recovery acceptance. Existing unrelated R1/R2 issues remain unchanged.

## 9. Workflow and report location

Only the seven scoped source/test paths and this new report are delivered, on a separate branch. No unrelated feature, dependency, PAM/polkit/sudo edit, source-branch rewrite, merge or issue closure. Report: `docs/development-reports/2026-11-02-auth-session-remediation-2.md`. Existing review report is preserved unchanged. Scoped second-review PASS is not permission to bypass this report's AS-02 blocker.

## 10. Agent/model budget

Main agent plus two bounded read-only reviewer invocations; main work limited to twelve tool rounds including publication. No scheduler, worker, cron or paid auxiliary CLI model was started. Actual aggregate billing/token cost unavailable; no zero-cost claim. Review result limitations are reported rather than spending further iterations on an unverified bridge.

## 11. Processes, locks and storage

Only synchronous source inspection/tests and report/GitHub publication. Fixture processes are scoped to scratch; no real session execution lock, VM or builder was started. Existing scheduler/worker controls were untouched, not re-certified. Git work is in an isolated scratch clone; original worktrees and image paths remain retained. Available scratch storage at `2026-11-02T09:16:59.940111+00:00`: **64366829568 bytes**. Final branch/blob/PR/comment/preservation verification is in the private publication receipt.

## 12. Next action and stop condition

Separately authorize completion and verification of the generation-bound AS-02 release observer, then re-review the final lifecycle before any deployment. This is a pending recommendation, not execution approval. **Stop after publishing this blocked partial remediation report. Do not begin Review 3, auto-remediate further, deploy, merge or release.**
