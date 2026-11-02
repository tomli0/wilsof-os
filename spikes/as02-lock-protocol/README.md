# AS-02 Phase 1 — isolated deterministic spike

**PARTIAL / PRODUCTION BLOCKED.** Nothing here is installed, imported by runtime,
or included in the explicit ISO payload manifest. No real lock/session/IPC/PAM
operation is implemented. This is a contract model plus known counterexamples.

Run from the repository root with already available Python/pytest:

    PYTHONDONTWRITEBYTECODE=1 python spikes/as02-lock-protocol/demo.py
    PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider spikes/as02-lock-protocol/test_protocol.py

- ADR.md: decision, source trace, trust assumptions and native blockers.
- transition-diagram.md: plain-text transition diagram with unsupported edges.
- protocol.py: conditional in-memory specification, not a transport adapter.
- legacy_boolean.py: intentionally unsafe negative control, never deploy.
- test_protocol.py: ten requested scenarios, bounded schedules and boundary probes.
- results.json: sanitized executed RED/GREEN/final/related results and model demo.
- independent-review.json: parent-sanitized independent review summary, not raw transcript.

Final executed result: 22 prototype tests passed; 39 related fixture tests passed.
One test explores 6561 schedules of length four. Three passing limitation probes
explicitly demonstrate retained launch permission after UI restart, cross-process
epoch reuse and late detection of an external lock. Passing means the limitation
was reproduced, not that it was corrected. No full-suite/native success claim.

## Verdict: PARTIAL

What worked: under trusted origin-bound event/ACK/fence inputs, delayed release A
cannot open a new intent B; launch permission is denied without current ACK;
wrong password and process exit do not unlock; normal modeled release recovers.

What did not: existing boolean/lock-notify paths do not provide those input
contracts, preactivation closure is unproved, counter identities reset across
process recreation, and pending-lock observer loss has no recovery transition.

Recommendation: keep #49 blocked and stop. Resolve native provenance, enforceable
activation gating and recovery architecture before a separately authorized Phase 2.
