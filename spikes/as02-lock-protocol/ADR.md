# ADR: AS-02 session-scoped lock gate — Phase 1

Status: **PARTIAL specification; existing-mechanism drop-in NOT VALIDATED. Production BLOCKED.**
Date: 2026-11-02. Experimental code only; do not install/import it into the desktop.
Decision: reject an asynchronous boolean unlock bridge. Keep a deterministic contract model and its counterexamples; stop before Phase 2.

## Context and inspected identities

Base: consolidated review `b75b8f8544e48578ac9c299307fe833c48f1ab19`. Live heads were #47 `0abf4a51af2338f14c691c2d325d6abfa2c8a410`, #48 `26cf38457efb170d587bd6e1f0b6f353c92fab5c`, #49 `a28d4678bbbaa091337fdab2b331a1b9e56b7e4d`. The accessible AS-02 blocker is auth-remediation section 8, not an assumed separately named report.[1][2]

Upstream sources below were retrieved and pinned on this date. Hyprland/Hyprlock main snapshots are contextual source, **not identified installed package versions**; no exact running package or native behavior is certified. Dux v2.0.0 resolved to `9b413296b16721f7679fb62e624cb1ed2433fa58`; Hypridle v0.1.8 to `e5c01af0842bd66617f7004568df9406111d6e80`.

## Trace and trust boundaries

| Boundary | Observed code / ordering | Consequence |
| --- | --- | --- |
| Lock request → helper | Both wrappers exec `wilsof-lock-session`; context validates private runtime, Wayland socket, compositor PID and logind session; persistent inode/flock serializes one session/compositor | A request or held flock is not compositor-secured proof. Native fd retention/session mapping are still unproved.[3] |
| Helper → desktop → password | `main()` requests `loginctl lock-session` then starts Hyprlock. No awaited current-UI quiescence acknowledgement | Request delivery, modal close and actual focus/grab release are not a handshake.[3][4] |
| Compositor → Hypridle | Lock-notify emits alternating **zero-argument** locked/unlocked; notification follows transition/lock frames. Hypridle receives on its Wayland connection, updates `m_isLocked`, starts configured hooks and publishes ScreenSaver state | Useful compositor authority, but no producer lock generation or preactivation ACK in this protocol. Forked hooks introduce independent delivery; native wire ordering is not itself broken.[5][6] |
| logind → Dux backend → QML | Backend maps Lock/Unlock requests and LockedHint changes into `state.Locked`. QML `updateLoginctlState()` assigns `state.locked || false`, then emits sessionLocked/sessionUnlocked on boolean edges | This is not direct authenticated compositor-release evidence. State contains sessionId/sessionPath, so “no session identity anywhere” would be inaccurate; no origin-bound lock-generation token accompanies the boolean QML signal.[7][8] |
| QML → Command Center | open/toggle/search check SessionService.locked; lockdown closes center/loaded Shortcuts and stops file search; activate() and lazy onLoaded opening lack equivalent local guards | A delayed notification can defeat receipt-time labeling, and a close() call is not demonstrated native input/grab quiescence.[4] |
| Startup/termination/recovery | greetd-owned session wrapper execs packaged start-hyprland; Lua starts Wilsof user target, requiring graphical-session and ordering DMS; DMS startup post-hook requeues wallpaper | No lock-generation store, native observer resync or preactivation handshake is supplied by this startup chain. No session actions were exercised.[11] |
| Compositor release → authentication claim | Hyprland also has forceUnlock; inspected Hyprlock has grace/SIGUSR1 paths | Compositor no-longer-locked is stronger than process exit, but **does not prove PAM succeeded**. Authentication/policy audit is a separate gate.[9][10] |

Trust excludes malicious same-UID/root/compositor/locker compromise: typed tokens are correlation, not credentials. A future IPC adapter must authenticate peer/session/connection and reject malformed data; this model is not such an endpoint.

## Minimal conditional protocol

One serialized owner holds `(session identity, authority incarnation, generation, event sequence)`. Session identity must bind boot/logind/compositor identity, not UID alone. Generation increases for **every accepted intent**, including immediate relock; old tokens/acks are invalidated immediately. Observer/process incarnation must be non-reused across real restarts. The model's integer incarnation is only an in-memory stand-in.

1. Default UNKNOWN, deny every open/search/activation/lazy modal path and existing text input. No boolean false or process status establishes an unlocked baseline.
2. Begin intent g: latch denial synchronously and request quiescence. UI ACK must bind g and UI incarnation, with all modal grabs/input and deferred opens actually disabled, not just a successful IPC return.
3. Model start permission requires the current ACK, live observer, synchronized authority and no occupied locker slot. It **does not launch a process**. Keep one physical slot until its own authoritative release; a new intent may replace the logical generation without overlapping native launches.
4. Origin-bound secured(g,seq) establishes LOCKED. Wrong password and all exits/signals leave gate closed. Release(g,seq) can restore IDLE only for the active intent after secured. An older release can drain its old physical slot, never release a newer intent. Gap/reordering/unknown origin quarantines.
5. UI restart drops ACK/defaults denied; a later real current release plus new current ACK can recover in the model. Observer/IPC loss denies access and requires a fresh causal baseline/incarnation. Pending-lock reconnect deliberately cannot guess recovery; it remains unavailable.

See [transition diagram](transition-diagram.md), [model](protocol.py) and [tests](test_protocol.py). All source-generation/fence/ACK facts are supplied as trusted model inputs, not derived from DMS booleans. Labeling a notification with current g **at receipt** is specifically prohibited.

## Alternatives and feasibility verdict

| Approach | Decision |
| --- | --- |
| Exit-zero, unconditional unlock, logind requests or boolean hooks | Rejected: neither authenticates release nor preserves origin across cycles.[2][3][8] |
| Receiver adds a counter to DMS boolean | Rejected: histories A genuinely released and delayed release A while unobserved B is locked can look identical. A sequence counter cannot recover missing provenance. |
| Single ordered native observer, per-cycle subscription or Wayland synchronization barrier | Worth a separately scoped feasibility decision. Connection-local ordering/object lifetime may support correlation under strict exclusive lock routing, but cross-client activation, initial state, external locks and UI quiescence are unproved. Do not claim that a roundtrip orders unrelated clients or current DMS callbacks. |
| Existing DMS process/backend hosts the coordinator | Preferred location to investigate **if** authoritative generation/fence and all-entrypoint fail-closed UI latch can be implemented; avoids assuming a new permanent service is necessary. Actual API/changes are not implemented. |
| New permanent coordinator daemon | Not justified by this phase; adds trust/lifetime/IPC surface and still does not create missing compositor/UI guarantees. Do not activate one. |

## Independent adversarial review and stop condition

Fresh-context reviewer executed the original 19 tests: 19 passed in 0.07s. It reported no internal model logic error **under the trusted-input/serialized assumptions**, but explicitly **production_ready=false**. Independent review did not certify a native protocol. Its concerns are preserved in [review summary](independent-review.json).

Concrete boundaries:

- **Start/activation TOCTOU:** ACK → start() returns true → DMS restart → caller still uses returned permission. There is no modeled activation operation to revoke/enforce that permission. Replacement production UI has no demonstrated persistent deny latch. Real preactivation lockdown is not guaranteed.
- **Cross-process epoch reuse:** constructing a new model with the same session resets counters. Old and new tokens/acks can be equal. Non-reused external incarnation and recovery authority are required, not proven.
- **Observer loss during lock:** reconnect retains pending old physical owner, rejects old events and refuses an idle reset. Safe denial, unresolved same-session liveness even if genuine unlock later happens.
- **Out-of-band lock:** notification arrives after password interface activation; denial at receipt cannot establish before-activation closure. All initiators must be mediated or compositor/UI coupling improved.
- **Native provenance:** XML has no token; Python event arguments cannot establish who generated them. Existing native fd inheritance, actual focus release and real PAM remain untested.

The parent executed three extra boundary probes demonstrating start-permission retention, epoch reuse and post-notification-only detection. These successful tests deliberately expose limitations; they are **not fixes** or a second independent review. Core `protocol.py` was unchanged after independent review.

## Validation and production recommendation

RED: two intended security assertions failed against an intentionally unsafe negative-control alias, with one negative-control test passing. This reproduces a model of the rejected design, not a new native exploit. First GREEN: 3 passed after the conditional gate model. Original expanded suite/reviewer: 19 passed. Final suite: **22 passed** including limitation probes; **6561** length-four schedules in one test. Related existing auth/Command Center/start/payload fixtures: **39 passed**. Runnable demo emits a labeled MODEL TRACE. Exact sanitized output is in [results](results.json).

Schedule exploration is bounded and checks model invariants, not all native interleavings. New scenario tests mostly validate the conditional model after its first tracer-bullet implementation; no separate RED is claimed for all 22 cases. No QEMU, native lock/PAM/IPC, ISO, hardware, dependencies or deployment ran.

**Recommendation: NO-GO for production implementation/integration from this prototype.** First resolve a supported origin-binding/causal-reconciliation mechanism and enforce UI denial through actual password activation/restart, including external initiators. Then design explicit pending-lock recovery and non-reused incarnations; require another bounded independent review before native implementation. A native experiment would need separate authorization. Preserve #49's blocker; do not auto-start Phase 2.

## Sources

[1] https://github.com/tomli0/wilsof-os/blob/b75b8f8544e48578ac9c299307fe833c48f1ab19/docs/development-reports/2026-11-02-consolidated-engineering-review-5.md — Consolidated Review 5
[2] https://github.com/tomli0/wilsof-os/blob/a28d4678bbbaa091337fdab2b331a1b9e56b7e4d/docs/development-reports/2026-11-02-auth-session-remediation-2.md — AS-02 blocker, section 8
[3] https://github.com/tomli0/wilsof-os/blob/a28d4678bbbaa091337fdab2b331a1b9e56b7e4d/bin/wilsof-lock-session — AS-03 and current lock lifecycle
[4] https://github.com/tomli0/wilsof-os/blob/a28d4678bbbaa091337fdab2b331a1b9e56b7e4d/config/dms/plugins/wilsofCommandCenter/CommandCenter.qml — Command Center access paths
[5] https://github.com/hyprwm/hyprland-protocols/blob/cd1aba6bd78775825eb230b3a4274c48b6705eb7/protocols/hyprland-lock-notify-v1.xml — Lock-notify wire contract
[6] https://github.com/hyprwm/hypridle/blob/e5c01af0842bd66617f7004568df9406111d6e80/src/core/Hypridle.cpp — Hypridle v0.1.8
[7] https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/quickshell/Services/SessionService.qml — Dux v2 SessionService
[8] https://github.com/duxlabs-dev/dux-shell/blob/9b413296b16721f7679fb62e624cb1ed2433fa58/core/internal/server/loginctl/monitor.go — Dux logind signal handling
[9] https://github.com/hyprwm/Hyprland/blob/d55a55d72a2ecfbb31b875b0b45c27559ce86691/src/protocols/SessionLock.cpp — Hyprland lock and force-unlock notifications
[10] https://github.com/hyprwm/hyprlock/blob/74efcdc96ee6d08480815064dab5112e0101eb1a/src/core/hyprlock.cpp — Hyprlock lifecycle, grace and SIGUSR1
[11] https://github.com/tomli0/wilsof-os/tree/b75b8f8544e48578ac9c299307fe833c48f1ab19 — Inspected Wilsof tree and startup policy
