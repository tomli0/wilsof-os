# AS-02 Architecture Simplification — Phase 1B

2026-11-02 UTC. Decision: **A is the preferred minimal architecture; native acceptance remains open.** Architecture investigation only, based on `7dc69f5b38b05c47c7bd8abc2bd38563062c6408`. Production is unchanged. This report changes the proposed solution, not the acceptance status of PR #49.

## 1. Verified boundary and existing behavior

The ext-session-lock-v1 contract assigns authentication to the locker and normal-surface input/render isolation to the compositor. The `locked` event follows protected presentation on all outputs; a dead locker must not unlock the session. Its privileged-surface exception matters: this is not an unconditional promise about every shell surface.[6]

Hyprland's inspected implementation stores lock ownership/state in `src/protocols/SessionLock.cpp` (`onLock`, lines 193–209; `unlockAndDestroy`, 130–147).[7]
`SessionLockManager.cpp:98–101` clears existing keyboard focus and the seat grab.[8]
`FocusState.cpp:235–236` rejects focus on a non-lock surface while locked.[9]
`InputManager.cpp:341–373` routes ordinary pointer targeting to the lock surface, except explicitly interactive above-lock layers.[10]
`ViewHitTester.cpp:344` requires `above_lock=2` for that exception.[13]
These are actual native boundaries, not Wilsof notification handlers.

DModal Top/Overlay placement does not itself confer the lock-surface role. Normal Command Center, Shortcuts and About surfaces remain ordinary layer-shell clients even though resident in DMS. Renderer exclusion/opaque primer and lock-surface rendering are in `Renderer.cpp:1211–1215,1781–1828`; `above_lock` and `misc:session_lock_xray` are deliberate exceptions. Inspect effective generated/user rules before acceptance; source defaults are not installed policy.[5][12][18]

**Falsification caveat:** do not cite `SeatManager.cpp:755–758` as proof that grabs are denied during session lock.[11] It calls `CInputManager::isLocked()`, which at `InputManager.cpp:1916–1917` means pointer constraint, not session lock. FocusGrab start can install a new grab; subsequent raw focus still encounters the native lock guard. A grab may impede locker focus: this is a source-level availability/routing concern, NOT a demonstrated password leak or bypass. Reacquisition, held input and touch remain mandatory native tests.[9][10][25]

Hyprlock requests the actual protocol lock, waits for `locked`, and releases via `sendUnlockAndDestroy()` (`hyprlock.cpp:764–850`). Grace and SIGUSR1 also initiate release: compositor release is not independent proof of PAM success. Wilsof uses immediate rendering; installed PAM, effective flags and recovery policy remain unverified.[15]

Current AS-03 helper validates session/compositor identity and uses atomic flock; busy means unconfirmed, not already-secured success. It sends `loginctl lock-session` before launching Hyprlock and never sends unlock on exit. The request can fan out to Hypridle and DMS, so redundant initiation and cached shell state are separate from acquisition. Native inherited-fd/session mapping remains open.[4][31]

DMS backend maps Lock requests into cached Locked state; SessionService forwards that boolean. A missing/late false can clear UI bookkeeping without touching Hyprland's lock object. Conversely stale true can leave Command Center refusing open after real unlock. Backend refresh/LockedHint can change that outcome: permanent latching is a risk, not established inevitability.[20][21][24]

## 2. Root cause: real defect versus over-specified architecture

The original verified AS-02 defect was unconditional UnlockSession after locker failure. No authentication bypass was demonstrated. PR #49 removed that behavior but retained synthetic request-based UI denial without a complete liveness path.[4][29]

Phase 1 then required generation-bound authority and preactivation UI ACK to synchronize a second authorization state. Its adversarial findings are valid for that conditional model, but do not establish that ordinary applications need that model to be isolated by a compositor lock. The model's stronger “nothing executes after intent/ACK” requirement differs from “no newly generated locked-session input reaches ordinary surfaces.” Treating them as equivalent introduced the architecture problem.[1][2][3]

The F1 comments assert that an open modal would receive password input. They document intended prevention, not measured native routing. No such leakage is established here; queued pre-lock events, a modal visible after unlock and stale DMS state are not themselves authentication bypasses.[5][8][9]

## 3. Alternatives A/B/C

| Alternative | Security and failure boundary | Complexity, updates, maintenance, dependencies | Decision / required evidence |
| --- | --- | --- | --- |
| **A Native compositor protection** | Hyprlock owns secure surfaces; Hyprland owns lock/input routing. UI events cannot authorize native unlock. Locker crash retains lock by contract; shell crash does not own it. Does not freeze background execution or cover pre-acquisition input. | Lowest Wilsof security code; existing dependencies only. Must qualify exact compositor/locker versions, rules and grab behavior after updates. | **Preferred, conditional.** Native routing, presentation and post-unlock liveness tests required. |
| **B Existing DMS/Quickshell lifecycle** | DMS has a built-in `WlSessionLock`, `secure` and PAM lifecycle. Its custom-lock command instead bypasses its own lock object; `isSessionLockSecure` cannot observe external Hyprlock. Restart follows logind state and can respawn a custom locker. | Reuse supported modal close/focus helpers cosmetically. Migrating authentication to the DMS locker changes policy, branding, crash domain and tests; it is not a small CC fix. No new dependency, but greater shell coupling. | Use existing lifecycle for UX only. Do not replace Hyprlock or treat own-lock `secure` as a global observer.[17][22][23] |
| **C Independent coordinator** | Could serialize cooperative intents with atomic admission, origin-bound generation ACKs, fresh process/session incarnations, crash cleanup and fail-closed IPC/disconnect handling. Cannot manufacture native provenance or intercept arbitrary direct lockers. Pending-disconnect recovery still needs authority. | Highest custom security code: native observer/adapter, IPC validation, persistent ownership/reconciliation, reconnect and external-path coverage. Estimate: several separately reviewed work packages, not a small 10–12 iteration change; maintenance becomes tied to compositor and DMS internals. | **Not justified.** Only revisit if a required property is proven missing from A/B; no coordinator implementation.[2][3] |

No SessionService sessionLocked callback was found in the inspected DModalHost; do not assume DModal automatically closes for an external locker. Quickshell's own-lock `secure` reflects its own protocol object, not an external session-lock subscription. The supported native mechanism to reuse for security is the compositor's lock, not an application boolean.[19][22][23]

## 4. Recommended architecture and invariants

Adopt A as the design target, with B limited to presentation cleanup. Keep Hyprlock; keep Command Center an ordinary non-lock surface. Never grant it above-lock interaction. Never use a stale notification, child exit, DMS restart or IPC response to unlock the compositor. Do not add a permanent service, new IPC protocol, generation store or authorization ACK.

After genuine native release, ordinary input eligibility returns through compositor routing; CC must not remain denied solely by a synthetic sticky `SessionService.locked`. Close/clear modals and cancel search on a best-effort lock notification, with no unlock notification required to reauthorize them. Cosmetic checks may suppress stale callbacks but must not be presented as the security boundary. This liveness simplification is a proposal, not exercised QML/runtime behavior.

Scope is local interactive access during an acquired native lock. Background apps/IPC continue running; same-UID/root/compositor/locker compromise, privileged input methods and explicitly above-lock surfaces are outside an ordinary-surface guarantee. If the product instead requires atomic denial from *request time* for every initiator, including direct external locks and already queued work, A alone does not establish that stronger requirement.

## 5. Code potentially removed NEXT session

- Remove the synthetic `loginctl lock-session` roundtrip from the direct Hyprlock start path if dependency tests confirm it is not required for another supported request consumer; external logind requests still need Hypridle/DMS's normal handler.
- Remove/reclassify CC's sticky `SessionService.locked` open/toggle/search authorization gate. Preserve small best-effort modal cleanup, including About/Shortcuts and deferred opens, without creating another authoritative local lock state.
- Do not revive secured/released shell hooks, receiver-labelled generations, UI-ACK tokens, exit-based unlock or synthetic `UnlockSession`/`SetLockedHint` bridges. Keep the Phase 1 spike as historical evidence, never payload.
- **Do not remove AS-03 flock/session validation in this work package.** It solves duplicate/cooperative starts, not lock authority; fd lifetime and two-session mapping remain separate acceptance gates.

These are removable responsibilities, not production edits made here.[2][4][5]

## 6. External initiation and remaining failure scenarios

Hypridle's 180/300-second wrappers, manual Super+L and CC lock action use Wilsof's helper; before-sleep uses the helper with `inhibit_sleep=3`. Hypridle observes compositor lock notifications for its own sleep inhibitor and ScreenSaver state; it does not make LockSession an authentication assertion.[16][30]

DMS power/session controls may use its built-in locker or configured custom command; actual installed settings/overrides were not certified.[17]
Direct Hyprlock and other ext-session-lock clients bypass Wilsof flock yet still enter Hyprland's native lock path.[6][7]
Other desktop apps may only send logind/ScreenSaver requests: successful delivery is not acquisition.[24]
Suspend has inhibitor deadlines and backend limitations; neither a delay timer nor a request guarantees secure resume.[16][24]

Required policy checks: one intended locker; no above-lock exception for Wilsof namespaces; no xray/transparent policy exposing content; no unexpected locked-enabled launcher bindings; explicit treatment of grace, SIGUSR1, compositor forceunlock and lock restoration. A competing locker must not release the current owner. A compositor crash/new greeter session is a separate lifecycle, not an authenticated unlock of the old session.

## 7. Isolated validation: all ten scenarios, no native pass

Executed **10 source-contract/real-JS callback tests, 0 failures, 0 errors, 0 skips**. The fixture executes the actual retrieved `updateLoginctlState` function in existing Node, plus source assertions. It does not run Qt, Wayland, DMS, Hyprlock, PAM or a compositor and builds no native-security model. Passing counterexample tests expose unresolved premises rather than repair them. Reproduce with `python spikes/as02-native-boundary/probe.py --sources-root <directory-containing-as02-upstream-clones>`; exact SHAs and sanitized receipts are adjacent.[20]

| Scenario | Isolated evidence / limitation | Required dynamic acceptance (all NOT RUN) |
| --- | --- | --- |
| 1 Old unlock during new lock | Actual callback accepts late false; native focus guard is separate. | Inject stale UI false while lock B owns session; no key/click/touch or pixels to CC. |
| 2 DMS restart while locked | QML defaults false; native lock state lives elsewhere. | Restart shell/backend; neither steal focus, expose CC nor create a conflicting owner. |
| 3 CC already open | Native acquisition clears focus and seat grab in source. | Open CC/Shortcuts/About, lock; synthetic secret reaches only locker. |
| 4 Open during transition | Source detects pointer-lock/session-lock mismatch; reacquisition unresolved. | Force IPC/lazy open before, during and after acquisition, including new grab attempts; no leak or focus deadlock. |
| 5 Locker crash | Destruction path does not clear native flag; protocol requires retention. | SIGTERM/SIGKILL/disconnect after secured versus startup failure; retain safe display/input, test authorized recovery. |
| 6 IPC disconnect | Missing state yields UI false, not native release. | Kill DMS IPC/backend and reconnect; lock remains, later honest unlock restores UI. |
| 7 Repeated locking | Actual duplicate booleans emit edge signals only. | Immediate relock and manual/idle/sleep contention; one owner, no stale release, no stuck CC. |
| 8 External lock | Native onLock has no Wilsof dependency. | Direct Hyprlock, logind, ScreenSaver and DMS actions with wrappers bypassed as appropriate. |
| 9 Successful unlock | Explicit protocol release and UI false paths inspected. | Wrong password rejected; correct PAM releases; fresh CC input works without custom unlock bridge. |
| 10 New session | Actual callback can rebind session ID; no generation guarantee implied. | Logout/new authenticated session, persistent user manager/two same-UID sessions; no stale ownership or UI latch. |

Additional QEMU criteria: identify installed package hashes/PAM/configs and exact source correspondence; inspect effective layer rules/binds; observe frames and focus on all outputs/DPMS/hotplug; test mouse, keyboard repeat/held keys and touch where available. Mark input sent before acquisition separately from input generated after secured confirmation. Check synthetic secret absence in CC query/status/search argv/logs. Actual suspend/resume and physical client Super/F1/password forwarding remain separate hardware gates; QEMU success alone cannot close them.

## 8. Independent architecture review and falsification result

One fresh-context read-only reviewer favored A conditionally, identified the request-cache/liveness problem, deliberate rendering exceptions, queued-work distinction, DMS restart/custom-lock ownership and missing native grab-reacquisition proof. It did not certify production. Its final read batch stopped at a misnamed FocusGrab path; the parent located/read `src/protocols/FocusGrab.cpp` and added the explicit pointer-constraint mismatch probe. Reviewer B/C labels differed from this assignment; this report uses the requested A/B/C definitions, not those shorthand labels.

The attempt to falsify A therefore leaves a specific unresolved native grab/focus acceptance gate, not a demonstrated authentication bypass. There is no basis to deploy “all UI guards removed” today, and no evidence that a custom coordinator would cure that upstream routing concern. If forced ordinary surfaces get active-lock input, or secure release cannot restore normal interaction without new authority, stop and revise the decision rather than add an asynchronous unlock patch.

## 9. NEXT-session implementation scope (proposal only)

One separately authorized **10–12 iteration, non-deployed candidate**: reproduce CC's request-derived sticky denial; remove only the direct synthetic request/CC authorization coupling; retain cosmetic cleanup and deferred-modal hygiene; retain AS-03, native locker, payload and personal lock preferences. Add focused regressions for callback ordering/restart, no exit-based unlock and all modal entrypoints; run existing auth/CC/session/payload suites and scoped independent review. No authentication migration, coordinator, package update, ISO or unrelated DI fixes.

Proposed budget: 2 discovery/reproduction, 3 small source edits, 3 focused/full relevant verification, 1 review, up to 3 correction/publication iterations. Stop blocked if scope grows. Native QEMU routing/availability qualification is a separate explicit acceptance task; no production approval follows from the candidate's fixture pass. This supersedes the proposed need for W1/W3 generation infrastructure, not the consolidated review's still-open native gates.[28]

## 10. GO / NO-GO

**GO:** A as the simplest architecture target and a small separately authorized simplification candidate. **NO-GO:** declaring safe simplification dynamically established, deploying/merging #49, building a new candidate ISO, physical installed acceptance or release. Safe ordinary-surface isolation is supported by the protocol/source, but the exact installed stack, grab races and restoration must pass section 7 before adoption. B is cosmetic reuse, not a new lock authority; C is unjustified. Stop after this recommendation.

## 11. Execution, artifacts, cost and process boundaries

Dedicated branch `docs/as02-phase1b-20261102`; only this report, checkpoint and isolated fixture/receipts are changed. No production implementation, Phase 2, ISO build/mount, QEMU, installation, PAM/session operation, permanent dependency, merge/release, PR #47/#48/#49 modification or worker/scheduler activation. Existing ISO/QA artifacts were not used as fixtures or modified; no new hash audit is claimed. Existing automation pause state was not re-certified.

Main route: gpt-6.1-sol/openai-codex; one inherited-route independent review, no requested OpenRouter/fallback. Reviewer receipt reports 5 model API calls; actual billing/tokens and independently confirmed child model identity are unavailable. Bounded investigation only; no automatic continuation to implementation. No native/project execution lock or durable worker was created. Retrieved clones and existing Node are disposable/read-only test inputs, not new runtime dependencies. Scratch available **63790092288 bytes at 2026-11-02T17:39:40.730512+00:00**.

## 12. Publication and completion boundary

Publish this documentation/fixture-only branch with `[skip ci]`; verify exact remote commit/blobs and pre-existing refs, then append a linked receipt to permanent issue #16 without changing its status or approval controls. The private publication receipt records actual success/failure; a planned push is not verification. GitHub CI is not run by this investigation and no CI-success claim is made. Full production suites, graphical authentication, installation and physical acceptance were not run because production was unchanged and native execution was prohibited. Next action is an owner decision on section 9, not automatic implementation.

## Sources

[1] https://github.com/tomli0/wilsof-os/blob/7dc69f5b38b05c47c7bd8abc2bd38563062c6408/docs/development-reports/2026-11-02-as02-lock-protocol-phase1.md — Phase 1 report
[2] https://github.com/tomli0/wilsof-os/blob/7dc69f5b38b05c47c7bd8abc2bd38563062c6408/spikes/as02-lock-protocol/ADR.md — Phase 1 ADR
[3] https://github.com/tomli0/wilsof-os/blob/7dc69f5b38b05c47c7bd8abc2bd38563062c6408/spikes/as02-lock-protocol/independent-review.json — Phase 1 adversarial findings
[4] https://github.com/tomli0/wilsof-os/blob/a28d4678bbbaa091337fdab2b331a1b9e56b7e4d/bin/wilsof-lock-session — Current wrapper
[5] https://github.com/tomli0/wilsof-os/blob/a28d4678bbbaa091337fdab2b331a1b9e56b7e4d/config/dms/plugins/wilsofCommandCenter/CommandCenter.qml — Current UI
[6] https://github.com/wayland-mirror/wayland-protocols/blob/b9edf66597586c914b5b1ff3d964d7ed201adab9/staging/ext-session-lock/ext-session-lock-v1.xml — protocols/staging/ext-session-lock/ext-session-lock-v1.xml
[7] https://github.com/hyprwm/Hyprland/blob/e0e9c84375f660aee18c26e5cf23688540457481/src/protocols/SessionLock.cpp — hyprland/src/protocols/SessionLock.cpp
[8] https://github.com/hyprwm/Hyprland/blob/e0e9c84375f660aee18c26e5cf23688540457481/src/managers/SessionLockManager.cpp — hyprland/src/managers/SessionLockManager.cpp
[9] https://github.com/hyprwm/Hyprland/blob/e0e9c84375f660aee18c26e5cf23688540457481/src/desktop/state/FocusState.cpp — hyprland/src/desktop/state/FocusState.cpp
[10] https://github.com/hyprwm/Hyprland/blob/e0e9c84375f660aee18c26e5cf23688540457481/src/managers/input/InputManager.cpp — hyprland/src/managers/input/InputManager.cpp
[11] https://github.com/hyprwm/Hyprland/blob/e0e9c84375f660aee18c26e5cf23688540457481/src/managers/SeatManager.cpp — hyprland/src/managers/SeatManager.cpp
[12] https://github.com/hyprwm/Hyprland/blob/e0e9c84375f660aee18c26e5cf23688540457481/src/render/Renderer.cpp — hyprland/src/render/Renderer.cpp
[13] https://github.com/hyprwm/Hyprland/blob/e0e9c84375f660aee18c26e5cf23688540457481/src/desktop/state/ViewHitTester.cpp — hyprland/src/desktop/state/ViewHitTester.cpp
[15] https://github.com/hyprwm/hyprlock/blob/69dc06ac0e04c75a95b1ffdf71992bfb03663c3f/src/core/hyprlock.cpp — hyprlock/src/core/hyprlock.cpp
[16] https://github.com/hyprwm/hypridle/blob/aa958ed7ad4863860b93ecd7189419e193bfae2c/src/core/Hypridle.cpp — hypridle/src/core/Hypridle.cpp
[17] https://github.com/AvengeMedia/DankMaterialShell/blob/7643dad25a585d380ba9eda3ff3e689fdade1e21/quickshell/Modules/Lock/Lock.qml — dms/quickshell/Modules/Lock/Lock.qml
[18] https://github.com/AvengeMedia/DankMaterialShell/blob/7643dad25a585d380ba9eda3ff3e689fdade1e21/quickshell/Modals/Common/DModal.qml — dms/quickshell/Modals/Common/DModal.qml
[19] https://github.com/AvengeMedia/DankMaterialShell/blob/7643dad25a585d380ba9eda3ff3e689fdade1e21/quickshell/Modals/Common/DModalHost.qml — dms/quickshell/Modals/Common/DModalHost.qml
[20] https://github.com/AvengeMedia/DankMaterialShell/blob/7643dad25a585d380ba9eda3ff3e689fdade1e21/quickshell/Services/SessionService.qml — dms/quickshell/Services/SessionService.qml
[21] https://github.com/AvengeMedia/DankMaterialShell/blob/7643dad25a585d380ba9eda3ff3e689fdade1e21/core/internal/server/loginctl/monitor.go — dms/core/internal/server/loginctl/monitor.go
[22] https://github.com/quickshell-mirror/quickshell/blob/9b0f339b19057f4731bf3b48293307d7ef241671/src/wayland/session_lock.hpp — quickshell/src/wayland/session_lock.hpp
[23] https://github.com/quickshell-mirror/quickshell/blob/9b0f339b19057f4731bf3b48293307d7ef241671/src/wayland/session_lock/lock.cpp — quickshell/src/wayland/session_lock/lock.cpp
[24] https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html — logind D-Bus contract
[25] https://github.com/hyprwm/Hyprland/blob/e0e9c84375f660aee18c26e5cf23688540457481/src/protocols/FocusGrab.cpp — hyprland/src/protocols/FocusGrab.cpp
[28] https://github.com/tomli0/wilsof-os/blob/7dc69f5b38b05c47c7bd8abc2bd38563062c6408/docs/development-reports/2026-11-02-consolidated-engineering-review-5.md — Consolidated review
[29] https://github.com/tomli0/wilsof-os/blob/7dc69f5b38b05c47c7bd8abc2bd38563062c6408/docs/development-reports/2026-11-02-auth-session-security-review-2.md — AS02 AS03 original findings
[30] https://github.com/tomli0/wilsof-os/blob/7dc69f5b38b05c47c7bd8abc2bd38563062c6408/config/hypr/hypridle.conf — Current idle policy
[31] https://github.com/tomli0/wilsof-os/blob/7dc69f5b38b05c47c7bd8abc2bd38563062c6408/docs/development-reports/2026-11-02-auth-session-remediation-2.md — Current AS03 remediation
