# PR #21 installer-schema review checkpoint

Updated: 2026-10-26 UTC. Issue: #11. PR: #21.
Branch: `issue-11-installer-architecture` (existing PR worktree).
Starting PR head: `f89ce6a82a5ddb5ccc4abf4f1e9c703f2e4ec0e9`.
PR base branch: `main` (no rebase or integration performed).
Tested implementation commit: `ee52e3174eda97ac38ebb757bb471416b7b173e3`.
Deployed revision: none.

## Findings addressed

- Review `discussion_r4299712964` (P1): constrain partitions to exactly the
  symbolic roles `["ESP", "root"]` in order, rejecting null/object entries,
  unknown roles, missing entries and additional partitions.
- Review `discussion_r4299712971` (P1): require boolean `encryption.enabled`
  and reject every other property, including passwords, passphrases,
  nested credentials and key-file paths, even when encryption is disabled.
- Add real Draft 2020-12 validation of the documented example and negative
  cases; install `jsonschema` through the shared development requirements
  in CI. Explain the limits of schema validation versus future runtime checks.

## Executed verification

An isolated local Python 3.14 environment used pytest 9.1.1 and jsonschema 4.26.0.

- RED: partition regressions reproduced as 8 failures before the layout fix.
- GREEN: 11 partition/example cases passed after the layout fix.
- RED: encryption regressions reproduced as 11 failures before that fix.
- GREEN: `python -m pytest -q tests/test_installation_plan_validation.py`:
  24 passed.
- `python -m pip install -r requirements-dev.txt`: succeeded.
- `python -m pytest -q` on the implementation commit: 71 passed.
- JSON parsing: all repository JSON files passed.
- Dialect-correct `sh -n` / `bash -n`: 13 tracked shell entrypoints passed.
- `git diff --check`: passed.
- Added-line static security scan: no matches for secret assignments,
  shell injection, eval/exec or unsafe pickle deserialization.
- Independent subscription-backed read-only focused review: PASS; no security
  concerns or logic errors. Optional additional container-type tests suggested.
  The reviewer inspected tests but did not execute them.

GitHub Actions results and final pushed head must be checked separately in the PR;
this checkpoint does not claim CI ran on an unpublished revision.

## Coordination and limits

The existing hourly job and worker pause control were left paused. The existing
worker lock was held during this manual task. The installed worker script,
OpenRouter budget gate, approval rules, spending limits and retry limits were
not changed. No OpenRouter or Terra reviewer was invoked.

No ISO build, VM/Proxmox change, disk probe/write, installation, deployment,
merge, release, issue closure or feature-Done transition was performed.
Schema validation does not implement an executor, encryption or disk revalidation.
Disposable UEFI VM and physical Intel/AMD/MacBook hardware acceptance remain
unperformed and require separate authorization.

## Handoff

Ready for PR review, not merged or Done. Next bounded review task: address PR #19's
reviewed-commit preflight and surviving-output validation findings before any
separately authorized ISO build. Do not run an ISO build to fix those docs.
